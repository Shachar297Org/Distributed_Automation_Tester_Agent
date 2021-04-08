def CopyScriptFileToDeviceFolders(devicesToCreate, scriptFilePath, config):
    """
    Copy script file to every device folder
    """
    print('Copy to {} devices'.format(devicesToCreate))

    for deviceRecord in devicesToCreate:
        prefix = config['DEVICE_FOLDERS_DIR']
        deviceName = '_'.join(
            [deviceRecord['DeviceSerialNumber'], deviceRecord['DeviceType']])
        deviceFolder = os.path.join(prefix, deviceName)
        scriptsFolder = os.path.join(deviceFolder, 'Scripts')

        if not os.path.exists(scriptsFolder):
            os.makedirs(scriptsFolder)

        destScriptPath = os.path.join(deviceFolder, 'Scripts',
                                      'selfActivationScript.txt')

        print('Copy script from {} to {}'.format(scriptFilePath,
                                                 destScriptPath))
        copyfile(scriptFilePath, destScriptPath)
    time.sleep(5)


def ModifyActivationScript(scriptFile, ga, sn):
    """
    Modify fields GA and SN in activation script
    """
    print('Modify file {}'.format(scriptFile))
    with open(scriptFile, 'r+') as reader:
        text = reader.read()
        text = re.sub('<GA>', ga, text)
        text = re.sub('<SN>', sn, text)
        reader.seek(0)
        reader.write(text)
        reader.truncate()
    time.sleep(1)


def ModifyActivationScripts(devicesToCreate, scriptFilePath, config):
    """
    Modify activation scripts for every device according to its GA and SN
    """
    for deviceRecord in devicesToCreate:
        prefix = config['DEVICE_FOLDERS_DIR']
        deviceName = '_'.join(
            [deviceRecord['DeviceSerialNumber'], deviceRecord['DeviceType']])
        deviceFolder = os.path.join(prefix, deviceName)
        scriptPath = os.path.join(deviceFolder, 'Scripts',
                                  'selfActivationScript.txt')
        ga = deviceRecord['DeviceType']
        sn = deviceRecord['DeviceSerialNumber']
        ModifyActivationScript(scriptPath, ga, sn)
    time.sleep(3)


def StartServer(deviceRecord, config, servers, index):
    """
    Start server of a device
    """
    prefix = config['DEVICE_FOLDERS_DIR']
    sn = deviceRecord['DeviceSerialNumber']
    ga = deviceRecord['DeviceType']
    deviceName = '_'.join([sn, ga])
    deviceFolder = os.path.join(prefix, deviceName)
    serverExeName = config['SERVER_EXE_NAME']
    serverPath = os.path.join(deviceFolder, 'Server', 'Debug', serverExeName)
    print('Running server {}'.format(deviceName))
    process = RunExecutable(serverPath, args=[str(index)], shell=False)
    print('{} server process with pid {} started'.format(
        serverPath, process.pid))
    if process:
        servers.append({
            'Pid': process.pid,
            'DeviceType': ga,
            'DeviceSerialNumber': sn,
            'Type': 'Server'
        })


def StartClient(deviceRecord, scriptFilePath, config, clients, index):
    """
    Start client of a device
    """
    prefix = config['DEVICE_FOLDERS_DIR']
    sn = deviceRecord['DeviceSerialNumber']
    ga = deviceRecord['DeviceType']
    deviceName = '_'.join([sn, ga])
    deviceFolder = os.path.join(prefix, deviceName)

    clientExeName = config['CLIENT_EXE_NAME']
    clientFolderName = clientExeName.split('.')[0]

    clientPath = os.path.join(deviceFolder, clientFolderName, 'Debug_x64',
                              clientExeName)

    activationScriptPath = os.path.join(deviceFolder, 'Scripts',
                                        'selfActivationScript.txt')
    print('Script path: {}'.format(activationScriptPath))

    print('Client exe path: {}'.format(clientPath))

    print('Running client {}'.format(deviceName))
    process = RunExecutable(
        clientPath,
        args=[activationScriptPath, deviceName,
              str(index)],
        shell=False)
    print('{} client process with pid {} started'.format(
        clientPath, process.pid))
    if process:
        clients.append({
            'Pid': process.pid,
            'DeviceType': ga,
            'DeviceSerialNumber': sn,
            'Type': 'Client'
        })


def StartAllServers(devicesToCreate, config, servers):
    """
    Start all device servers
    """
    for index, deviceRecord in enumerate(devicesToCreate):
        StartServer(deviceRecord, config, servers, index)
        time.sleep(0.5)


def StartAllClients(devicesToCreate, scriptFilePath, config, clients):
    """
    Start all device clients
    """
    for index, deviceRecord in enumerate(devicesToCreate):
        StartClient(deviceRecord, scriptFilePath, config, clients, index)
        time.sleep(0.5)


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

        if (not os.path.exists(configFile)):
            print('No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        deviceToCreateFile = config['DEVICES_TO_CREATE_PATH']
        scriptFilePath = config['SCRIPT_PATH']
        processesPath = config['PROCESSES_PATH']

        if (not os.path.exists(deviceToCreateFile)):
            print('Error: No such folder {}'.format(deviceToCreateFile))
            exit(2)

        if (not os.path.exists(scriptFilePath)):
            print('Error: No such file {}'.format(scriptFilePath))
            exit(2)

        jsonContent = ReadFileContent(deviceToCreateFile)
        devicesToCreate = json.loads(jsonContent)

        CopyScriptFileToDeviceFolders(devicesToCreate, scriptFilePath, config)

        #print('Modify GA and SN in activation script of devices.')
        #ModifyActivationScripts(devicesToCreate, scriptFilePath, config)

        print('Start devices (servers and clients)')
        servers = []
        clients = []
        StartAllServers(devicesToCreate, config, servers)
        StartAllClients(devicesToCreate, scriptFilePath, config, clients)

        print('Write server and client processes to json file')
        processes = servers + clients
        jsonString = json.dumps(processes)
        WriteToTextFile(processesPath, jsonString)
        print('-----success-----')
        exit(0)

    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc()
        print('-----fail-----')
        exit(1)