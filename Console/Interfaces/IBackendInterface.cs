using Console.Models;
using System;
using System.Threading.Tasks;

namespace Console.Interfaces
{
    public interface IBackendInterface
    {
        Task<bool> Init();

        Task SendDevices(string jsonContent);

        Task<bool> SendScript(ScriptData scriptData);
        Task SetSettings(AgentSettings settings);
        bool Stop();
        AgentData GetAgentData();
    }
}
