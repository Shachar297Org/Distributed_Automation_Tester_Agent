using System;
using System.Threading.Tasks;

namespace Shared
{
    public interface IBackendInterface
    {
        Task<bool> Init();

        void SendDevices(string jsonContent);

        bool SendScript(string jsonContent);
    }
}
