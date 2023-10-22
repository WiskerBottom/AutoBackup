import socket, os, sys, time, base64, threading, hashlib
from datetime import date
#from time import time

def NetworkCheck(Gateway):
    response = os.system("ping -c 1 " + Gateway)
    if response == 0:
        return True
    else:
        return False

#When starting from systemctl it errors out at os.getlogin() even though I have it running under charlotte's user and group
#host = os.getlogin()
host = "NAME"
port = 2075
ServerAddress = "000.000.000.000"
s = socket.socket()
while True:
    if NetworkCheck('192.168.86.1') == True:
        s.bind((ServerAddress,port))
        break
    else:
        print("Failed to bind to " + ServerAddress + ":2075")
        time.sleep(10)
utf = "utf-8"
os.chdir('/home/' + host + '/Documents/Programs/Python/AutoBackup/')

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
            StartTime = int(time() * 1000) #Gets time of when transmittion starts

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
            #print(MessageCore[-300:])
            #print(str(len(MessageCore)) + " Length of MessageCore") 

            if FileName == "ABSBenchMark":
                EndTime = int(time() * 1000) #Gets time of transmittion end
                print("Transmittion for ABSBenchMark file took " + str(EndTime-StartTime) + " milliseconds on version (cksum) " + str(cksum(sys.argv[0])))


            return base64.b64decode(MessageCore), FileName, address[0], ArgInfo
        else:
            print("Message length check failed.")
            s.close()
            quit()

def cksum(file):
        try:
            with open(file, 'rb') as f:
                hash = hashlib.sha224(f.read()).hexdigest()
                f.close()
                return(hash)
        except:
            return(0)

AutoBackupPath = '/home/' + host + '/Toshiba3TB/AutoBackup/'

#ChecksumMaintenance = threading.Thread(target=ChecksumUpdate, args=('/home/charlotte/Toshiba3TB/AutoBackup/',))
#ChecksumMaintenance.start()

#f = open('/home/' + host + '/Documents/Programs/AutoBackup/SSHFSList.txt')
#for line in f.readlines():
#    x = open('/etc/mtab', 'r')
#    #print(line.replace('\n', ''))
#    os.system('sshfs ' + AutoBackupPath + " " + line)

#quit()

while True:
    message, FileName, address, ArgInfo = RecMsg()
    #Checksum, 'MSG', address of sender, username of sender, name of file corresponding to sent checksum
    if FileName == "MSG":
        IncomingChecksum = message.decode()
        print(cksum(AutoBackupPath + ArgInfo[0] + str(date.today()) + '/' + ArgInfo[1]))
        print(IncomingChecksum)
        if IncomingChecksum == cksum(AutoBackupPath + ArgInfo[0] + str(date.today()) + '/' + ArgInfo[1]):
            SendMsg(address, "denied", "m")
            print("Request Denied")
        else:
            SendMsg(address, "approved", "m")
            status = "approved"
            print("Request Approved")
            message, FileName, address, ArgInfo = RecMsg()
            username = ArgInfo[0]
            destination = ArgInfo[1]
            if len(ArgInfo) >= 3:
                SubFolder = ArgInfo[2]
            else:
                SubFolder = ""
            if destination == "default":
                destination = str(date.today()) + '/'
            else:
                destination = str(date.today()) + '/' + destination
            SentPath = (username + destination + SubFolder).replace('\n','')
            print(SentPath.replace('\n',''))
            tolerance = 0
            occurrence = 0
            def DirectoryForge(DesiredPath, tolerance=0, occurrence=0):
                occurence = 0
                PathLength = len(DesiredPath) #As range stops before the number it is reaching the -1 is not required
                #print(str(PathLength) + " Path Length")
                for character in range(PathLength):
                    #print(character)
                    if DesiredPath[character] == "/":
                        #print(DesiredPath[character])
                        if occurrence == tolerance:
                            #print("Tolerance increased " + str(character))
                            PathSegment = DesiredPath[:character]
                            tolerance = tolerance + 1
                            break
                        else:
                            print("occurence increased "  + str(character))
                            occurrence = occurrence + 1
                #print(PathSegment + " Path Segment")
                #print(AutoBackupPath + DesiredPath)
                if os.path.isdir(AutoBackupPath + DesiredPath) == True:
                    print("Directroy Forge Finished")
                    return()
                elif os.path.isdir(AutoBackupPath + PathSegment) == True:
                    #print("elif")
                    #print("Tolerance: " + str(tolerance))
                    #print("Occerance: " + str(occurrence))
                    DirectoryForge(DesiredPath, tolerance)
                else:
                    #print("else")
                    #print("Tolerance: " + str(tolerance))
                    #print("Occerance: " + str(occurrence))
                    os.mkdir(AutoBackupPath + PathSegment)
                    DirectoryForge(DesiredPath, tolerance)
            DirectoryForge(SentPath)
            f = open(AutoBackupPath + username + destination + SubFolder + FileName.replace('\n',''), 'wb')
            f.write(message)
            print("Message from " + username.replace('/','') + " written at " + username + destination + SubFolder + ".")
    else:
        print("Expected MSG for checksum, got " + FileName)
        quit()
        
    
