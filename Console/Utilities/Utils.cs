using Console.Models;
using Main;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Management;
using System.Text;
using System.Threading.Tasks;
using System.Configuration;
using System.Collections.Specialized;
using System.Net;
using System.Net.Sockets;

namespace Console.Utilities
{
    public static class Utils
    {
        /// <summary>
        /// Run Windows command in background and wait until it finishes
        /// </summary>
        /// <param name="exeFile">Executable file</param>
        /// <param name="cmd">command</param>
        /// <param name="args">arguments</param>
        /// <param name="outputFile">Output file path</param>
        /// <returns>Command return code</returns>
        public static int RunCommand(string exeFile, string cmd, string args, string cwd, string outputFile)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = exeFile;
            start.Arguments = string.Format("{0} {1}", cmd, args);
            start.WorkingDirectory = cwd;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;
            int returnCode = 0;
            using (Process process = Process.Start(start))
            {
                process.WaitForExit();
                using (StreamReader reader = process.StandardOutput)
                {
                    string output = reader.ReadToEnd();
                    if (outputFile != null)
                    {
                        using (StreamWriter writer = new StreamWriter(outputFile, append: true))
                        {
                            writer.Write(output);
                        }
                    }
                }
                returnCode = process.ExitCode;
            }
            return returnCode;
        }

        public static void KillProcessAndChildren(int pid)
        {
            // Cannot close 'system idle process'
            if (pid == 0)
            {
                return;
            }
            ManagementObjectSearcher searcher = new ManagementObjectSearcher
            ("Select * From Win32_Process Where ParentProcessID=" + pid);
            ManagementObjectCollection moc = searcher.Get();
            foreach (ManagementObject mo in moc)
            {
                KillProcessAndChildren(Convert.ToInt32(mo["ProcessID"]));
            }
            try
            {
                Process proc = Process.GetProcessById(pid);
                proc.Kill();
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
        public static List<Device> ReadDevicesFromFile(string jsonFile)
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
        public static List<LumXProcess> ReadProcessesFromFile(string jsonFile)
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
            catch (Exception)
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
        public static void WriteDeviceListToFile(List<Device> list, string jsonFile)
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
        public static string ReadFileContent(string filePath)
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
        public static void WriteToFile(string filePath, string content, bool append)
        {
            using (StreamWriter writer = new StreamWriter(filePath, append))
            {
                writer.Write(content);
            }
        }

        public static string GetInternalIPAddress()
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

        public static void LoadConfig()
        {
            using (var streamReader = File.OpenText("D:/Config/agent_config.txt"))
            {
                var lines = streamReader.ReadToEnd().Split("\r\n".ToCharArray(), StringSplitOptions.RemoveEmptyEntries);
                foreach (string line in lines)
                {
                    string[] fields = line.Split('=');
                    Settings.settingsDict[fields[0]] = fields[1];
                }
            }
        }
    }
}
