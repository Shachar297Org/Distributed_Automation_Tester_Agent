def GetComparisonResultsFromLog(logFilePath: str, rdsRecordStrings: list):
    """
    Return comparison results from a log file
    """
    missingEventsFromLog = []

    # Retrieve log events from log file
    print('Load records from log file: {}'.format(logFilePath))
    logEntries = ReadLogFile(logFilePath)
    for i in range(len(logEntries)):
        logEntries[i]['entryTimeStamp'] = ConvertDatetime(
            logEntries[i]['entryTimeStamp'], '%m/%d/%Y %H:%M:%S %p',
            '%Y-%m-%d %H:%M:%S')
    print('Log records: {}'.format(len(logEntries)))
    logRecords = [ConvertEntryToRecord(entry) for entry in logEntries]

    # Get all log events that do not exist in RDS
    for logRecord in logRecords:
        if str(logRecord) not in rdsRecordStrings:
            missingEventsFromLog.append(logRecord.ToDict())
    print('{} missing records were found.'.format(len(missingEventsFromLog)))

    return missingEventsFromLog


def ArbitraryResults(sn: str, ga: str):
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


def CollectComparisonResults(config: object, sn: str, ga: str,
                             devicesFoldersDir: str):
    missingEvents = []
    deviceName = '_'.join([sn, ga])
    print('Collecting comparison results for {}'.format(deviceName))
    deviceFoldersDir = config['DEVICE_FOLDERS_DIR']

    # Connect to RDS
    host = config['RDS_HOST']
    db = config['RDS_DB']
    username = config['RDS_USER']
    password = config['RDS_PASS']
    rdsSim = True if config['RDS_SIM'].lower() == 'true' else False
    if rdsSim:
        return ArbitraryResults(sn, ga)
    dbConn = ConnectRDS(host, db, username, password)
    if not dbConn:
        print('Error: Could not connect to RDS.')
        return []

    # Retrieve from RDS all device events
    print('Retrieve from RDS all event entries related to the device')
    rdsEntries = GetAllDeviceEntries(dbConn, ga, sn)
    print('Entries in RDS: {}'.format(len(rdsEntries)))
    rdsRecords = [ConvertEntryToRecord(entry) for entry in rdsEntries]
    for i in range(len(rdsRecords)):
        rdsRecords[i].entryTimeStamp = ConvertDatetime(
            rdsRecords[i].entryTimeStamp, '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M:%S')
    rdsRecordStrings = [str(rdsRecord) for rdsRecord in rdsRecords]
    DisconnectRDS(dbConn)

    logsFolderPath = os.path.join(deviceFoldersDir, deviceName, 'Client',
                                  'Debug_x64', 'Logs', '1.0.0.0')
    logFileNames = os.listdir(logsFolderPath)
    for logFileName in logFileNames:
        logFilePath = os.path.join(logsFolderPath, logFileName)
        missingEventsFromLog = GetComparisonResultsFromLog(
            logFilePath, rdsRecordStrings)
        missingEvents.extend(missingEventsFromLog)

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

        tesCenterUrl = config['TEST_CENTER_URL']
        SendComparisonResults(tesCenterUrl, comparisonResults)

        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        traceback.print_exc()
        print('-----fail-----')
        exit(1)
