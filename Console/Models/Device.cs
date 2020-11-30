using System;
using System.Collections.Generic;
using System.Text;

namespace Main
{
    public class Device
    {
        public Device(string ga, string sn, bool isActivated)
        {
            DeviceType = ga;
            DeviceSerialNumber = sn;
            IsActivated = isActivated;
        }

        public string DeviceType { get; set; }

        public string DeviceSerialNumber { get; set; }

        public bool IsActivated { get; set; }
    }
}
