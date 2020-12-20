using System;
using System.Threading.Tasks;

namespace Shared
{
    public interface IBackendInterface
    {
        Task<bool> Init();

        bool SendDevices(string jsonContent);

        bool SendScript(string jsonContent);
    }
}
