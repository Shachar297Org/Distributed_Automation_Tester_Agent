import os
import sys
import json
import time
from utils import *
from create_device_env import *
from logger import *


def CreateDeviceFolders(devicesToCreateRecords: list, maxDevicesToCreate: int, configParser: object, logger: object):
    """
    Create device folders
    """
    # Filter devices to create
    deviceRecords = []
    for device in devicesToCreateRecords[:maxDevicesToCreate]:
        sn = device['DeviceSerialNumber']
        gn = device['DeviceType']
        deviceRecords.append(
            {'deviceName': '_'.join([sn, gn]), 'DeviceType': gn, 'DeviceSerialNumber': sn})

    # Create device folders base dir
    deviceFoldersBaseDir = configParser.get('Env', 'prefix')
    if not os.path.exists(deviceFoldersBaseDir):
        os.makedirs(deviceFoldersBaseDir)

    logger.WriteLog('Devices to create: {}/{}'.format(len(deviceRecords),
                                                      len(devicesToCreateRecords)), 'info')
    for deviceRecord in deviceRecords:
        try:
            logger.WriteLog('Creating env folder for {} ...'.format(
                deviceRecord), 'info')
            CreateDeviceFolder(deviceRecord, configParser)
            time.sleep(2)
        except OSError as ex:
            logger.WriteLog(ex, 'error')
            return False
        logger.WriteLog('Device env {} was created successfully.'.format(
            deviceRecord), 'info')
    return True


if __name__ == "__main__":
    # try:
    devicesToCreateFile = sys.argv[1]

    configParser = LoadConfig()
    logger = InitLogger(configParser)

    if (not os.path.exists(devicesToCreateFile)):
        logger.WriteLog('No such file {}'.format(
            devicesToCreateFile), 'error')
        exit(2)

    maxDevicesToCreate = int(sys.argv[2])

    content = ReadFileContent(devicesToCreateFile)
    devicesToCreateRecords = json.loads(content)

    CreateDeviceFolders(devicesToCreateRecords,
                        maxDevicesToCreate, configParser, logger)

    # except Exception as ex:
    #     logger.WriteLog(ex, 'error')
