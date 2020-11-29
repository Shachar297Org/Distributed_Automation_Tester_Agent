import os
from sql import *
from utils import *
from record import *


def GetEntriesByDeviceAndEvent(dbConn: object, deviceType: str, serialNumber: str, entryKey: str, entryValue: str):
    """
    Return all entries related to device type, device serial number, entry key and entry value
    """
    tableName = '.'.join([dbConn.db, 'ProcessingData'])
    query = "select * from {} where deviceType='{}' and deviceSerialNumber='{}' and entryKey='{}' and entryValue='{}'".format(
        tableName, deviceType, serialNumber, entryKey, entryValue)
    resultsSet = dbConn.ExecuteQuery(tableName, query)
    return resultsSet


def GetAllDeviceEntries(dbConn: object, deviceType: str, deviceSerialNumber: str):
    """
    Return all entries related to device type and device serial number
    """
    tableName = '.'.join([dbConn.db, 'ProcessingData'])
    query = "select * from {} where deviceType='{}' and deviceSerialNumber='{}'".format(
        tableName, deviceType, deviceSerialNumber)
    resultsSet = dbConn.ExecuteQuery(tableName, query)
    return resultsSet


def GetKRecentDeviceEntries(dbConn: object, deviceType: str, deviceSerialNumber: str, k: int):
    """
    Return most k recent entries related to device type and device serial number
    """
    tableName = '.'.join([dbConn.db, 'ProcessingData'])
    query = "select * from {} where deviceType='{}' and deviceSerialNumber='{}' order by entryTimeStamp limit {}".format(
        tableName, deviceType, deviceSerialNumber, k)
    resultsSet = dbConn.ExecuteQuery(tableName, query)
    return resultsSet


def ConvertEntryToRecord(entry: object):
    """
    Convert entry with all fields from RDS to record with 5 relevant fields
    """
    deviceType = entry['deviceType']
    serialNum = entry['deviceSerialNumber']
    entryKey = entry['entryKey']
    entryValue = entry['entryValue']
    entryTimeStamp = str(entry['entryTimeStamp'])
    return Record(deviceType, serialNum, entryKey, entryValue, entryTimeStamp)


def ParseLogFileToRecords(logFile: str):
    """
    Parse log file to list of records
    """
    entries = ReadLogFile(logFile)
    records = []
    for entry in entries:
        record = ConvertEntryToRecord(entry)
        records.append(record)
    return records


def RetrieveEntriesByDevice(deviceType: str, serialNum: str, limit: int):
    dbConn = None
    try:
        config = ReadConfigFile('_Config/config.ini')
        host = config['RDSConnection']['host']
        db = config['RDSConnection']['db']
        username = config['RDSConnection']['username']
        password = config['RDSConnection']['password']
        dbConn = DbConnector(host, db, username, password)
    except Exception as ex:
        print(ex)
        return None

    resultsSet = GetKRecentDeviceEntries(dbConn, deviceType, serialNum, limit)
    records = []
    for entry in resultsSet:
        print(entry)
        record = ConvertEntryToRecord(entry)
        records.append(record)
    return records


def ConnectRDS(host: str, db: str, username: str, password: str):
    """
    Connect to RDS and return connection object
    """
    dbConn = None
    try:
        dbConn = DbConnector(host, db, username, password)
        if dbConn:
            return dbConn
        else:
            return None
    except Exception as ex:
        print(ex)
        return None


def SearchRecordInRDS(dbConn: object, record: object):
    """
    Search record in RDS by its hash value (unique key)
    """
    if not dbConn:
        return False

    print(record)
    uniqueValue = record.Hash()
    print('Unique value: {}'.format(uniqueValue))
    deviceType = record.GetDeviceType()
    serialNumber = record.GetSerialNum()
    entryKey = record.GetEntryKey()
    entryValue = record.GetEntryValue()
    entryTimeStamp = record.GetEntryTimeStamp()
    entries = GetEntriesByDeviceAndEvent(
        dbConn, deviceType, serialNumber, entryKey, entryValue)
    print('Entries from RDS: {}'.format(len(entries)))

    for entry in entries:
        rec = ConvertEntryToRecord(entry)
        recHashValue = rec.Hash()
        if recHashValue == uniqueValue:
            return True
    return False


