using Console.Models;
using Main;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;

using System.IO;
using System.Linq;
using System.Management;
using System.Text;
using System.Threading.Tasks;
using System.Configuration;
using System.Collections.Specialized;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Diagnostics;

namespace Console.Utilities
{
    public class Utils
    {
        private static ReaderWriterLockSlim _readWriteLock = new ReaderWriterLockSlim();

        private static Settings _settings;

        public Utils(Settings settings)
        {
            _settings = settings;
        }

        public int RunCommand(string exeFile, string cmd, string args, string cwd, string outputFile, bool useShell = false)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = exeFile;
            start.Arguments = string.Format("{0} {1}", cmd, args);
            start.WorkingDirectory = cwd;
            start.UseShellExecute = useShell;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;

            int exit = 0;

            using (var process = new Process
            {
                StartInfo = start
            })
            {
                process.Start();
                var result = Task.Run(() => process.StandardOutput.ReadToEnd());
                var error = Task.Run(() => process.StandardError.ReadToEnd());

                process.WaitForExit();

                WriteToFile(outputFile, result.Result, append: true);
                WriteToFile(outputFile, error.Result, append: true);

                exit = process.ExitCode;

            }

            return exit;
        }

        /// <summary>
        /// Run Windows command in background asynchronically
        /// </summary>
        /// <param name="exeFile">Executable file</param>
        /// <param name="cmd">command</param>
        /// <param name="args">arguments</param>
        /// <param name="outputFile">Output file path</param>
        /// <returns>Command return code</returns>
        public async Task RunCommandAsync(string exeFile, string cmd, string args, string cwd, string outputFile)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = exeFile;
            start.Arguments = string.Format("{0} {1}", cmd, args);
            start.WorkingDirectory = cwd;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;

            var result = await ProcessAsyncHelper.RunAsync(start);

            WriteToFile(outputFile, result.StdOut, append: true);
            WriteToFile(outputFile, result.StdErr, append: true);
           
        }

        public async Task KillWithADelay(int pid, int delay)
        {
            await Task.Delay(delay);
            KillProcessAndChildren(pid);
            WriteLog($"Server process with PID {pid} was terminated.", "info");
        }

        /// <summary>
        /// Terminates process and all its children by pid
        /// </summary>
        /// <param name="pid"></param>
        public void KillProcessAndChildren(int pid)
        {
            // Cannot close 'system idle process'
            if (pid == 0)
            {
                return;
            }

            try
            {
                Process proc = Process.GetProcessById(pid);
                proc.Kill(true);
            }
            catch (ArgumentException)
            {
                // Process already exited.
            }
        }

        /// <summary>
        /// Read device list from json file
        /// </summary>
        /// <param name="jsonFile">json file</param>
        /// <returns>list of device objects</returns>
        public List<Device> ReadDevicesFromFile(string jsonFile)
        {
            List<Device> deviceList = null;
            try
            {
                using (StreamReader reader = new StreamReader(jsonFile))
                {
                    string json = reader.ReadToEnd();
                    deviceList = JsonConvert.DeserializeObject<List<Device>>(json);
                }
            }
            catch (Exception)
            {
                deviceList = null;
            }
            if (deviceList == null)
            {
                deviceList = new List<Device>();
            }
            return deviceList;
        }

        /// <summary>
        /// Read process list from json file
        /// </summary>
        /// <param name="jsonFile">json file</param>
        /// <returns>list of process objects</returns>
        public List<LumXProcess> ReadProcessesFromFile(string jsonFile)
        {
            List<LumXProcess> processList = null;
            try
            {
                using (StreamReader reader = new StreamReader(jsonFile))
                {
                    string json = reader.ReadToEnd();
                    processList = JsonConvert.DeserializeObject<List<LumXProcess>>(json);
                }
            }
            catch (Exception ex)
            {
                processList = null;
            }
            if (processList == null)
            {
                processList = new List<LumXProcess>();
            }
            return processList;
        }

        /// <summary>
        /// Write device list to json file
        /// </summary>
        /// <param name="list">device list</param>
        /// <param name="jsonFile">json file</param>
        public void WriteDeviceListToFile(List<Device> list, string jsonFile)
        {
            string jsonObj = JsonConvert.SerializeObject(list);
            using (StreamWriter writer = new StreamWriter(jsonFile))
            {
                writer.Write(jsonObj);
            }
        }

        /// <summary>
        /// Read file content
        /// </summary>
        /// <param name="filePath">file path</param>
        /// <returns>file content</returns>
        public string ReadFileContent(string filePath)
        {
            string content = "";
            using (StreamReader reader = new StreamReader(filePath))
            {
                content = reader.ReadToEnd();
            }
            return content;
        }


        /// <summary>
        /// Write content to file
        /// </summary>
        /// <param name="filePath">file path</param>
        /// <param name="content">content</param>
        /// <param name="append">append to file or not</param>
        public void WriteToFile(string filePath, string content, bool append)
        {
            _readWriteLock.EnterWriteLock();
            try
            {
                using (StreamWriter writer = new StreamWriter(filePath, append))
                {
                    writer.WriteLine(content);
                }
            }
            finally
            {
                _readWriteLock.ExitWriteLock();
            }

        }
       
        /// <summary>
        /// Get internal IP address of the host
        /// </summary>
        /// <returns></returns>
        public string GetInternalIPAddress()
        {
            var host = Dns.GetHostEntry(Dns.GetHostName());
            foreach (var ip in host.AddressList)
            {
                if (ip.AddressFamily == AddressFamily.InterNetwork)
                {
                    return ip.ToString();
                }
            }
            throw new Exception("No internal IP address was found in this system");
        }

        /// <summary>
        /// Check if process is running
        /// </summary>
        /// <param name="pid">Process ID</param>
        /// <returns>True or false</returns>
        public bool IsProcessRunning(int pid)
        {
            return Process.GetProcesses().Any(p => p.Id == pid);
        }

        public void WriteLog(string msg, string level)
        {
            _readWriteLock.EnterWriteLock();
            try
            {
                using (StreamWriter writer = new StreamWriter(_settings["LOG_FILE_PATH"], append: true))
                {
                    string nowTime = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
                    writer.WriteLine($"{nowTime} [{level.ToUpper()}] : {msg}");
                }
            }
            finally
            {
                _readWriteLock.ExitWriteLock();
            }
            
        }

    }
}
