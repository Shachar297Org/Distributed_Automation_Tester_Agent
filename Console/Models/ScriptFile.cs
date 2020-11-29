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
    public class ScriptFile
    {
        public ScriptFile(string type, string content)
        {
            Type = type;
            Content = content;
        }

        public string Type { get; set; }

        public string Content { get; set; }
    }
}
