def GetComparisonResultsFromLog(logFilePath):
    """
    Return comparison results from a log file
    """

    # Retrieve from RDS all event entries related to the device by SN and GA
    # Convert device entries to event records
    # Retieve all event entries from client logs
    # Get all log events that do not exist in RDS -> missing events
    # Return the missing events
    missingEventsFromLog = []
    return missingEventsFromLog


def RunCompare(deviceRec: dict):
    """
    Return comparison results for a device in format: <ga, sn, eventKey, eventVal, creationTime>
    """
    missingEventsOfDevice = []
    sn = deviceRec['DeviceSerialNumber']
    ga = deviceRec['DeviceType']
    deviceName = '_'.join([sn, ga])
    print('Collecting comparison results for {}'.format(deviceName))

    # Connect to RDS
    ConnectRDS()
    """
    logFilesPath = ...
    logFiles = os.listdir(logFilesPath)
    for logFile in logFiles:
        logFilePath = os.path.join(logFilesPath, logFile)
        missingEventsFromLog = GetComparisonResultsFromLog(logFilePath)
        missingEventsOfDevice.extend(missingEventsFromLog)
    """

    # Disconnect from RDS

    return missingEventsOfDevice


def CollectComparisonResults(devicesRecords: list, devicesFoldersDir: str):
    missingEvents = []
    for deviceRec in devicesRecords:
        deviceMissingEvents = RunCompare(deviceRec)
        # Write all missing events per each device to file missing_events.json
    return missingEvents


if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    from utils import *
    from compare import *

    print('-----compare_events-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]

        if (not os.path.exists(configFile)):
            print('No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        devicesJsonFile = config['DEVICES_TO_CREATE_PATH']
        devicesFoldersDir = config['DEVICE_FOLDERS_DIR']
        comparisonResultsFile = config['COMPARISON_RESULTS_PATH']

        if (not os.path.exists(devicesJsonFile)):
            print('No such file {}'.format(devicesJsonFile))
            exit(2)

        if (not os.path.exists(devicesFoldersDir)):
            print('No such folder {}'.format(devicesFoldersDir))
            exit(2)

        content = ReadFileContent(devicesJsonFile)
        devicesRecords = json.loads(content)

        comparisonResults = CollectComparisonResults(devicesRecords,
                                                     devicesFoldersDir)

        with open(comparisonResultsFile, 'w') as fp:
            json.dump(comparisonResults, fp)

        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        print('-----fail-----')
        exit(1)