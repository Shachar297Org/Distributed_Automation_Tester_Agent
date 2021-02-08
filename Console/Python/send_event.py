def SendLogEventsFile(deviceName: str, logContent: str, testCenterUrl: str):
    print('Send script log of {} to test center {}'.format(
        deviceName, testCenterUrl))
    jsonObj = {'deviceName': deviceName, 'Content': logContent}
    response = requests.post(url=testCenterUrl + "/getScriptLog",
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps(jsonObj))
    if not response.ok:
        print('Request failed. status code: {}'.format(response.status_code))


if __name__ == "__main__":
    from activate_env import *
    ActivateEnv()

    import sys
    import json
    import time
    import requests
    from utils import *

    print('-----send_client_log-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]
        deviceName = sys.argv[2]
        logFile = sys.argv[3]

        if (not os.path.exists(logFile)):
            print('No such log file {}'.format(logFile))
            exit(2)

        config = LoadConfigText(configFile)

        testCenterUrl = config['TEST_CENTER_URL']

        logContent = ReadFileContent(logFile)

        SendLogFile(deviceName, logContent, testCenterUrl)

        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        print('-----fail-----')
        exit(1)
