using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Console.Models
{
    /// <summary>
    /// LumXProcess contains Process ID (pid) and name (<device_sn>_<device_gn>_server/client)
    /// </summary>
    public class LumXProcess
    {
        public LumXProcess(int pid, string name)
        {
            Pid = pid;
            Name = name;
        }

        public int Pid { get; set; }

        public string Name { get; set; }
    }
}
