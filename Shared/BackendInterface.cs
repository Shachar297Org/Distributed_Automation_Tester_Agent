using System;

namespace Shared
{
    public interface IBackendInterface
    {
        bool Init();

        bool SendDevices(string jsonContent);

        bool SendScript(string jsonContent);
    }
}
