


def CreateDeviceFolders(devicesToCreateRecords: list, config: object):
    """
    Create device folders
    """
    # Create device dictionaries list
    deviceRecords = []
    for device in devicesToCreateRecords:
        sn = device['DeviceSerialNumber']
        gn = device['DeviceType']
        deviceRecords.append({
            'DeviceName': '_'.join([sn, gn]),
            'DeviceType': gn,
            'DeviceSerialNumber': sn
        })

    # Create device folders base dir
    deviceFoldersBaseDir = config['DEVICE_FOLDERS_DIR']
    if not os.path.exists(deviceFoldersBaseDir):
        os.makedirs(deviceFoldersBaseDir)

    print('Devices to create: {}'.format(len(deviceRecords)))

    T1 = time.time()
    for deviceRecord in deviceRecords:
        t1 = time.time()
        print('Creating env folder for {} ...'.format(deviceRecord))
        CreateDeviceFolder(deviceRecord, config)
        t2 = time.time()
        dt = math.ceil(t2 - t1)
        print('Device env {} was created successfully. Time: {} sec'.format(
            deviceRecord, dt))

    T2 = time.time()
    DT = math.ceil(T2 - T1)
    print('Total time: {} sec'.format(DT))


if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    import time
    import math
    import traceback
    from utils import *
    from create_device_env import *

    print('-----create_device_folders-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]

        if (not os.path.exists(configFile)):
            print('Error: No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        devicesToCreateFile = config['DEVICES_TO_CREATE_PATH']

        content = ReadFileContent(devicesToCreateFile)
        devicesToCreateRecords = json.loads(content)

        CreateDeviceFolders(devicesToCreateRecords, config)
        print('-----success-----')
        exit(0)

    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc()
        print('-----fail-----')
        exit(1)

    exit(0)