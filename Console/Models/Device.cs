using System;
using System.Collections.Generic;
using System.Text;

namespace Console.Models
{
    public class Device
    {
        public Device(string ga, string sn, bool finished)
        {
            DeviceType = ga;
            DeviceSerialNumber = sn;
            Finished = finished;
        }

        public string DeviceType { get; set; }

        public string DeviceSerialNumber { get; set; }

        public bool Finished { get; set; }
    }
}
