import os
import subprocess
import re
from compare import *
from create_device_env import *
from shutil import copyfile
import requests
import time
import fileinput
from logger import *


class Agent:
    def __init__(self, configFile: str, port: int, maxDevicesToCreate: int):
        self.configFile = configFile
        self.port = port
        self.maxDevicesToCreate = maxDevicesToCreate
        self.state = 'disconnected'
        self.configParser = configparser.ConfigParser()
        self.configParser.read(configFile, encoding='utf-8')
        self.servers = {}
        self.clients = {}
        self.deviceRecords = []
        self.name = 'Agent-{}'.format(self.port)
        self.CreateAgentFolder()
        logFile = os.path.join(self.agentFolder, 'logFile.txt')
        self.logger = Logger('Agent-{}'.format(self.port), logFile)

    def __str__(self):
        return 'Agent-{}'.format(self.port)

    def CreateAgentFolder(self):
        """
        Create agent folder
        """
        baseFolder = self.GetConfigParam('Env', 'baseFolder')
        self.agentFolder = os.path.join(baseFolder, self.name)
        if not os.path.exists(self.agentFolder):
            os.mkdir(self.agentFolder)

    def WriteLog(self, msg: str, level: str):
        self.logger.WriteLog(msg, level)

    def GetConfigParam(self, section, param):
        """
        Return config parameter
        """
        return self.configParser.get(section, param)

    def ChangeState(self, state):
        self.state = state

    def SendConnect(self):
        """
        Send connect command to test center
        """
        print('---Sending connect to test center---')
        print('Waiting 5 sec till the agent app is run...')
        time.sleep(5)
        testCenterIP = self.GetConfigParam('test_center', 'ip')
        testCenterPort = self.GetConfigParam('test_center', 'port')
        r = requests.get(
            'http://{}:{}/connect?agent_port={}'.format(testCenterIP, testCenterPort, self.port))
        print('Sent connect to test center')
        print(r.status_code)
        if r.status_code == 200:
            self.state = 'connected'
            print(r.json())

    def CreateDevicesEnvs(self, devicesToCreate: list):
        """
        Create device folders
        """
        # Filter devices to create
        deviceRecords = []
        for device in devicesToCreate[:self.maxDevicesToCreate]:
            sn = device['deviceSerialNumber']
            gn = device['deviceType']
            deviceRecords.append(
                {'deviceName': '_'.join([sn, gn]), 'deviceType': gn, 'serialNumber': sn})
        self.deviceRecords = deviceRecords

        self.WriteLog('Devices to create: {}/{}'.format(len(self.deviceRecords),
                                                        len(devicesToCreate)), 'info')
        for deviceRecord in self.deviceRecords:
            try:
                self.WriteLog('Creating env folder for {} ...'.format(
                    deviceRecord), 'info')
                CreateDeviceEnv(deviceRecord, self.configFile)
                time.sleep(7)
            except OSError as ex:
                self.WriteLog(ex, 'error')
                return False
            self.WriteLog('Device env {} was created successfully.'.format(
                deviceRecord), 'info')
        return True

    def CopyScriptFileToDeviceFolders(self, scriptPath: str):
        """
        Copy script file to every device folder
        """
        print('Copy to {} devices'.format(len(self.deviceRecords)))
        for deviceRecord in self.deviceRecords:
            prefix = self.GetConfigParam('Env', 'prefix')
            deviceName = deviceRecord['deviceName']
            deviceFolder = os.path.join(prefix, deviceName)
            destScriptPath = os.path.join(
                deviceFolder, 'Scripts', 'selfActivationScript.txt')
            print('Copy script from {} to {}'.format(
                scriptPath, destScriptPath))
            copyfile(scriptPath, destScriptPath)
        time.sleep(5)

    def ModifyActivationScripts(self):
        """
        Modify activation scripts for every device according to its GA and SN
        """
        for deviceRecord in self.deviceRecords:
            prefix = self.GetConfigParam('Env', 'prefix')
            deviceName = deviceRecord['deviceName']
            deviceFolder = os.path.join(prefix, deviceName)
            scriptPath = os.path.join(
                deviceFolder, 'Scripts', 'selfActivationScript.txt')
            ga = deviceRecord['deviceType']
            sn = deviceRecord['serialNumber']
            self.ModifyActivationScript(scriptPath, ga, sn)
        time.sleep(3)

    def ModifyActivationScript(self, scriptFile: str, ga: str, sn: str):
        """
        Modify fields GA and SN in activation script 
        """
        self.WriteLog('Modify file {}'.format(scriptFile), 'info')
        with open(scriptFile, 'r+') as reader:
            text = reader.read()
            text = re.sub('<GA>', ga, text)
            text = re.sub('<SN>', sn, text)
            reader.seek(0)
            reader.write(text)
            reader.truncate()
        time.sleep(1)

    def StartServer(self, deviceRecord: dict):
        """
        Start server of a device
        """
        prefix = self.GetConfigParam('Env', 'prefix')
        deviceName = deviceRecord['deviceName']
        deviceFolder = os.path.join(prefix, deviceName)

        serverPath = os.path.join(
            deviceFolder, 'Server', 'Debug', 'LumXServerHost.exe')
        process = RunExecutable(serverPath, args=[], shell=False)
        print('{} server process with pid {} started'.format(
            serverPath, process.pid))
        if process:
            self.servers[deviceRecord['deviceName'] + 'Server'] = process

    def StartClient(self, deviceRecord: dict):
        """
        Start client of a device
        """
        prefix = self.GetConfigParam('Env', 'prefix')
        deviceName = deviceRecord['deviceName']
        deviceFolder = os.path.join(prefix, deviceName)

        clientPath = os.path.join(
            deviceFolder, 'Client', 'Debug_x64', 'ClientWPF_Tester_Logger.exe')

        activationScriptPath = os.path.join(
            deviceFolder, 'Scripts', 'selfActivationScript.txt')
        self.WriteLog('Script path: {}'.format(activationScriptPath), 'info')

        self.WriteLog('Client exe path: {}'.format(clientPath), 'info')

        process = RunExecutable(
            clientPath, args=[activationScriptPath, deviceRecord['deviceName']], shell=False)
        # process = RunExecutable(clientPath, args=[], shell=False)
        print('{} client process with pid {} started'.format(
            clientPath, process.pid))
        if process:
            self.clients[deviceRecord['deviceName'] + 'Client'] = process

    def StartAllServers(self):
        """
        Start all device servers
        """
        for deviceRecord in self.deviceRecords:
            self.StartServer(deviceRecord)

    def StartAllClients(self):
        """
        Start all device clients
        """
        for deviceRecord in self.deviceRecords:
            self.StartClient(deviceRecord)

    def StopServer(self, deviceName):
        """
        Stop device server
        """
        print('Stop server {}'.format(self.servers[deviceName].pid))
        self.servers[deviceName].kill()
        print('{} server stopped.'.format(deviceName))

    def StopClient(self, deviceName):
        """
        Stop device client
        """
        print('Stopping client {}'.format(deviceName))
        self.clients[deviceName].kill()
        print('{} client stopped.'.format(deviceName))

    def StopAllServers(self):
        """
        Stop all device servers
        """
        for deviceName in self.servers.keys():
            self.StopServer(deviceName)

    def StopAllClients(self):
        """
        Stop all device clients
        """
        for deviceName in self.clients.keys():
            self.StopClient(deviceName)
