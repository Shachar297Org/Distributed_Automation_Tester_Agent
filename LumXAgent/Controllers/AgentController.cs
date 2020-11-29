using Console;
using Console.Utilities;
using Shared;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Web.Http;
using System.Web.Http.Results;

namespace LumXAgent.Controllers
{
    public class AgentController : ApiController
    {
        IBackendInterface backEnd;

        public AgentController()
        {
            backEnd = new BackEnd();
        }

        // Get: index
        [HttpGet]
        [Route("index")]
        public JsonResult<string> Index()
        {
            string cwd = Directory.GetCurrentDirectory();
            Utils.LoadConfig();
            string testCenterUrl = Settings.Get("TEST_CENTER_URL");
            return Json("{About: LumenisX Agent, cwd: " + cwd + ", test_center: " + testCenterUrl + "}");
        }

        // Get: init
        [HttpGet]
        [Route("init")]
        public JsonResult<string> Init()
        {
            bool result = backEnd.Init();
            return Json("{Result: " + result + "}");
        }

        [HttpPost]
        [Route("sendDevices")]
        public void SendDevices()
        {
            HttpContent requestContent = Request.Content;
            string content = requestContent.ReadAsStringAsync().Result;
            backEnd.SendDevices(content);
        }

        [HttpPost]
        [Route("sendScript")]
        public void SendScript()
        {
            HttpContent requestContent = Request.Content;
            string scriptContent = requestContent.ReadAsStringAsync().Result;
            backEnd.SendScript(scriptContent);
        }
    }
}
