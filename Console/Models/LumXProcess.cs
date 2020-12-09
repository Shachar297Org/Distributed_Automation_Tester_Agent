using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Console.Models
{
    /// <summary>
    /// LumXProcess contains Process ID (pid), GN, SN and type (server/client)
    /// </summary>
    public class LumXProcess
    {
        public LumXProcess(int pid, string ga, string sn, string type)
        {
            Pid = pid;
            DeviceType = ga;
            DeviceSerialNumber = sn;
            Type = type;
        }

        public int Pid { get; set; }

        public string DeviceType { get; set; }

        public string DeviceSerialNumber { get; set; }

        public string Type { get; set; }

    }
}
