using System;
using System.Threading.Tasks;

namespace Shared
{
    public interface IBackendInterface
    {
        Task<bool> Init();

        Task SendDevices(string jsonContent);

        Task<bool> SendScript(string jsonContent);
    }
}
