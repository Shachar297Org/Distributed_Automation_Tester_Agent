import os
import sys
import json
import time
from utils import *


def CollectActivationResults(devicesRecords: list, devicesFoldersDir: str):
    activationResults = []
    for deviceRecord in devicesRecords:
        sn = deviceRecord['DeviceSerialNumber']
        gn = deviceRecord['DeviceType']
        deviceName = '_'.join([sn, gn])
        deviceFolderPath = os.path.join(devicesFoldersDir, deviceName)
        logFilePath = os.path.join(
            deviceFolderPath, 'Client', 'Debug_x64', 'Logs', 'log.txt')
        print('Read logs from file {}'.format(logFilePath))
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
    print('-----collect_activation_results-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]

        if (not os.path.exists(configFile)):
            print('No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        devicesJsonFile = config['DEVICES_TO_CREATE_PATH']
        devicesFoldersDir = config['DEVICE_FOLDERS_DIR']
        activationResultsFile = config['ACTIVATION_RESULTS_PATH']

        if (not os.path.exists(devicesJsonFile)):
            print('No such file {}'.format(devicesJsonFile))
            exit(2)

        if (not os.path.exists(devicesFoldersDir)):
            print('No such folder {}'.format(devicesFoldersDir))
            exit(2)

        content = ReadFileContent(devicesJsonFile)
        devicesRecords = json.loads(content)

        activationResults = CollectActivationResults(
            devicesRecords, devicesFoldersDir)

        with open(activationResultsFile, 'w') as fp:
            json.dump(activationResults, fp)

        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        print('-----fail-----')
        exit(1)
