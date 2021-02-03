using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Console.Models
{
    /// <summary>
    /// ScriptFile contains type (text/json/...) and content
    /// </summary>
    public class ScriptData
    {
        public ScriptData(string type, string content, int stoppingDelay)
        {
            Type = type;
            Content = content;
            StoppingDelay = stoppingDelay;
        }

        public string Type { get; set; }

        public string Content { get; set; }

        public int StoppingDelay { get; set; }
    }
}
