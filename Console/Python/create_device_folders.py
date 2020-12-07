import os
import sys
import json
import time
import traceback
from utils import *
from create_device_env import *


def CreateDeviceFolders(devicesToCreateRecords: list, maxDevicesToCreate: int, config: object):
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
    deviceFoldersBaseDir = config['DEVICE_FOLDERS_DIR']
    if not os.path.exists(deviceFoldersBaseDir):
        os.makedirs(deviceFoldersBaseDir)

    print('Devices to create: {}/{}'.format(len(deviceRecords),
                                            len(devicesToCreateRecords)))
    for deviceRecord in deviceRecords:
        try:
            print('Creating env folder for {} ...'.format(deviceRecord))
            CreateDeviceFolder(deviceRecord, config)
            time.sleep(2)
        except Exception as ex:
            print('Error: {} {}'.format(ex, print))
            traceback.print_exc()
            return False
        print('Device env {} was created successfully.'.format(deviceRecord))
    return True


if __name__ == "__main__":
    print('-----create_device_folders-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]

        if (not os.path.exists(configFile)):
            print('Error: No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        devicesToCreateFile = config['DEVICES_TO_CREATE_PATH']
        maxDevicesToCreate = int(config['MAX_DEVICES_TO_CREATE'])

        content = ReadFileContent(devicesToCreateFile)
        devicesToCreateRecords = json.loads(content)

        CreateDeviceFolders(devicesToCreateRecords, maxDevicesToCreate, config)
        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        print('-----fail-----')
        exit(1)
