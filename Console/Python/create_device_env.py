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


def ReadDevicesCsv(csvFile: str, config: object):
    """
    Read devices from csv file
    """
    prefix = config['DEVICE_FOLDERS_DIR']

    clients = []
    with open(csvFile, 'r') as reader:
        lines = reader.readlines()
        for line in lines:
            fields = [field.strip('\n ') for field in line.split(',')]
            deviceName = fields[0]
            deviceType = fields[1]
            serialNumber = fields[2]
            clients.append({
                'deviceName': deviceName,
                'path': os.path.join(prefix, deviceName),
                'deviceType': deviceType,
                'serialNumber': serialNumber
            })

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
    elements = [
        elem for elem in root.iter() if attributeKey in elem.attrib.values()
    ]
    if len(elements) == 0:
        return None
    element = elements[0]
    element.attrib['value'] = attributeValue
    root = tree.getroot()
    tree.write(xmlFile, encoding='utf-8', method='xml')


def CreateDeviceFolder(device: dict, config: object):
    """
    Create device folder
    """
    env = config['ENV']
    lumenisApiHost = config['API_LUMENIS']
    clientApp = config['CLIENT_PATH']
    serverApp = config['SERVER_PATH']
    activationApp = config['ACTIVATOR_PATH']
    opensslPath = config['OPENSSL_PATH']
    activationScriptFilePath = config['SCRIPT_PATH']

    deviceName = device['DeviceName']
    deviceType = device['DeviceType']
    serialNumber = device['DeviceSerialNumber']

    prefix = config['DEVICE_FOLDERS_DIR']
    deviceFolder = os.path.join(prefix, deviceName)

    # Create client folder
    if not os.path.exists(deviceFolder):
        os.mkdir(deviceFolder)

    clientFolderName = config['CLIENT_EXE_NAME'].split('.')[0]

    # if not os.path.exists(os.path.join(deviceFolder, clientFolderName)):
    CopyDirectory(clientApp, os.path.join(deviceFolder, clientFolderName))

    UpdateHaspFile(
        os.path.join(deviceFolder, clientFolderName, 'Debug_x64',
                     'HASP_SIMUL.ini'), device)

    # Create server folder
    # if not os.path.exists(os.path.join(deviceFolder, 'Server')):
    CopyDirectory(serverApp, os.path.join(deviceFolder, 'Server'))

    logsFolder = os.path.join(deviceFolder, 'Logs')
    certFolder = os.path.join(deviceFolder, 'LumXCertificationFolder')

    serverConfigPath = os.path.join(deviceFolder, 'Server', 'Debug',
                                    'ConfigurationSettings.Server.config')

    UpdateXmlConfigFile(serverConfigPath, 'LogFilesLocation', logsFolder)

    UpdateXmlConfigFile(serverConfigPath, 'CertificationFolderLocation',
                        certFolder)

    UpdateXmlConfigFile(serverConfigPath, 'aws-environment', env)

    UpdateXmlConfigFile(serverConfigPath, 'endpoint', lumenisApiHost)

    # Create acivator folder
    # if not os.path.exists(os.path.join(deviceFolder, 'LumXActivator')):
    # CopyDirectory(activationApp, os.path.join(deviceFolder, 'LumXActivator'))

    # Create scripts folder
    if not os.path.exists(os.path.join(deviceFolder, 'Scripts')):
        os.mkdir(os.path.join(deviceFolder, 'Scripts'))

    # destScriptPath = os.path.join(
    # deviceFolder, 'Scripts', 'activationScript.txt')
    # copyfile(activationScriptFilePath, destScriptPath)

    # UpdateXmlConfigFile(os.path.join(deviceFolder, 'LumXActivator',
    #                                 'Activator.exe.config'), 'LogFilesLocation', logsFolder)

    # UpdateXmlConfigFile(os.path.join(deviceFolder, 'LumXActivator',
    #                                 'Activator.exe.config'), 'CertificationFolderLocation', certFolder)

    # UpdateXmlConfigFile(os.path.join(deviceFolder, 'LumXActivator',
    #                                 'Activator.exe.config'), 'OpenSslExePath', opensslPath)
