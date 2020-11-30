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
        Logger _logger;

        /// <summary>
        /// Create agent base directory and send connect command to test center
        /// </summary>
        public bool Init()
        {
            try
            {
                Utils.LoadConfig();
                _logger = new Logger(Settings.Get("LOG_FILE_PATH"));

                string internalIP = Utils.GetInternalIPAddress();
                _logger.WriteLog($"Agent internal IP: {internalIP}", "info");
                string agentUrl = internalIP + ":" + Settings.Get("AGENT_PORT");
                Settings.Set("AGENT_URL", agentUrl);
                _logger.WriteLog($"Create agent folder for {agentUrl}", "info");
                Directory.CreateDirectory(Settings.Get("AGENT_DIR_PATH"));
                string cwd = Directory.GetCurrentDirectory();
                string testCenterUrl = Settings.Get("TEST_CENTER_URL");
                _logger.WriteLog($"Send connect to test center in {testCenterUrl}", "info");
                Utils.RunCommand("curl", testCenterUrl + $"/connect?port={Settings.Get("AGENT_PORT")}", "", cwd, null);
                return true;
            }
            catch (Exception ex) {
                _logger.WriteLog($"Error: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }

        /// <summary>
        /// Get device list from test center, create device folders and when finished send agentReady
        /// </summary>
        /// <param name="jsonContent">json containing device list</param>
        public bool SendDevices(string jsonContent)
        {
            try {
                Utils.LoadConfig();
                _logger = new Logger(Settings.Get("LOG_FILE_PATH"));

                _logger.WriteLog("Received device list", "info");
                List<Device> devicesToCreate = JsonConvert.DeserializeObject<List<Device>>(jsonContent);
                Utils.WriteDeviceListToFile(devicesToCreate, Settings.Get("DEVICES_TO_CREATE_PATH"));
                _logger.WriteLog("Start creating device folders", "info");
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "create_device_folders.py", $"{Settings.Get("DEVICES_TO_CREATE_PATH")} {int.Parse(Settings.Get("MAX_DEVICES_TO_CREATE"))}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                string cwd = Directory.GetCurrentDirectory();
                Utils.RunCommand("curl", Settings.Get("TEST_CENTER_URL") + $"/agentReady?port={Settings.Get("AGENT_PORT")}", "", cwd, null);
                return true;
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }
    

        /// <summary>
        /// Get script from test center, run device servers and clients and finally send activation results
        /// </summary>
        /// <param name="jsonContent">json containing script file</param>
        public bool SendScript(string jsonContent)
        {
            try
            {
                Utils.LoadConfig();
                _logger = new Logger(Settings.Get("LOG_FILE_PATH"));
                ScriptFile scriptFileObj = JsonConvert.DeserializeObject<ScriptFile>(jsonContent);
                Utils.WriteToFile(Settings.Get("SCRIPT_PATH"), scriptFileObj.Content, false);
                int maxDevicesToCreate = int.Parse(Settings.Get("MAX_DEVICES_TO_CREATE"));
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "start_devices.py", $"{Settings.Get("DEVICES_TO_CREATE_PATH")} {Settings.Get("SCRIPT_PATH")} {maxDevicesToCreate} {Settings.Get("PROCESSES_PATH")}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                Thread.Sleep(int.Parse(Settings.Get("PROCESS_UPTIME_IN_MS")));
                _getProcessTimer.Elapsed += GetProcessTimer_Elapsed;
                _getProcessTimer.Start();
            return true;
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }

        /// <summary>
        /// Stop all device clients and servers processes
        /// </summary>
        /// <param name="sender">sender</param>
        /// <param name="e">event</param>
        private void GetProcessTimer_Elapsed(object sender, ElapsedEventArgs e)
        {
            List<LumXProcess> processList = Utils.ReadProcessesFromFile(Settings.Get("PROCESSES_PATH"));
            foreach (var processObj in processList)
            {
                Utils.KillProcessAndChildren(processObj.Pid);
            }
            // todo: collect client logs and send test center activation script results via POST request
        }
    }
}
