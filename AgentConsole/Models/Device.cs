using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Text;

namespace Console.Models
{
    public class Device
    {
        public Device(string ga, string sn)
        {
            DeviceType = ga;
            DeviceSerialNumber = sn;
            Finished = false;
        }

        public string DeviceType { get; set; }

        public string DeviceSerialNumber { get; set; }

        public bool Finished { get; set; }
    }
}
