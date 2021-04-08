using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Console.Models
{
    public enum AgentStatus
    {
        INIT,
        CREATING_DEVICE_FOLDERS,
        RUNNING,
        FINISHED
    }

    public class AgentSettings
    {
        public string TestCenterUrl { get; set; }
        public string AgentDirPath { get; set; }        
    }

    public class AgentData
    {
        public int ServersNumber { get; set; }
        public int ClientsNumber { get; set; }

        public List<Device> Devices { get; set; }

        public string Status { get; set; }
    }
}
