def SendActivationResults(resultRecords: list, testCenterUrl: str):
    print('Send activation results to test center {}'.format(testCenterUrl))
    response = requests.post(url=testCenterUrl,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps(resultRecords))
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

    print('-----send_activation_results-----')
    print('Arguments: {}'.format(sys.argv))

    try:
        configFile = sys.argv[1]

        if (not os.path.exists(configFile)):
            print('No such config file {}'.format(configFile))
            exit(2)

        config = LoadConfigText(configFile)

        testCenterUrl = config['TEST_CENTER_URL']
        activationResultsFile = config['ACTIVATION_RESULTS_PATH']

        if (not os.path.exists(activationResultsFile)):
            print('No such file {}'.format(activationResultsFile))
            exit(2)

        content = ReadFileContent(activationResultsFile)
        resultRecords = json.loads(content)

        activationResults = SendActivationResults(resultRecords, testCenterUrl)

        print('-----success-----')

    except Exception as ex:
        print('Error: {}'.format(ex))
        print('-----fail-----')
        exit(1)
