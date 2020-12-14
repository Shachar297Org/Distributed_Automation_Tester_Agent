using Console.Models;
using Console.Utilities;
using Main;
using Newtonsoft.Json;
using Shared;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;

namespace Console
{
    public class BackEnd : IBackendInterface
    {
        System.Timers.Timer _getProcessTimer = new System.Timers.Timer(new TimeSpan(0, 1, 0).TotalMilliseconds);
        // Every minute the agent checks if a device client process finished running
        Logger _logger;

        /// <summary>
        /// Create agent base directory and send connect command to test center
        /// </summary>
        public bool Init()
        {
            Utils.LoadConfig();
            _logger = new Logger(Settings.Get("LOG_FILE_PATH"));
            try
            {
                string internalIP = Utils.GetInternalIPAddress();
                _logger.WriteLog($"Agent internal IP: {internalIP}", "info");
                string agentUrl = internalIP + ":" + Settings.Get("AGENT_PORT");
                Settings.Set("AGENT_URL", agentUrl);
                _logger.WriteLog($"Create agent folder for {agentUrl}", "info");
                Directory.CreateDirectory(Settings.Get("AGENT_DIR_PATH"));
                string cwd = Directory.GetCurrentDirectory();
                string testCenterUrl = Settings.Get("TEST_CENTER_URL");
                _logger.WriteLog($"Send connect to test center in {testCenterUrl}", "info");
                Utils.RunCommand("curl", testCenterUrl + $"/connect?port={Settings.Get("AGENT_PORT")}", "", cwd, Settings.Get("OUTPUT"));
                return true;
            }
            catch (Exception ex) {
                _logger.WriteLog($"Error in init: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }

        /// <summary>
        /// Get device list from test center, create device folders and when finished send agentReady
        /// </summary>
        /// <param name="jsonContent">json containing device list</param>
        public bool SendDevices(string jsonContent)
        {
            Utils.LoadConfig();
            _logger = new Logger(Settings.Get("LOG_FILE_PATH"));

            _logger.WriteLog("Received device list", "info");
            try {
                _logger.WriteLog($"Json content: {jsonContent}", "info");
                List<Device> devicesToCreate = JsonConvert.DeserializeObject<List<Device>>(jsonContent);
                Utils.WriteDeviceListToFile(devicesToCreate, Settings.Get("DEVICES_TO_CREATE_PATH"));
                _logger.WriteLog("Start creating device folders", "info");
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "create_device_folders.py", $"{Settings.Get("CONFIG_FILE")}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                string cwd = Directory.GetCurrentDirectory();
                _logger.WriteLog($"Send agentReady to test center in {Settings.Get("TEST_CENTER_URL")}", "info");
                Utils.RunCommand("curl", Settings.Get("TEST_CENTER_URL") + $"/agentReady?port={Settings.Get("AGENT_PORT")}", "", cwd, Settings.Get("OUTPUT"));
                return true;
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error in sendDevices: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }
    

        /// <summary>
        /// Get script from test center, run device servers and clients and finally send comparison events results
        /// </summary>
        /// <param name="jsonContent">json containing script file</param>
        public bool SendScript(string jsonContent)
        {
            Utils.LoadConfig();
            _logger = new Logger(Settings.Get("LOG_FILE_PATH"));
            try
            {
                ScriptFile scriptFileObj = JsonConvert.DeserializeObject<ScriptFile>(jsonContent);
                Utils.WriteToFile(Settings.Get("SCRIPT_PATH"), scriptFileObj.Content, false);
                int maxDevicesToCreate = int.Parse(Settings.Get("MAX_DEVICES_TO_CREATE"));
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "start_devices.py", $"{Settings.Get("CONFIG_FILE")}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                Thread.Sleep(int.Parse(Settings.Get("PROCESS_UPTIME_IN_MS")));
                _getProcessTimer.Elapsed += GetProcessTimer_Elapsed;
                _getProcessTimer.Start();
                return true;
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error in sendScript: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }  

        /// <summary>
        /// Return server LumenisX process object related to the device ga, sn>
        /// </summary>
        /// <param name="processList">process list</param>
        /// <param name="ga">Device GA</param>
        /// <param name="sn">Device SN</param>
        /// <returns></returns>
        private LumXProcess GetServerByDevice(List<LumXProcess> processList, string ga, string sn)
        {
            foreach (var processObj in processList)
            {
                if (processObj.Type == "Server" && processObj.DeviceType == ga && processObj.DeviceSerialNumber == sn)
                {
                    return processObj;
                }
            }
            return null;
        }

        /// <summary>
        /// Check if device client process finished, then terminate the server process and send log to test center
        /// Return true if there are still device processes running
        /// </summary>
        /// <returns></returns>
        private bool CheckDeviceClientFinished()
        {
            try
            {
                List<LumXProcess> processList = Utils.ReadProcessesFromFile(Settings.Get("PROCESSES_PATH"));
                List<LumXProcess> processesToRemove = new List<LumXProcess>();
                foreach (var processObj in processList)
                {
                    if (processObj.Type == "Client")
                    {
                        // If client process is NOT running
                        if (!Utils.IsProcessRunning(processObj.Pid))
                        {
                            // Stop the relevant server
                            _logger.WriteLog($"Client process with PID {processObj.Pid} was terminated.", "info");
                            string ga = processObj.DeviceType;
                            string sn = processObj.DeviceSerialNumber;
                            LumXProcess serverObj = GetServerByDevice(processList, ga, sn);
                            if (serverObj == null)
                            {
                                _logger.WriteLog($"No relevant server process found for device {processObj.DeviceSerialNumber}.", "error");
                            }
                            Utils.KillProcessAndChildren(serverObj.Pid);
                            _logger.WriteLog($"Server process with PID {serverObj.Pid} was terminated.", "info");

                            // Remove server and client processes from list
                            processesToRemove.Add(processObj);
                            processesToRemove.Add(serverObj);

                            // Send script results to test center
                            SendScriptResults(sn, ga);
                        }
                    }
                }

                // Remove finished processes from list
                foreach (var processToRemove in processesToRemove)
                {
                    processList.Remove(processToRemove);
                }

                // Update processes file
                string processesJsonFile = Settings.Get("PROCESSES_PATH");
                string processesContent = JsonConvert.SerializeObject(processList);
                Utils.WriteToFile(processesJsonFile, processesContent, append: false);

                return processList.Count > 0;
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error: {ex.Message} {ex.StackTrace}", "error");
                return true;
            }
        }

        private void SendScriptResults(string sn, string ga)
        {
            Utils.LoadConfig();
            string deviceName = string.Join("_", new string[] { sn, ga });
            string deviceFoldersDir = Settings.Get("DEVICE_FOLDERS_DIR");
            string deviceClientLogFolder = Path.Combine(deviceFoldersDir, deviceName, "Client", "Debug_x64", "Logs");
            string logFile = Path.Combine(deviceClientLogFolder, "log.txt");
            _logger.WriteLog($"Client log file path: {logFile}", "info");
            string logContent = Utils.ReadFileContent(logFile);
            if (logContent.Contains("fail"))
            {
                _logger.WriteLog($"Script failed.", "info");
                SendClientLog(logFile, deviceName);
                _logger.WriteLog($"Log file was sent to test center.", "info");
            }
            else
            {
                _logger.WriteLog($"Script ran successfully.", "info");
            }
            _logger.WriteLog($"Compare events.", "info");
            int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "compare_events.py", $"{Settings.Get("CONFIG_FILE")} {sn} {ga}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
            _logger.WriteLog($"Comparison results were sent to test center.", "info");       
        }

        /// <summary>
        /// Send client log content to test center
        /// </summary>
        /// <param name="logFile">log file path</param>
        /// <param name="deviceName">Device name: sn_ga</param>
        private void SendClientLog(string logFile, string deviceName)
        {
            string configFile = Settings.Get("CONFIG_FILE");
            _logger.WriteLog($"Script failed.", "info");
            int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "send_client_log.py", $"{configFile} {deviceName} {logFile}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
            _logger.WriteLog($"Log file was send to test center.", "info");
        }

        /// <summary>
        /// Stop all device clients and servers processes and compare events
        /// </summary>
        /// <param name="sender">sender</param>
        /// <param name="e">event</param>
        private void GetProcessTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            _getProcessTimer.Stop();
            _logger.WriteLog($"---Process timer stopped---", "info");
            _logger.WriteLog($"Check device client finished.", "info");
            // If there are still running devices
            if (CheckDeviceClientFinished())
            {
                _logger.WriteLog($"There are still running devices.", "info");
                _getProcessTimer.Start();
                _logger.WriteLog($"---Process timer started---", "info");
            }
            else
            {         
                _logger.WriteLog($"There are no more running devices.", "info");
            }
        }
    }
}
