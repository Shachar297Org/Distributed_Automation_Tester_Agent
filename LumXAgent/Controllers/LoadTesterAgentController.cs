using Console.Interfaces;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Text;
using Console.Utilities;
using Console.Models;
using System.Net.Http;
using System.Net;

namespace LumXAgentCore.Controllers
{
    [ApiController]
    [Route("/")]
    public class LoadTesterAgentController : Controller
    {
        private ILoadTesterAgent _loadTester;

        private static Settings Settings;

        public LoadTesterAgentController(ILoadTesterAgent loadTester, Settings settings)
        {
            _loadTester = loadTester;
            Settings = settings;
        }

        // Get: index
        [HttpGet("index")]
        //[Route("index")]
        public JsonResult Index()
        {
            string cwd = Directory.GetCurrentDirectory();
            string testCenterUrl = Settings["TEST_CENTER_URL"];
            return Json("{About: LumenisX Agent, cwd: " + cwd + ", test_center: " + testCenterUrl + "}");
        }

        // Get: agent settings
        [HttpGet("getAgentSettings")]
        //[Route("getAgentSettings")]
        public JsonResult GetAgentSettings()
        {
            var agentSettings = new AgentSettings();
            agentSettings.AgentDirPath = Settings["AGENT_DIR_PATH"];

            return Json(agentSettings);
        }

        // Get: init
        [HttpGet]
        [Route("init")]
        public async Task<JsonResult> Init()
        {
            bool result = await _loadTester.Init();
            return Json(new { Result = result });
        }

        [HttpPost]
        [Route("stop")]
        public async Task<JsonResult> Stop()
        {
            bool result = _loadTester.Stop();
            return Json(new { Result = result });
        }

        [HttpGet]
        [Route("getAgentData")]
        public JsonResult GetAgentData()
        {
            AgentData result = _loadTester.GetAgentData();
            return Json(result);
        }

        [HttpPost("sendDevices")]
        public async Task SendDevices([FromBody] List<Device> devices)
        {
            await _loadTester.SendDevices(devices);
        }

        [HttpPost]
        [Route("sendScript")]
        public async Task SendScript([FromBody] ScriptData scriptData)
        {
            await _loadTester.SendScript(scriptData);
        }

        [HttpPost]
        [Route("setSettings")]
        public async Task SetSettings([FromBody] AgentSettings settings)
        {
            await _loadTester.SetSettings(settings);
        }

    }
}
