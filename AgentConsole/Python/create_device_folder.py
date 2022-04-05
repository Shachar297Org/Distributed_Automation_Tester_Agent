def CreateDeviceFolderWrapper(deviceName: list, config: object):
    """
    Create device folder
    """
    # Create device dictionary
    deviceDict = {}
    parts = deviceName.split('_')
    deviceDict['DeviceName'] = deviceName
    deviceDict['DeviceSerialNumber'] = parts[0]
    deviceDict['DeviceType'] = parts[1]

    # Create device folders base dir
    deviceFoldersBaseDir = config['DEVICE_FOLDERS_DIR']
    if not os.path.exists(deviceFoldersBaseDir):
        os.makedirs(deviceFoldersBaseDir)

    print('Creating device folder for: {}'.format(deviceName))

    t1 = time.time()
    CreateDeviceFolder(deviceDict, config)
    t2 = time.time()
    dt = math.ceil(t2 - t1)
    print('Device folder {} was created successfully. Time: {} sec'.format(
        deviceDict, dt))


if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    import time
    import math
    import traceback
    import pandas
    from utils import *
    from create_device_env import *

    print('-----create_device_folder-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]
        deviceName = sys.argv[2]

        if (not os.path.exists(configFile)):
            print('Error: No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        CreateDeviceFolderWrapper(deviceName, config)
        print('-----success-----')
        exit(0)

    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc()
        print('-----fail-----')
        exit(1)
