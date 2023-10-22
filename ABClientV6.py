import os, sys, socket, time, base64, hashlib
from datetime import date

port = 2075
ServerAddress = "000.000.000.00"
s = socket.socket()
s.bind(('',port))
utf = "utf-8"
CurrentDirectory = os.getcwd()
threads = 2

def SearchFile(Query, PathToFile):
    Query = str(Query)
    m = open(PathToFile, 'r')
    ReadoutOfInformation = m.readlines()
    HeaderFound = False
    for f in ReadoutOfInformation:
        if HeaderFound == True:
            return(f.replace('\n',''))
        if Query + '\n' == f:
            HeaderFound = True

def SendMsg(addr, message, type, *args): #address, destination, message/file, Additional optional info
    if type == "m":
        data = message.encode(encoding=utf)
        name = base64.b64encode('MSG'.encode(encoding=utf))
    elif type == "f":
        data = open(message, 'rb').read()
        MessageLength = len(message) - 1
        counter = 0
        for character in range(MessageLength):
            CurrentStringIndex = MessageLength - counter
            if message[CurrentStringIndex] == "/":
                name = base64.b64encode(message[(CurrentStringIndex + 1):].encode(utf))
                break
            counter = counter + 1

    else:
        print('Type "' + type + '" argument invalid in SendMsg, quitting...')
        quit()
    EncMessage = base64.b64encode(data)
    print(len(EncMessage))
    a = socket.socket()
    a.connect((addr, 2075))
    print("sending " + str(name) + " to: " + str(addr) + " on 2075")
    a.send((str(len(EncMessage)) + '-').encode(encoding=utf)) #Length of EncMessage
    a.send((name + "-".encode(encoding=utf))) #file or message name, uses SegmentDecode(), so does not require a precceding length
    a.send(((str(len(args)) + "-")).encode(encoding=utf)) #number of optional arguments
    for arg in args:
        print(arg)
        a.send((base64.b64encode(arg.encode(utf)) + "-".encode()))
    a.send(EncMessage) #sends the actual message as b64
    a.send('-END'.encode(encoding=utf)) #signals end of message, helps confirm correct number bytes was read
    a.close()
def RecMsg(): #Returns message, filename, address of sender and ArgInfo (A list of any extra arguments sent)

    ReconstructedMessage = []
    LengthReconstructedMessage = 0
    while True:
        s.listen(5)
        EncMessage, address = s.accept()
        def SegmentDecode(): #Decodes incoming message untill it sees a '-'
            MsgInfo = []
            while True:
                MessageSegment = EncMessage.recv(1).decode(encoding=utf)
                if MessageSegment == "-":
                    break
                else:
                    MsgInfo.append(MessageSegment)
            return ("".join(MsgInfo))
        MsgLength = SegmentDecode()
        print("Expected incoming bytes: " + str(MsgLength))
        FileName = base64.b64decode(SegmentDecode()).decode(utf)
        print("File name: " + FileName)

        if FileName == "ABSBenchMark":
            StartTime = int(time.time()) #Gets time of when transmittion starts
            print("Got time of transmittion start")

        ArgsLength = int(SegmentDecode())
        print(str(ArgsLength) + " extra arguments expected:")
        ArgInfo = []
        for item in range(ArgsLength):
            message = base64.b64decode(SegmentDecode()).decode(utf)
            #message = str(SegmentDecode())
            ArgInfo.append(message)
            print("    " + message)
        while LengthReconstructedMessage < int(MsgLength):
            print(str(LengthReconstructedMessage) + '/' + str(MsgLength), end='\r')
            if LengthReconstructedMessage == int(MsgLength):
                #print("FINAL LENGTH: " + str(LengthReconstructedMessage) + '/' + MsgLength)
                break
            elif int(MsgLength) - LengthReconstructedMessage < 4096:
                CoreSegment = EncMessage.recv(int(MsgLength) - LengthReconstructedMessage).decode(encoding=utf)
                #print(str(int(MsgLength) - LengthReconstructedMessage) + " last segment length decoded")
                ReconstructedMessage.append(CoreSegment)
                LengthReconstructedMessage = LengthReconstructedMessage + len(CoreSegment)
            else:
                CoreSegment = EncMessage.recv(4096).decode(encoding=utf)
                ReconstructedMessage.append(CoreSegment)
                #print(str(LengthReconstructedMessage) + '/' + str(MsgLength), end='\r')
                LengthReconstructedMessage = LengthReconstructedMessage + len(CoreSegment)
        MessageCore = "".join(ReconstructedMessage)
        print("FINAL LENGTH: " + str(LengthReconstructedMessage) + '/' + MsgLength)
        #print(MessageCore)
        #print(len(MessageCore))
        #print(base64.b64decode(MessageCore))
        if EncMessage.recv(4).decode(encoding=utf) == "-END":
            print("Message successfully recieved from " + str(address[0]) + " on port 2075.")
            print(MessageCore[-300:])
            print(str(len(MessageCore)) + " Length of MessageCore")

            if FileName == "ABSBenchMark":
                EndTime = int(time.time()) #Gets time of transmittion end
                print("Transmittion for ABSBenchMark file took " + EndTime-StartTime + " on ver " + cksum(sys.argv[0]))

            return base64.b64decode(MessageCore), FileName, address[0], ArgInfo
        else:
            print("Message length check failed.")
            s.close()
            quit()
