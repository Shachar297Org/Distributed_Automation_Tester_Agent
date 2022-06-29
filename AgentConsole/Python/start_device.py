def StartServer(deviceName, deviceIndex, config):
    """
    Start server of a device
    """
    prefix = config['DEVICE_FOLDERS_DIR']
    parts = deviceName.split('_')
    sn, ga = parts[0], parts[1]
    deviceFolder = os.path.join(prefix, deviceName)
    serverExeName = config['SERVER_EXE_NAME']
    serverPath = os.path.join(deviceFolder, 'Server', 'Debug', serverExeName)
    print('Running server {}'.format(deviceName))
    process = RunExecutable(serverPath, args=[deviceIndex], shell=False)
    print('{} server process with pid {} started'.format(
        serverPath, process.pid))
    if process:
        return {
            'Pid': process.pid,
            'DeviceType': ga,
            'DeviceSerialNumber': sn,
            'Type': 'Server'
        }


def StartClient(deviceName, scriptFilePath, deviceIndex, config):
    """
    Start client of a device
    """
    prefix = config['DEVICE_FOLDERS_DIR']
    deviceFolder = os.path.join(prefix, deviceName)
    parts = deviceName.split('_')
    sn, ga = parts[0], parts[1]

    clientExeName = config['CLIENT_EXE_NAME']
    clientFolderName = config['CLIENT_PATH'].split('/')[-1]

    clientPath = os.path.join(deviceFolder, clientFolderName, 'Debug_x64',
                              clientExeName)

    print('Client exe path: {}'.format(clientPath))

    print('Running client {}'.format(deviceName))
    process = RunExecutable(clientPath,
                            args=[scriptFilePath, deviceName, deviceIndex],
                            shell=False)
    print('{} client process with pid {} started'.format(
        clientPath, process.pid))
    if process:
        return {
            'Pid': process.pid,
            'DeviceType': ga,
            'DeviceSerialNumber': sn,
            'Type': 'Client'
        }


def CreateScriptForDevice(deviceName, scriptFilePath, config):
    """
    Start client of a device
    """
    prefix = config['DEVICE_FOLDERS_DIR']
    deviceFolder = os.path.join(prefix, deviceName)
    parts = deviceName.split('_')
    sn, ga = parts[0], parts[1]

    filename = scriptFilePath.split('/')[-1]
    print(filename)

    # Opening JSON file
    f = open(scriptFilePath)

    data = json.load(f)

    print("----------------------------------------------------------------------------")

    print(data["Tests"][0]["Instructions"][0]["Parameters"][0]["SelectedValueString"])
    print(data["Tests"][0]["Instructions"][1]["Parameters"][0]["SelectedValueString"])

    data["Tests"][0]["Instructions"][0]["Parameters"][0]["SelectedValueString"] = ga
    data["Tests"][0]["Instructions"][1]["Parameters"][0]["SelectedValueString"] = sn
      
    print(data["Tests"][0]["Instructions"][0]["Parameters"][0]["SelectedValueString"])
    print(data["Tests"][0]["Instructions"][1]["Parameters"][0]["SelectedValueString"])

    # Closing file
    f.close()

    # Serializing json 
    json_object = json.dumps(data, indent = 4)
    print(json_object)
      
    out_path = os.path.join(deviceFolder, filename)
    print('Script path: {}'.format(out_path))

    # Writing to sample.json
    with open(out_path, "w") as outfile:
        outfile.write(json_object)

    return out_path

    



if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    import time
    import re
    import traceback
    from utils import *
    from create_device_env import *

    print('-----start_devices-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]
        deviceName = sys.argv[2]
        deviceIndex = sys.argv[3]

        if (not os.path.exists(configFile)):
            print('No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        scriptFilePath = config['SCRIPT_PATH']
        processesDirPath = config['PROCESSES_DIR_PATH']

        if not os.path.exists(scriptFilePath):
            print('Error: No such file {}'.format(scriptFilePath))
            exit(2)

        if not os.path.exists(processesDirPath):
            os.makedirs(processesDirPath)

        out_path = CreateScriptForDevice(deviceName, scriptFilePath, config)

        print('Start device {}'.format(deviceName))
        serverProcess = StartServer(deviceName, deviceIndex, config)
        #time.sleep(10)
        clientProcess = StartClient(deviceName, out_path, deviceIndex,
                                    config)

        print('Write server and client processes to json file')
        processes = [serverProcess, clientProcess]
        jsonString = json.dumps(processes)

        processesPath = os.path.join(processesDirPath,
                                     deviceName + '_proc.json')
        WriteToTextFile(processesPath, jsonString)
        print('-----success-----')
        exit(0)

    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc()
        print('-----fail-----')
        exit(1)
