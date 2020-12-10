def GetComparisonResultsFromLog(logFilePath: str):
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


def CollectComparisonResults(config: object, sn: str, ga: str,
                             devicesFoldersDir: str):
    missingEvents = []
    deviceName = '_'.join([sn, ga])
    print('Collecting comparison results for {}'.format(deviceName))

    # Connect to RDS
    host = config['RDS_HOST']
    db = config['RDS_DB']
    username = config['RDS_USER']
    password = config['RDS_PASS']
    rdsSim = True if config['RDS_SIM'].lower() == 'true' else False
    if rdsSim:
        return [
            {
                'EventDeviceType': ga,
                'EventDeviceSerialNumber': sn,
                'EventKey': 'E1',
                'EventValue': 'V1',
                'CreationTime': '12/10/2020 10:37:00'
            },
            {
                'EventDeviceType': ga,
                'EventDeviceSerialNumber': sn,
                'EventKey': 'E2',
                'EventValue': 'V2',
                'CreationTime': '12/10/2020 10:37:01'
            },
            {
                'EventDeviceType': ga,
                'EventDeviceSerialNumber': sn,
                'EventKey': 'E3',
                'EventValue': 'V3',
                'CreationTime': '12/10/2020 10:37:02'
            },
        ]
    """
    ConnectRDS(host, db, username, password)
    logFilesPath = ...
    logFiles = os.listdir(logFilesPath)
    for logFile in logFiles:
        logFilePath = os.path.join(logFilesPath, logFile)
        missingEventsFromLog = GetComparisonResultsFromLog(logFilePath)
        missingEventsOfDevice.extend(missingEventsFromLog)

    Disconnect from RDS
    """
    return missingEvents


def SendComparisonResults(tesCenterUrl: str, comparisonResults: list):
    response = requests.post(
        url='{}/getComparisonResults'.format(tesCenterUrl),
        json=comparisonResults)
    if not response.ok:
        print('Error: request failed. status code: {}'.format(
            response.status_code))


if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    import requests
    import traceback
    from utils import *
    from compare import *

    print('-----compare_events-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]
        sn = sys.argv[2]
        ga = sys.argv[3]

        deviceName = '_'.join([sn, ga])

        if not os.path.exists(configFile):
            print('No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        devicesFoldersDir = config['DEVICE_FOLDERS_DIR']
        comparisonResultsFolder = config['COMPARISON_RESULTS_DIR']

        if not os.path.exists(devicesFoldersDir):
            print('No such folder {}'.format(devicesFoldersDir))
            exit(2)

        if not os.path.exists(comparisonResultsFolder):
            os.makedirs(comparisonResultsFolder)

        comparisonResults = CollectComparisonResults(config, sn, ga,
                                                     devicesFoldersDir)

        comparisonResultsOfDeviceFile = os.path.join(comparisonResultsFolder,
                                                     deviceName + '.csv')

        WriteToCsvFile(comparisonResultsOfDeviceFile, comparisonResults)

        # with open(comparisonResultsOfDeviceFile, 'w') as fp:
        #     json.dump(comparisonResults, fp)

        tesCenterUrl = config['TEST_CENTER_URL']
        SendComparisonResults(tesCenterUrl, comparisonResults)

        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc()
        print('-----fail-----')
        exit(1)