def cksum(file):
    with open(file, 'rb') as f:
        hash = hashlib.sha224(f.read()).hexdigest()
        f.close()
        print(hash)
        return(hash)

f = open('/home/NAME/Documents/Comms/BackupList.txt')
BackupList = f.readlines()
f.close()
#user = os.getlogin()
if len(sys.argv) == 1:
    user = os.getlogin() + '/'
elif len(sys.argv) == 2:
    user = sys.argv[1]
elif len(sys.argv) == 3:
    user = sys.argv[1]
    BackupList = []
    BackupList.append(sys.argv[2])

#os.chdir('/home/' + user + '/share/')
#[optional[ sys.argv[1] = destination user defaults to your computer's name, [optional] sys.argv[2] = optional argument for manually passing BackupList commands.

for command in BackupList:
    StrippedCommand = str(command).replace('\n','')
    if os.path.isdir(StrippedCommand) == True:
        CommandList = []
        GazeHistory = []
        def FolderSweeper(directory, gaze=""):
            folders = []
            DirectoryList = os.listdir(directory + gaze)
            for item in DirectoryList:
                if os.path.isfile(directory + gaze + '/' + item) == True:  
                    CommandList.append(directory + gaze + '/' + item)
                    GazeHistory.append(gaze + '/')
                    print(gaze + '/' + item)
                else:
                    folders.append(item)
            for folder in folders:
                FolderSweeper(directory, gaze + '/' + folder)
        FolderSweeper(StrippedCommand)
        sync = 0
        counter = 0
        CommandLength = len(command) - 3
        print(command)
        print(CommandLength)
        for character in range(CommandLength):
            CurrentStringIndex = CommandLength - counter
            print(command[CurrentStringIndex] + " command character")
            print(str(CurrentStringIndex) + " String Index")
            if command[CurrentStringIndex] == "/":
                SourceFolder = StrippedCommand[(CurrentStringIndex + 1):].replace('/','')
                #print(SourceFolder + " SOURCE FOLDER")
                break
            counter = counter + 1
        for command in CommandList:
            print(command + " command")
            print(GazeHistory[sync] + " GazeHistory")
            print(SourceFolder.replace('/','') + " SourceFolder")
            print(user + " user")
            #user, sourcefolder and gase all include trailing slash
            Checksum = cksum(command)
            CommandLength = len(command) - 1
            counter = 0
            for character in range(CommandLength):
                CurrentStringIndex = CommandLength - counter
                print(command[CurrentStringIndex])
                if command[CurrentStringIndex] == "/":
                    FileName = command[(CurrentStringIndex + 1):]
                    break
                counter = counter + 1
            print(SourceFolder + " SourceFolder")
            print(GazeHistory[sync] + " GazeHistory[sync]")
            print(FileName + " FileName")
            #if GazeHistory[sync] ==  '/':
            #    RefinedGazeHistory = ''
            #else:
            RefinedGazeHistory = GazeHistory[sync]
            print(user + "date/" + SourceFolder.replace('/','') + RefinedGazeHistory + FileName)
            SendMsg(ServerAddress, Checksum, 'm', user, SourceFolder + RefinedGazeHistory + FileName)
            message, FileName, address, ArgInfo = RecMsg()
            if message.decode(utf) == "approved":
                SendMsg(ServerAddress, str(command), 'f', user, SourceFolder, GazeHistory[sync])
                print('\n')
                sync = sync + 1
            else:
                print(message)
                print("Server already has file, skipping... \n")
                sync = sync + 1
    else:
        #ip, message, type, user, folder

        #Getting SourceFolder
        counter = 0
        CommandLength = len(command) - 3
        for character in range(CommandLength):
            CurrentStringIndex = (CommandLength) - counter
            print(command[CurrentStringIndex] + " command character")
            print(str(CurrentStringIndex) + " String Index")
            if command[CurrentStringIndex] == "/":
                SourceFolder = StrippedCommand[(CurrentStringIndex + 1):].replace('/','')
                #print(SourceFolder + " SOURCE FOLDER")
                break
            counter = counter + 1

        #Gazehistory dosent matter as we are directly pointing to the file
        GazeHistory = ""

        #Getting cksum
        print(command + " command")
        print(GazeHistory + " GazeHistory")
        print(SourceFolder.replace('/','') + " SourceFolder")
        print(user + " user")
        #user, sourcefolder and gase all include trailing slash
        Checksum = cksum(StrippedCommand)

        #Getting FileName
        CommandLength = len(command) - 1
        counter = 0
        for character in range(CommandLength):
            CurrentStringIndex = CommandLength - counter
            print(command[CurrentStringIndex])
            if command[CurrentStringIndex] == "/":
                FileName = command[(CurrentStringIndex + 1):]
                break
            counter = counter + 1

        SendMsg(ServerAddress, Checksum, 'm', user, SourceFolder + GazeHistory + FileName)
        message, FileName, address, ArgInfo = RecMsg()
        if message.decode(utf) == "approved":
            SendMsg(ServerAddress, StrippedCommand, 'f', user + "/", "default")
