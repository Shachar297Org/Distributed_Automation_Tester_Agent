using System;
using System.Collections.Generic;
using System.Text;

namespace Main
{
    public class Event
    {
        public Event(string ga, string sn, string ekey, string evalue, DateTime time)
        {
            EventDeviceType = ga;
            EventDeviceSerialNumber = sn;
            EventKey = ekey;
            EventValue = evalue;
            CreationTime = time;
        }

        public string EventDeviceType { get; set; }

        public string EventDeviceSerialNumber { get; set; }

        public string EventKey { get; set; }

        public string EventValue { get; set; }

        public DateTime CreationTime { get; set; }
    }
}
