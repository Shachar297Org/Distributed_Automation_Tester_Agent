﻿using Console;
using Console.Utilities;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Web.Http;
using System.Text;
using System.Web.Http.Results;
using System.Threading.Tasks;
using Console.Models;
using Console.Interfaces;

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
        public async Task<JsonResult<string>> Init()
        {
            bool result = await backEnd.Init();
            return Json("{Result: " + result + "}");
        }

        [HttpPost]
        [Route("sendDevices")]
        public async Task SendDevices()
        {
            HttpContent requestContent = Request.Content;
            string content = await requestContent.ReadAsStringAsync();
            await backEnd.SendDevices(content);
        }

        [HttpPost]
        [Route("sendScript")]
        public async Task SendScript([FromBody] ScriptData scriptData)
        {
            await backEnd.SendScript(scriptData);
        }

        [HttpGet]
        [Route("testcmd")]
        public HttpResponseMessage TestCommand(string num)
        {
            Utils.LoadConfig();
            string pythonPath = Settings.Get("PYTHON");
            string pythonScriptsPath = Settings.Get("PYTHON_SCRIPTS_PATH");
            //int returnCode = Utils.RunCommand(@"pythonScript.py", "", num, @"D:\Temp",@"D:\test_center\out.txt");
            int returnCode = Utils.RunCommand(pythonPath, "pythonScript.py", num, pythonScriptsPath, @"D:\test_center\out.txt");
            var output = Utils.ReadFileContent(@"D:\test_center\out.txt");
            var response = Request.CreateResponse(HttpStatusCode.OK);
            var jsonText = "{returnCode:" + returnCode + ", " + "output:" + output + "}";
            response.Content = new StringContent(jsonText, Encoding.UTF8, "application/json");
            return response;
        }
    }
}
