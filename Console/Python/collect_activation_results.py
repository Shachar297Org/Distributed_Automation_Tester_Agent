import os
import sys
import json
import time
from utils import *
from logger import *


def CollectActivationResults(devicesRecords: list, devicesFoldersDir: str, logger: object):
    activationResults = []
    for deviceRecord in devicesRecords:
        sn = deviceRecord['DeviceSerialNumber']
        gn = deviceRecord['DeviceType']
        deviceName = '_'.join([sn, gn])
        deviceFolderPath = os.path.join(devicesFoldersDir, deviceName)
        logFilePath = os.path.join(
            deviceFolderPath, 'Client', 'Debug_x64', 'Logs', 'log.txt')
        logger.WriteLog('Read logs from file {}'.format(logFilePath), 'info')
        isActivated = 'True'
        if not os.path.exists(logFilePath):
            isActivated = 'False'
        else:
            content = ReadFileContent(logFilePath)
            isActivated = 'False' if 'fail' in content.lower() else 'True'
        activationResults.append(
            {'DeviceSerialNumber': sn, 'DeviceType': gn, 'IsActivated': isActivated})
    return activationResults


if __name__ == "__main__":
    devicesJsonFile = sys.argv[1]
    devicesFoldersDir = sys.argv[2]
    activationResultsFile = sys.argv[3]

    configParser = LoadConfig()
    logger = InitLogger(configParser)

    if (not os.path.exists(devicesJsonFile)):
        logger.WriteLog('No such file {}'.format(
            devicesJsonFile), 'error')
        exit(2)

    if (not os.path.exists(devicesJsonFile)):
        logger.WriteLog('No such folder {}'.format(
            devicesFoldersDir), 'error')
        exit(2)

    content = ReadFileContent(devicesJsonFile)
    devicesRecords = json.loads(content)

    activationResults = CollectActivationResults(
        devicesRecords, devicesFoldersDir, logger)

    with open(activationResultsFile, 'w') as fp:
        json.dump(activationResults, fp)
