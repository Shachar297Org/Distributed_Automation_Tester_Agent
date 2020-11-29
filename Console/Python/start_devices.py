import os
import sys
import json
import time
import re
from utils import *
from create_device_env import *


def CopyScriptFileToDeviceFolders(devicesToCreate, scriptFilePath, configParser, logger):
    """
    Copy script file to every device folder
    """
    logger.WriteLog('Copy to {} devices'.format(devicesToCreate), 'info')

    for deviceRecord in devicesToCreate:
        prefix = configParser.get('Env', 'prefix')
        deviceName = '_'.join(
            [deviceRecord['DeviceSerialNumber'], deviceRecord['DeviceType']])
        deviceFolder = os.path.join(prefix, deviceName)
        scriptsFolder = os.path.join(deviceFolder, 'Scripts')

        if not os.path.exists(scriptsFolder):
            os.makedirs(scriptsFolder)

        destScriptPath = os.path.join(
            deviceFolder, 'Scripts', 'selfActivationScript.txt')

        logger.WriteLog('Copy script from {} to {}'.format(
            scriptFilePath, destScriptPath), 'info')
        copyfile(scriptFilePath, destScriptPath)
    time.sleep(5)


def ModifyActivationScript(scriptFile, ga, sn, logger):
    """
    Modify fields GA and SN in activation script
    """
    logger.WriteLog('Modify file {}'.format(scriptFile), 'info')
    with open(scriptFile, 'r+') as reader:
        text = reader.read()
        text = re.sub('<GA>', ga, text)
        text = re.sub('<SN>', sn, text)
        reader.seek(0)
        reader.write(text)
        reader.truncate()
    time.sleep(1)


def ModifyActivationScripts(devicesToCreate, scriptFilePath, configParser, logger):
    """
    Modify activation scripts for every device according to its GA and SN
    """
    for deviceRecord in devicesToCreate:
        prefix = configParser.get('Env', 'prefix')
        deviceName = '_'.join(
            [deviceRecord['DeviceSerialNumber'], deviceRecord['DeviceType']])
        deviceFolder = os.path.join(prefix, deviceName)
        scriptPath = os.path.join(
            deviceFolder, 'Scripts', 'selfActivationScript.txt')
        ga = deviceRecord['DeviceType']
        sn = deviceRecord['DeviceSerialNumber']
        ModifyActivationScript(scriptPath, ga, sn, logger)
    time.sleep(3)


def StartServer(deviceRecord, configParser, logger, servers):
    """
    Start server of a device
    """
    prefix = configParser.get('Env', 'prefix')
    deviceName = '_'.join(
        [deviceRecord['DeviceSerialNumber'], deviceRecord['DeviceType']])
    deviceFolder = os.path.join(prefix, deviceName)

    serverPath = os.path.join(
        deviceFolder, 'Server', 'Debug', 'LumXServerHost.exe')
    process = RunExecutable(serverPath, args=[], shell=False)
    logger.WriteLog('{} server process with pid {} started'.format(
        serverPath, process.pid), 'info')
    if process:
        servers.append({'Name': deviceName + 'Server', 'Pid': process.pid})


def StartClient(deviceRecord, scriptFilePath, configParser, logger, clients):
    """
    Start client of a device
    """
    prefix = configParser.get('Env', 'prefix')
    deviceName = '_'.join(
        [deviceRecord['DeviceSerialNumber'], deviceRecord['DeviceType']])
    deviceFolder = os.path.join(prefix, deviceName)

    clientPath = os.path.join(
        deviceFolder, 'Client', 'Debug_x64', 'ClientWPF_Tester_Logger.exe')

    activationScriptPath = os.path.join(
        deviceFolder, 'Scripts', 'selfActivationScript.txt')
    logger.WriteLog('Script path: {}'.format(activationScriptPath), 'info')

    logger.WriteLog('Client exe path: {}'.format(clientPath), 'info')

    process = RunExecutable(
        clientPath, args=[activationScriptPath, deviceName], shell=False)
    logger.WriteLog('{} client process with pid {} started'.format(
        clientPath, process.pid), 'info')
    if process:
        clients.append({'Name': deviceName + 'Client', 'Pid': process.pid})


def StartAllServers(devicesToCreate, configParser, logger, servers):
    """
    Start all device servers
    """
    for deviceRecord in devicesToCreate:
        StartServer(deviceRecord, configParser, logger, servers)


def StartAllClients(devicesToCreate, scriptFilePath, configParser, logger, clients):
    """
    Start all device clients
    """
    for deviceRecord in devicesToCreate:
        StartClient(deviceRecord, scriptFilePath,
                    configParser, logger, clients)


if __name__ == "__main__":
    # try:
    deviceToCreateFile = sys.argv[1]
    scriptFilePath = sys.argv[2]
    maxDevicesToStart = int(sys.argv[3])
    processesPath = sys.argv[4]

    configParser = LoadConfig()
    logger = InitLogger(configParser)

    if (not os.path.exists(deviceToCreateFile)):
        logger.WriteLog('No such folder {}'.format(
            deviceToCreateFile), 'error')
        exit(2)

    if (not os.path.exists(scriptFilePath)):
        logger.WriteLog('No such file {}'.format(scriptFilePath), 'error')
        exit(2)

    jsonContent = ReadFileContent(deviceToCreateFile)
    devicesToCreate = json.loads(jsonContent)[:maxDevicesToStart]

    CopyScriptFileToDeviceFolders(
        devicesToCreate, scriptFilePath, configParser, logger)

    logger.WriteLog(
        'Modify GA and SN in activation script of devices.', 'info')
    ModifyActivationScripts(
        devicesToCreate, scriptFilePath, configParser, logger)

    logger.WriteLog('Start devices (servers and clients)', 'info')
    servers = []
    clients = []
    StartAllServers(devicesToCreate, configParser, logger, servers)
    StartAllClients(devicesToCreate, scriptFilePath,
                    configParser, logger, clients)

    logger.WriteLog('Write server and client processes to json file', 'info')
    processes = servers + clients
    jsonString = json.dumps(processes)
    WriteToTextFile(processesPath, jsonString)

    # except Exception as ex:
    #     print(ex)