def RunComparison(configFilePath: str):
    print('Test arguments:')
    print('Config file path: {}'.format(configFilePath))

    config = ReadConfigFile(configFilePath)
    host = config['RDSConnection']['host']
    db = config['RDSConnection']['db']
    username = config['RDSConnection']['username']
    password = config['RDSConnection']['password']
    logFolder = config['log']['logFolder']
    csvFolder = config['csv']['csvFolder']
    print('Config file was loaded.')

    dbConn = ConnectRDS(host, db, username, password)

    if not dbConn:
        print('Cannot connect to RDS.')
        return
    print('Connected to RDS.')

    if not os.path.exists(logFolder):
        print('Error: no such folder {}'.format(logFolder))
        return

    if not os.path.exists(csvFolder):
        os.mkdir(csvFolder)

    logFiles = [os.path.join(logFolder, filename)
                for filename in os.listdir(logFolder)]

    notReceivedRecords = []
    for logFile in logFiles:
        print('Load records from log file: {}'.format(logFile))
        records = ParseLogFileToRecords(logFile)
        received = 0
        for record in records:
            result = SearchRecordInRDS(dbConn, record)
            print(result)
            if result:
                received += 1
            else:
                notReceivedRecords.append(record.ToDict())
        print('Sent events: {}'.format(len(records)))
        print('Received events: {}'.format(received))
    nowTime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csvFile = os.path.join(csvFolder, nowTime)
    WriteToCsvFile(csvFile, notReceivedRecords)


###########
# Tests
###########


def TestDatabase():
    config = ReadConfigFile('_Config/config.ini')
    host = config['RDSConnection']['host']
    db = config['RDSConnection']['db']
    username = config['RDSConnection']['username']
    password = config['RDSConnection']['password']
    dbConn = DbConnector(host, db, username, password)
    print(dbConn)
    print(dbConn.GetDatabses())

    tableName = '.'.join([dbConn.db, 'ProcessingData'])
    columns = dbConn.GetColumns(tableName)
    print(columns)

    tableName = '.'.join([dbConn.db, 'ProcessingData'])
    query = "select * from Processing.ProcessingData limit 10"
    resultsSet = dbConn.ExecuteQuery(tableName, query)
    for row in resultsSet[:3]:
        print(row)


def TestDataRetrive():
    dbConn = None
    try:
        config = ReadConfigFile('_Config/config.ini')
        host = config['RDSConnection']['host']
        db = config['RDSConnection']['db']
        username = config['RDSConnection']['username']
        password = config['RDSConnection']['password']
        dbConn = DbConnector(host, db, username, password)
    except Exception as ex:
        print(ex)
        return None

    resultsSet = GetKRecentDeviceEntries(dbConn, 'GA-0005200', '444', 5)
    print('#Records: {}'.format(len(resultsSet)))
    for record in resultsSet:
        print(record)

    logFile = 'C:/Temp/ClientWPF_Tester.2020_09_02_14_53 - Copy.lumenis'
    records = ReadLogFile(logFile)
    for record in records:
        print(record)


def TestParseLogFileToRecords(logFile: str):
    print('Log File: {}'.format(logFile))
    records = ParseLogFileToRecords(logFile)
    for record in records:
        print(record)
        print(record.Hash())


def TestRetrieveDataFromRDS():
    records = RetrieveEntriesByDevice('GA-0005200', '444', limit=5)
    for record in records:
        print(record)
        print(record.Hash())


if __name__ == "__main__":
    config = ReadConfigFile('_Config/config.ini')
    host = config['RDSConnection']['host']
    db = config['RDSConnection']['db']
    username = config['RDSConnection']['username']
    password = config['RDSConnection']['password']
    logfile = config['log']['logfiles']

    TestDatabase()
    # TestDataRetrive()
    # TestParseLogFileToRecords(logfile)
    # TestRetrieveDataFromRDS()
