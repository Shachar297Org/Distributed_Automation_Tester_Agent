import os
import pandas
import datetime
import csv
from configparser import ConfigParser
import subprocess
from logger import *


def ReadLogFile(logFile, columns=None):
    """
    Read log file and return records list when each record is a dictionary
    """
    resultSet = []
    with open(logFile, 'r') as reader:
        lines = reader.readlines()
        columnsLine = lines[0].strip('\n\"')
        if columns is None:
            columns = columnsLine.split(',')
        for line in lines[1:]:
            if len(line) == 0 or line[0] == '\n':
                continue
            line = line.strip('\n\"')
            fields = line.split(',')
            record = {columns[i]: fields[i] for i in range(len(columns))}
            resultSet.append(record)
    return resultSet


def GenerateNowTime():
    """
    Generate and return the current time in the format YYYY-MM-DD hh:mm:ss
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def ConvertDatetime(datetimeStr: str, fromFormat: str, toFormat: str):
    """
    Convert datetime from one format to another
    """
    dt = datetime.datetime.strptime(datetimeStr, fromFormat)
    return dt.strftime(toFormat)


def ConvertDatetimeFromAMPMTo24(datetimeStr: str, fromFormat: str):
    if datetimeStr.endswith('AM'):
        return datetimeStr
    elif datetimeStr.endswith('PM'):
        dt = datetime.datetime.strptime(datetimeStr, fromFormat)
        hour = dt.hour
        hour += 12
        dt = dt.replace(hour=hour)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return datetimeStr


def ReadEventEntriesFromExcelFile(excelFilePath: str, sheetName: str):
    """
    Read event entries from excel file and sheet
    """
    df = pandas.read_excel(excelFilePath, sheet_name=sheetName)
    columnNames = list(df.keys())
    eventRecords = []
    for index in range(len(df)):
        eventRecord = {
            columnName: str(df[columnName][index])
            for columnName in columnNames
        }
        eventRecords.append(eventRecord)
    return eventRecords


def ReadConfigFile(configFilePath: str):
    """
    Read config file and return config object
    """
    config = ConfigParser()
    config.read(configFilePath)
    return config


def WriteToCsvFile(csvFile: str, records: list):
    """
    Write records to csv file
    """
    if len(records) == 0:
        return
    with open(csvFile, 'w', newline='') as file:
        header = list(records[0].keys())
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def WriteToTextFile(filePath: str, content: str):
    """
    Write to text file a given content
    """
    if len(content) == 0:
        return
    with open(
            filePath,
            'w',
    ) as writer:
        writer.write(content)


def RunExecutable(exeFile: str, args: list, shell: bool):
    """
    Run executable file with arguments
    """
    exeDir = os.path.dirname(os.path.realpath(exeFile))
    try:
        if shell:
            cmd = ' '.join([exeFile] + args)
            # process = subprocess.Popen('start cmd /K {}'.format(
            #     cmd), cwd=exeDir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False)
            process = subprocess.Popen('start cmd /K {}'.format(cmd),
                                       cwd=exeDir,
                                       shell=True)
        else:
            process = subprocess.Popen(
                [exeFile] + args,
                cwd=exeDir,
                creationflags=subprocess.DETACHED_PROCESS)
        return process
    except Exception as ex:
        print('Error in running executable: {}'.format(ex))
        return None


def ReadFileContent(file):
    content = ''
    with open(file, 'r') as reader:
        content = reader.read()
    return content


def LoadConfig():
    configParser = ConfigParser()
    configParser.read('config.ini', encoding='utf-8')
    return configParser


def LoadConfigText(configFile: str):
    config = {}
    with open(configFile, 'r') as reader:
        lines = reader.readlines()
        for line in lines:
            if '=' in line:
                line = line.strip(' \n')
                fields = line.split('=')
                key, value = fields[0], fields[1]
                config[key] = value
    return config


def InitLogger(configParser: object):
    logFolder = configParser.get('Logger', 'logfolder')
    if not os.path.exists(logFolder):
        os.makedirs(logFolder)
    logFile = configParser.get('Logger', 'logfile')
    logger = Logger('Agent', logFile)
    return logger
