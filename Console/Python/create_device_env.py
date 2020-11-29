import sys
import os
import time
import shutil
import configparser
import xml.etree.ElementTree as ET
from shutil import copyfile


def CopyDirectory(src: str, dest: str):
    """
    Copy directory from src to dest
    """
    if not os.path.exists(src):
        print('No such directory {}'.format(src))
        return
    try:
        if os.path.exists(dest):
            shutil.rmtree(dest)
            time.sleep(2)
        shutil.copytree(src, dest)
    except shutil.Error as ex:
        print('Directory not copied. Error {}'.format(ex))
    except OSError as ex:
        print('Directory not copied. Error {}'.format(ex))


def ReadDevicesCsv(csvFile: str, configParser: object):
    """
    Read devices from csv file
    """
    prefix = configParser.get('Env', 'prefix')

    clients = []
    with open(csvFile, 'r') as reader:
        lines = reader.readlines()
        for line in lines:
            fields = [field.strip('\n ') for field in line.split(',')]
            deviceName = fields[0]
            deviceType = fields[1]
            serialNumber = fields[2]
            clients.append(
                {'deviceName': deviceName, 'path': os.path.join(prefix, deviceName), 'deviceType': deviceType, 'serialNumber': serialNumber})

    return clients


def UpdateHaspFile(haspFile: str, deviceRecord: dict):
    """
    Update HASP file according to device record
    """
    firstLine = ''
    with open(haspFile, 'r') as reader:
        lines = reader.readlines()
        firstLine = lines[0]

    with open(haspFile, 'w') as writer:
        writer.write(firstLine)
        writer.write('GA = {}\n'.format(deviceRecord['DeviceType']))
        writer.write('SN = {}\n'.format(deviceRecord['DeviceSerialNumber']))


def UpdateXmlConfigFile(xmlFile: str, attributeKey: str, attributeValue: str):
    """
    Update xml config file by attriubte key and value
    """
    tree = ET.parse(xmlFile)
    root = tree.getroot()
    elements = [elem for elem in root.iter(
    ) if attributeKey in elem.attrib.values()]
    if len(elements) == 0:
        return None
    element = elements[0]
    element.attrib['value'] = attributeValue
    root = tree.getroot()
    tree.write(xmlFile, encoding='utf-8', method='xml')


def CreateDeviceFolder(device: dict, configParser: object):
    """
    Create device folder
    """
    clientApp = configParser.get('Paths', 'clientApp')
    serverApp = configParser.get('Paths', 'serverApp')
    activationApp = configParser.get('Paths', 'activationApp')
    opensslPath = configParser.get('Paths', 'openssl')
    activationScriptFilePath = configParser.get(
        'Scripts', 'activationScriptFilePath')

    deviceName = device['deviceName']
    deviceType = device['DeviceType']
    serialNumber = device['DeviceSerialNumber']

    prefix = configParser.get('Env', 'prefix')
    deviceFolder = os.path.join(prefix, deviceName)

    # Create client folder
    if not os.path.exists(deviceFolder):
        os.mkdir(deviceFolder)

    # if not os.path.exists(os.path.join(deviceFolder, 'Client')):
    CopyDirectory(clientApp, os.path.join(deviceFolder, 'Client'))

    UpdateHaspFile(os.path.join(
        deviceFolder, 'Client', 'Debug_x64', 'HASP_SIMUL.ini'), device)

    # Create server folder
    # if not os.path.exists(os.path.join(deviceFolder, 'Server')):
    CopyDirectory(serverApp, os.path.join(deviceFolder, 'Server'))

    logsFolder = os.path.join(deviceFolder, 'Logs')
    certFolder = os.path.join(deviceFolder, 'LumXCertificationFolder')

    UpdateXmlConfigFile(os.path.join(deviceFolder, 'Server', 'Debug',
                                     'ConfigurationSettings.Server.config'), 'LogFilesLocation', logsFolder)

    UpdateXmlConfigFile(os.path.join(deviceFolder, 'Server', 'Debug',
                                     'ConfigurationSettings.Server.config'), 'CertificationFolderLocation', certFolder)

    # Create acivator folder
    # if not os.path.exists(os.path.join(deviceFolder, 'LumXActivator')):
    CopyDirectory(activationApp, os.path.join(deviceFolder, 'LumXActivator'))

    # Create scripts folder
    if not os.path.exists(os.path.join(deviceFolder, 'Scripts')):
        os.mkdir(os.path.join(deviceFolder, 'Scripts'))

    # destScriptPath = os.path.join(
        # deviceFolder, 'Scripts', 'activationScript.txt')
    # copyfile(activationScriptFilePath, destScriptPath)

    UpdateXmlConfigFile(os.path.join(deviceFolder, 'LumXActivator',
                                     'LumXActivator.exe.config'), 'LogFilesLocation', logsFolder)

    UpdateXmlConfigFile(os.path.join(deviceFolder, 'LumXActivator',
                                     'LumXActivator.exe.config'), 'CertificationFolderLocation', certFolder)

    UpdateXmlConfigFile(os.path.join(deviceFolder, 'LumXActivator',
                                     'LumXActivator.exe.config'), 'OpenSslExePath', opensslPath)
