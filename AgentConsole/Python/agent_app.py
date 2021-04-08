import os
import sys
from flask import Flask, jsonify, request
import requests
from agent import *
import threading
from utils import *
import time


app = Flask(__name__)


agent = None


@app.route('/')
def index():
    return jsonify({'About': 'LumenisX Agent'})


@app.route('/ack')
def Ack():
    agent.ChangeState('connected')
    return jsonify({'Ack': 'Success'})


@app.route('/sendDevices', methods=["POST"])
def SendDevices():
    """
    Send devices list to agent
    """
    # Agent received json containing devices to create
    devicesJson = request.get_json()
    print(devicesJson)
    agent.WriteLog(
        'Got from test center json file: {}'.format(devicesJson), 'info')

    # Write to file devices to create
    csvFile = os.path.join(
        agent.agentFolder, 'devices_for_agent-{}.csv'.format(agent.port))
    agent.WriteLog(
        'Write devices to create to file {}.'.format(csvFile), 'info')
    WriteToCsvFile(csvFile, devicesJson)

    # Agent start creating device folders
    agent.WriteLog('Start creating device folders.', 'info')
    # todo: perform this operation with thread and use thread.join to wait for the thread to finish
    # agent.CreateDevicesEnvs(devicesJson)
    #agent.WriteLog('Send ready.', 'info')
    return jsonify({'devices': devicesJson}, 200)


@app.route('/sendScript', methods=["POST"])
def SendScript():
    """
    Send script file to agent
    """
    # Agent receives json with script file
    scriptFileObj = request.get_json()
    scriptFilePath = os.path.join(
        agent.agentFolder, 'selfActivationScript.txt')

    WriteToTextFile(scriptFilePath, str(scriptFileObj['content']))
    print('Agent received script')
    time.sleep(3)
    #agent.WriteLog('Copy script to device folders.', 'info')
    # agent.CopyScriptFileToDeviceFolders(scriptFilePath)
    #agent.WriteLog('Modify GA and SN in activation script of devices.', 'info')
    # agent.ModifyActivationScripts()

    agent.WriteLog('Start devices (servers and clients)', 'info')
    # agent.StartAllServers()
    # agent.StartAllClients()

    # todo: Check server and client logs, check activation results and report to test center

    return jsonify({'state': 'received script'}, 200)


@ app.route('/getAgentPort')
def GetAgentPort():
    """
    Get agent rest-api port
    """
    return jsonify({'Agent port': agent.port})


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Enter port and max_devices_to_create as arguments.')
        exit(1)

    port = int(sys.argv[1])
    maxDevicesToCreate = int(sys.argv[2])

    agent = Agent('config.ini', port, maxDevicesToCreate)

    agent.WriteLog('Agent {} was created.'.format(agent), 'info')

    # Send /connect to test center
    #connectThread = threading.Thread(target=agent.SendConnect)
    # connectThread.start()

    # Run rest-api on port <port>
    agent.WriteLog('Run rest-api on port {}.'.format(agent.port), 'info')
    app.run(debug=True, host='0.0.0.0', port=port)
