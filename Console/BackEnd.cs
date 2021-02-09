using Console.Models;
using Console.Utilities;
using Main;
using Newtonsoft.Json;
using Console.Interfaces;
using System;
using System.Collections.Generic;
using System.Diagnostics;
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
        // Every minute the agent checks if a device client process finished running
        private static System.Timers.Timer _getProcessTimer = new System.Timers.Timer(new TimeSpan(0, 5, 0).TotalMilliseconds);

        private static int _stoppingDelay = 0;
        private static int _keepAliveCount = 0;

        /// <summary>
        /// Create agent base directory and send connect command to test center
        /// </summary>
        public async Task<bool> Init()
        {
            _getProcessTimer.AutoReset = false;

            Utils.LoadConfig();
            try
            {
                Utils.WriteLog($"-----AGENT INIT BEGIN----", "info");
                string internalIP = Utils.GetInternalIPAddress();
                Utils.WriteLog($"Agent internal IP: {internalIP}", "info");
                string agentUrl = internalIP + ":" + Settings.Get("AGENT_PORT");
                Settings.Set("AGENT_URL", agentUrl);
                Utils.WriteLog($"Create agent folder for {agentUrl}", "info");
                Directory.CreateDirectory(Settings.Get("AGENT_DIR_PATH"));
                string cwd = Directory.GetCurrentDirectory();
                string testCenterUrl = Settings.Get("TEST_CENTER_URL");
                Utils.WriteLog($"Send connect to test center in {testCenterUrl}", "info");
                await Utils.RunCommandAsync("curl", testCenterUrl + $"/connect?port={Settings.Get("AGENT_PORT")}", "", cwd, Settings.Get("OUTPUT"));
                return true;
            }
            catch (Exception ex)
            {
                Utils.WriteLog($"Error in init: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
            finally
            {
                Utils.WriteLog($"-----AGENT INIT END----", "info");
            }
        }

        /// <summary>
        /// Get device list from test center, create device folders and when finished send agentReady
        /// </summary>
        /// <param name="jsonContent">json containing device list</param>
        public async Task SendDevices(string jsonContent)
        {
            var sw = new Stopwatch();

            List<Task> createFolderTasks = new List<Task>();

            Utils.LoadConfig();

            Utils.WriteLog("-----AGENT DEVICE FOLDER CREATION STAGE BEGIN-----", "info");
            Utils.WriteLog("Received device list", "info");
            try
            {
                Utils.WriteLog($"Json content: {jsonContent}", "info");
                List<Device> devicesToCreate = JsonConvert.DeserializeObject<List<Device>>(jsonContent);
                Utils.WriteDeviceListToFile(devicesToCreate, Settings.Get("DEVICES_TO_CREATE_PATH"));
                Utils.WriteLog("Start creating device folders", "info");

                sw.Start();
                if (devicesToCreate.Count > 0)
                {
                    foreach (Device device in devicesToCreate)
                    {
                        string deviceName = device.DeviceSerialNumber + "_" + device.DeviceType;
                        //Task t = Task.Run(() =>
                        //{
                        Utils.RunCommand(Settings.Get("PYTHON"), "create_device_folder.py",
                            $"{Settings.Get("CONFIG_FILE")} {deviceName}",
                            Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                        //});
                        //createFolderTasks.Add(t);                      
                    }
                }

                //Task.WaitAll(createFolderTasks.ToArray());
                sw.Stop();

                Utils.WriteLog($"Creating folders finished in {sw.ElapsedMilliseconds / 1000} seconds", "info");

                string cwd = Directory.GetCurrentDirectory();
                Utils.WriteLog($"Send agentReady to test center in {Settings.Get("TEST_CENTER_URL")}", "info");
                await Utils.RunCommandAsync("curl", Settings.Get("TEST_CENTER_URL") + $"/agentReady?port={Settings.Get("AGENT_PORT")}", "", cwd, Settings.Get("OUTPUT"));
            }
            catch (AggregateException ex)
            {
                foreach (var inner in ex.InnerExceptions)
                {
                    Utils.WriteLog($"Inner exception: {inner.Message} {inner.StackTrace}", "error");
                }

            }
            catch (Exception ex)
            {
                Utils.WriteLog($"Error in sendDevices: {ex.Message} {ex.StackTrace}", "error");
            }
            finally
            {
                Utils.WriteLog("-----AGENT DEVICE FOLDER CREATION STAGE END-----", "info");
            }

        }

        private void ReadDeviceProcesses()
        {
            string processesDirPath = Settings.Get("PROCESSES_DIR_PATH");
            Utils.WriteLog($"Read process objects from {processesDirPath}", "info");
            string[] deviceProcessFiles = Directory.GetFiles(processesDirPath);
            List<LumXProcess> processList = new List<LumXProcess>();
            foreach (var deviceProcessFile in deviceProcessFiles)
            {
                List<LumXProcess> deviceProcessList = Utils.ReadProcessesFromFile(deviceProcessFile);
                processList.AddRange(deviceProcessList);
            }

            // Update processes file
            string processesJsonFile = Settings.Get("PROCESSES_PATH");
            string processesContent = JsonConvert.SerializeObject(processList);
            Utils.WriteToFile(processesJsonFile, processesContent, append: false);
        }


        /// <summary>
        /// Get script from test center, run device servers and clients and finally send comparison events results
        /// </summary>
        /// <param name="jsonContent">json containing script file</param>
        public async Task<bool> SendScript(ScriptData scriptFileObj)
        {
            _stoppingDelay = scriptFileObj.StoppingDelay;

            List<Task> startDevicesTasks = new List<Task>();
            var sw = new Stopwatch();

            Utils.LoadConfig();
            try
            {

                if (!string.IsNullOrEmpty(scriptFileObj.Content))
                {
                    Utils.WriteToFile(Settings.Get("SCRIPT_PATH"), scriptFileObj.Content, false);
                }

                Utils.WriteLog($"-----AGENT RUNINNG DEVICES STAGE BEGIN-----", "info");
                List<Device> devicesToCreate = Utils.ReadDevicesFromFile(Settings.Get("DEVICES_TO_CREATE_PATH"));

                sw.Start();

                if (devicesToCreate.Count > 0)
                {
                    for (int deviceIndex = 0; deviceIndex < devicesToCreate.Count; deviceIndex++)
                    {
                        Device device = devicesToCreate[deviceIndex];
                        string deviceName = device.DeviceSerialNumber + "_" + device.DeviceType;
                        var index = deviceIndex;

                        // Task startDevice = Task.Run(() =>
                        //Utils.RunCommandAsync(Settings.Get("PYTHON"), "start_device.py",
                        //                $"{Settings.Get("CONFIG_FILE")} {deviceName} {index}",
                        //                Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"))
                        // );

                        // startDevicesTasks.Add(startDevice);

                        Utils.RunCommand(Settings.Get("PYTHON"), "start_device.py",
                                        $"{Settings.Get("CONFIG_FILE")} {deviceName} {index}",
                                        Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                    }

                }

                //Task.WaitAll(startDevicesTasks.ToArray());

                sw.Stop();

                Utils.WriteLog($"Starting devices finished in {sw.ElapsedMilliseconds / 1000} seconds", "info");
                ReadDeviceProcesses();

                _getProcessTimer.AutoReset = false;
                _getProcessTimer.Elapsed += GetProcessTimer_Elapsed;
                _getProcessTimer.Start();

            }
            catch (AggregateException ex)
            {
                foreach (var inner in ex.InnerExceptions)
                {
                    Utils.WriteLog($"Inner exception: {inner.Message} {inner.StackTrace}", "error");
                }

                return false;
            }
            catch (Exception ex)
            {
                Utils.WriteLog($"Error in sendScript: {ex.Message} {ex.StackTrace}", "error");

                return false;
            }
            finally
            {
                Utils.WriteLog($"-----AGENT RUNINNG DEVICES STAGE END-----", "info");
            }

            return true;
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
            var result = processList.Where(processObj => processObj.Type == "Server" && processObj.DeviceType == ga && processObj.DeviceSerialNumber == sn).FirstOrDefault();
            return result;
        }

        /// <summary>
        /// Terminate the server process and send log to test center
        /// </summary>
        /// <returns></returns>
        public void KillServersAndSendLog(List<LumXProcess> processList, List<LumXProcess> clientsNotRunning)
        {
            foreach (var clientObj in clientsNotRunning)
            {
                // Stop the relevant server
                Utils.WriteLog($"Client process with PID {clientObj.Pid} was terminated.", "info");
                var serverObj = GetServerByDevice(processList, clientObj.DeviceType, clientObj.DeviceSerialNumber);

                if (serverObj == null)
                {
                    Utils.WriteLog($"No relevant server process found for device {clientObj.DeviceSerialNumber}.", "error");
                }
                else
                {
                    Utils.KillProcessAndChildren(serverObj.Pid);
                    Utils.WriteLog($"Server process with PID {serverObj.Pid} was terminated.", "info");

                    // Send script results to test center
                    SendScriptResults(serverObj.DeviceSerialNumber, serverObj.DeviceType);

                }

            }

        }

        /// <summary>
        /// Send script results containing client log in case of failure and compare results
        /// </summary>
        /// <param name="sn">Devcie SN</param>
        /// <param name="ga">Device GA</param>
        private void SendScriptResults(string sn, string ga)
        {
            Utils.LoadConfig();
            string deviceName = string.Join("_", new string[] { sn, ga });
            string deviceFoldersDir = Settings.Get("DEVICE_FOLDERS_DIR");
            string clientFolderName = Settings.Get("CLIENT_EXE_NAME").Split('.')[0];
            string deviceClientLogFolder = Path.Combine(deviceFoldersDir, deviceName, clientFolderName, "Debug_x64", "Logs");
            string logFile = Path.Combine(deviceClientLogFolder, "log.txt");
            Utils.WriteLog($"Client log file path: {logFile}", "info");
            string logContent = Utils.ReadFileContent(logFile);
            if (logContent.Contains("fail"))
            {
                SendClientLog(logFile, deviceName);
            }
            else
            {
                Utils.WriteLog($"Script ran successfully.", "info");
            }

            Utils.WriteLog($"Send log events.", "info");
            int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "compare_events.py", $"{Settings.Get("CONFIG_FILE")} {sn} {ga}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));

            if (returnCode == 0)
            {
                Utils.WriteLog($"Comparison results were sent to test center.", "info");
            }
            else
            {
                Utils.WriteLog($"Comparison results sending to test center failed.", "info");
            }

        }

        /// <summary>
        /// Send client log content to test center
        /// </summary>
        /// <param name="logFile">log file path</param>
        /// <param name="deviceName">Device name: sn_ga</param>
        private void SendClientLog(string logFile, string deviceName)
        {
            string configFile = Settings.Get("CONFIG_FILE");
            Utils.WriteLog($"Script failed.", "info");
            int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "send_client_log.py", $"{configFile} {deviceName} {logFile}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));

            if (returnCode == 0)
            {
                Utils.WriteLog($"Log file was send to test center.", "info");
            }
            else
            {
                Utils.WriteLog($"Log file sending to test center failed.", "info");
            }
        }

        private bool IsQueueEmpty(LumXProcess process)
        {
            var file = Settings.Get("EMPTY_QUEUE_FILE");
            var devices_folder = Settings.Get("DEVICE_FOLDERS_DIR");
            var server_folder = process.DeviceSerialNumber.ToUpper() + "_" + process.DeviceType.ToUpper() + "\\Server\\Debug";

            var empty_queue_filepath = Path.Combine(devices_folder, server_folder, file);

            return File.Exists(empty_queue_filepath);
        }

        /// <summary>
        /// Stop all device clients and servers processes and compare events
        /// </summary>
        /// <param name="sender">sender</param>
        /// <param name="e">event</param>
        private void GetProcessTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            try
            {
                if (_keepAliveCount <= _stoppingDelay)
                {
                    if (_keepAliveCount == 0)
                    {
                        _getProcessTimer.Interval = new TimeSpan(0, 1, 0).TotalMilliseconds;
                    }
                    _keepAliveCount++;
                    _getProcessTimer.Start();
                }
                else
                {
                    Utils.WriteLog($"---Process timer stopped---", "info");
                    Utils.WriteLog($"Check device client finished.", "info");
                    // If there are still running devices
                    List<LumXProcess> processList = Utils.ReadProcessesFromFile(Settings.Get("PROCESSES_PATH"));
                    var running = processList.Where(p => Utils.IsProcessRunning(p.Pid)).ToList();

                    var notRunning = processList.Where(p => !running.Contains(p) && IsQueueEmpty(p)).ToList();
                    var clientsNotRunning = notRunning.Where(p => p.Type == "Client").ToList();

                    if (clientsNotRunning.Count > 0)
                    {
                        KillServersAndSendLog(processList, clientsNotRunning);

                        // Update processes file
                        string processesJsonFile = Settings.Get("PROCESSES_PATH");
                        string processesContent = JsonConvert.SerializeObject(running);
                        Utils.WriteToFile(processesJsonFile, processesContent, append: false);
                    }

                    if (running.Count > 0)
                    {
                        Utils.WriteLog($"There are still running devices.", "info");

                        _keepAliveCount = 0;
                        _getProcessTimer.Start();
                        Utils.WriteLog($"---Process timer started---", "info");
                    }
                    else
                    {
                        Utils.WriteLog($"There are no more running devices.", "info");
                    }
                }

            }
            catch (Exception ex)
            {
                Utils.WriteLog($"Error: {ex.Message} {ex.StackTrace}", "error");
            }

        }
    }
}
