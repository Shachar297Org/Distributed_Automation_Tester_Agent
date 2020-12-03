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
                Utils.RunCommand("curl", testCenterUrl + $"/connect?port={Settings.Get("AGENT_PORT")}", "", cwd, null);
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
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "create_device_folders.py", $"{Settings.Get("DEVICES_TO_CREATE_PATH")} {int.Parse(Settings.Get("MAX_DEVICES_TO_CREATE"))}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                string cwd = Directory.GetCurrentDirectory();
                Utils.RunCommand("curl", Settings.Get("TEST_CENTER_URL") + $"/agentReady?port={Settings.Get("AGENT_PORT")}", "", cwd, null);
                return true;
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error in sendDevices: {ex.Message} {ex.StackTrace}", "error");
                return false;
            }
        }
    

        /// <summary>
        /// Get script from test center, run device servers and clients and finally send activation and compare events results
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
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "start_devices.py", $"{Settings.Get("DEVICES_TO_CREATE_PATH")} {Settings.Get("SCRIPT_PATH")} {maxDevicesToCreate} {Settings.Get("PROCESSES_PATH")}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
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
        /// Collect activate results from all devices
        /// </summary>
        private void CollectActivationResults()
        {
            Utils.LoadConfig();
            _logger = new Logger(Settings.Get("LOG_FILE_PATH"));
            try
            {
                string devicesJsonFile = Settings.Get("DEVICES_TO_CREATE_PATH");
                string deviceFoldersDir = Settings.Get("DEVICE_FOLDERS_DIR");
                string activationResultsFile = Settings.Get("ACTIVATION_RESULTS_PATH");
                int returnCode = Utils.RunCommand(Settings.Get("PYTHON"), "collect_activation_results.py", $"{devicesJsonFile} {deviceFoldersDir} {activationResultsFile}", Settings.Get("PYTHON_SCRIPTS_PATH"), Settings.Get("OUTPUT"));
                // read activate_results.json to json object and send to test center
            }
            catch (Exception ex)
            {
                _logger.WriteLog($"Error in collectActivationResults: {ex.Message} {ex.StackTrace}", "error");
            }
        }

        /// <summary>
        /// Stop all device clients and servers processes and compare events
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
            // todo: Collect client logs and create activation_results json object in the format: <ga>,<sn>,<activation_status>
            // todo: Send to test center POST request getScriptResults with activation_results json
            // todo: Initiate compare events
            // todo: Collect compare results and create compare_events_results json object in the format: <ga>,<sn>,<event_key>,<event_value>,<creation_time>
            // todo: Send to test center POST request GetComparisonResults with compare_events_results json
        }
    }
}
