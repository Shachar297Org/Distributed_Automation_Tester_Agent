def SendRequestLogin(config: object):
    """
    Sends to api host login request and return access token
    """
    loginHost = config['API_LOGIN_HOST']
    loginData = {"email": config['API_USER'], "password": config['API_PASS']}
    response = requests.post(url=loginHost,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps(loginData))
    if not response.ok:
        print('Request failed. status code: {} reason: {}'.format(
            response.status_code, response.reason))
        return None
    jsonObj = response.json()
    return jsonObj['accessToken']


def GetPreviousDate():
    fromTime = datetime.datetime.now() - timedelta(days=1)
    return fromTime.strftime('%Y-%m-%d')


def GetDeviceEvents(sn: str, ga: str, config: object):
    accessToken = SendRequestLogin(config)
    if not accessToken:
        print('Error: Login failed.')
        raise Exception('Cannot login portal')
    print('Login success.')
    apiEventHost = config['API_EVENT']
    nowDate = datetime.datetime.now().strftime("%Y-%m-%d")
    prevDate = GetPreviousDate()
    prevDate = '2020-12-24'
    apiEventUrl = apiEventHost + '?deviceSerialNumber={}&deviceType={}&from={}T08%3A00%3A00.015Z&to={}T08%3A00%3A00.015Z'.format(
        sn, ga, prevDate, nowDate)

    print('Url: {}'.format(apiEventUrl))

    response = requests.get(url=apiEventUrl,
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization':
                                'Bearer {}'.format(accessToken)
                            })
    print('Response: ', response.status_code, response.reason)
    jsonData = response.json()
    eventObjects = jsonData['data']
    return eventObjects


def GetComparisonResultsFromLog(logFilePath: str, rdsRecordStrings: list):
    """
    Return comparison results from a log file
    """
    missingEventsFromLog = []

    # Retrieve log events from log file
    print('Load records from log file: {}'.format(logFilePath))
    columns = [
        'deviceType', 'deviceSerialNumber', 'entryKey', 'entryValue',
        'entryTimestamp'
    ]
    logEntries = ReadLogFile(logFilePath, columns)

    for i in range(len(logEntries)):
        logEntries[i]['entryTimestamp'] = ConvertDatetimeFromAMPMTo24(
            logEntries[i]['entryTimestamp'], '%m/%d/%Y %H:%M:%S %p')
    print('Log records: {}'.format(len(logEntries)))

    logRecords = [ConvertEntryToRecord(entry) for entry in logEntries]

    # Get all log events that do not exist in RDS
    for logRecord in logRecords:
        if str(logRecord) not in rdsRecordStrings:
            missingEventsFromLog.append(logRecord.ToDict())
    print('{} missing records were found.'.format(len(missingEventsFromLog)))

    return missingEventsFromLog


def CollectComparisonResults(config: object, sn: str, ga: str,
                             devicesFoldersDir: str):
    missingEvents = []
    deviceName = '_'.join([sn, ga])
    print('Collecting comparison results for {}'.format(deviceName))
    deviceFoldersDir = config['DEVICE_FOLDERS_DIR']

    rdsSim = True if config['RDS_SIM'].lower() == 'true' else False
    if rdsSim:
        return []

    # Retrieve from RDS all device events
    print('Retrieve from RDS all event entries related to the device')
    rdsEntries = GetDeviceEvents(sn, ga, config)
    print('Entries in RDS: {}'.format(len(rdsEntries)))
    rdsRecords = [ConvertEntryToRecord(entry) for entry in rdsEntries]

    for i in range(len(rdsRecords)):
        rdsRecords[i].entryTimeStamp = ConvertDatetime(
            rdsRecords[i].entryTimeStamp, '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S')
    rdsRecordStrings = [str(rdsRecord) for rdsRecord in rdsRecords]

    clientFolderName = config['CLIENT_EXE_NAME'].split('.')[0]
    logsFolderPath = os.path.join(deviceFoldersDir, deviceName,
                                  clientFolderName, 'Debug_x64', 'Logs',
                                  '1.0.0.0')
    logFileNames = os.listdir(logsFolderPath)
    for logFileName in logFileNames:
        logFilePath = os.path.join(logsFolderPath, logFileName)
        if os.path.isdir(logFilePath):
            continue
        missingEventsFromLog = GetComparisonResultsFromLog(
            logFilePath, rdsRecordStrings)
        missingEvents.extend(missingEventsFromLog)

    return missingEvents


def SendComparisonResults(tesCenterUrl: str, comparisonResults: list):
    try:
        response = requests.post(
            url='{}/getComparisonResults'.format(tesCenterUrl),
            json=comparisonResults)
        if not response.ok:
            print('Error: request failed. status code: {}'.format(
                response.status_code))
    except Exception as ex:
        print('Error: test center is not reachable {}'.format(ex))


if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    import requests
    import traceback
    from datetime import timedelta
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
