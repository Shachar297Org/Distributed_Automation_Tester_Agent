﻿using System;
using System.Collections.Generic;
using System.Text;

namespace Main
{
    public class Device
    {
        public Device(string ga, string sn)
        {
            DeviceType = ga;
            DeviceSerialNumber = sn;
        }

        public string DeviceType { get; set; }
        public string DeviceSerialNumber { get; set; }
    }
}
