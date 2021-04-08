using Console.Models;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Console.Interfaces
{
    public interface ILoadTesterAgent
    {
        Task<bool> Init();

        Task SendDevices(List<Device> devices);

        Task<bool> SendScript(ScriptData scriptData);
        Task SetSettings(AgentSettings settings);
        bool Stop();
        AgentData GetAgentData();
    }
}
