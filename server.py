import socket
import sys
import random
import os
import string
import time

def create(soc1, path):

    soc1.send(str.encode("1"))
    time.sleep(0.05)

    f = open(path, "rb")
    l = f.read(1024)
    while (l):
        soc1.send(l)
        time.sleep(0.05)
        l = f.read(1024)
    f.close()
    time.sleep(0.1)
    soc1.close()


def createDirectory1(soc, path):

    time.sleep(0.1)

    # soc.send(str.encode("off"))
    time.sleep(0.05)
    soc.close()

def on_created(changePath, soc):
    if (os.path.isfile(changePath)):
        time.sleep(0.1)

        create(soc, changePath)

    else:
        time.sleep(0.1)
        createDirectory1(soc, changePath)
    time.sleep(0.01)



def on_deleted(soc1, event, changePath):
    delete(soc1, event, changePath)

    time.sleep(0.1)
    soc1.close()

def delete(soc, event, changePath):
    soc.recv(3)
    time.sleep(0.1)
    if (type(ID) == str):
        soc.send(str.encode(ID))
    else:
        soc.send(ID)
    time.sleep(0.1)
    soc.send(str.encode(changePath))
    time.sleep(0.1)

def updateList(ID, sequence_number, change, path):
    path_change = change + path
    dict_Id = dictID[ID]
    for seq_num in dict_Id:
        if str(seq_num) != str(sequence_number):
            dict_Id[seq_num].append(path_change)
    dictID[ID] = dict_Id

CHUNKSIZE = 1_000_000
dictID = {}


def createFile(ID, clientPath, client):

    flag = client.recv(10)
    flag = str(flag, 'utf-8')
    if (flag == "1"):
        f = open(ID + '/' + clientPath, 'w')  # Open in binary
        while (True):

            # We receive and write to the file.
            l = client.recv(1024)
            while (l):
                f.write(str(l, 'utf-8'))
                l = client.recv(1024)
            f.close()
            break


def createDirectory(client, path,ID):
    os.mkdir(ID + '/' + path)
    for file in os.listdir(ID + '/' + path):
        currenFilePath = path + '/' + file
        if (os.path.isfile(currenFilePath)):
            createFile(ID,client,currenFilePath)
        else:
            os.mkdir(currenFilePath)
            createDirectory(client,currenFilePath,ID)

def deleteDirectory(path):
    for file in os.listdir(path):
        currenFilePath = path + '/' + file
        if (os.path.isfile(currenFilePath)):
            os.remove(currenFilePath)
        else:
            deleteDirectory(currenFilePath)
            os.rmdir(currenFilePath)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])
sock.bind(('', port))
sock.listen(1)
while True:
    client, address = sock.accept()
    clientMessage = client.recv(535)
    clientMessage = str(clientMessage, 'utf-8')

    s = 123

    if len(clientMessage) >= 128:

        theNum = len(dictID[clientMessage]) + 1
        dictID[clientMessage][theNum] = []

        time.sleep(0.1)
        client.send(str.encode(str(theNum)))
        time.sleep(0.1)

        with client:
            # for path, dirs, files in os.walk('/home/orpaz/CLionProjects/abc'):
            for path, dirs, files in os.walk(os.path.abspath(os.getcwd()) + '/' + clientMessage + '/'):
                for file in files:
                    filename = os.path.join(path, file)
                    # relpath = os.path.relpath(filename, '/home/orpaz/CLionProjects/abc')
                    relpath = os.path.relpath(filename, os.path.abspath(os.getcwd()) + '/' + clientMessage + '/')
                    filesize = os.path.getsize(filename)

                    time.sleep(0.1)
                    with open(filename, 'rb') as f:
                        client.sendall(relpath.encode() + b'\n')
                        time.sleep(0.1)
                        client.sendall(str(filesize).encode() + b'\n')
                        time.sleep(0.1)
                        # Send the file in chunks so large files can be handled.
                        while True:
                            data = f.read(CHUNKSIZE)
                            if not data: break
                            client.sendall(data)
            client.close()
    if clientMessage == "new client":
        id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(128))
        print(id)
        ID = str.encode(id)
        dictID[id] = {1: []}
        time.sleep(0.1)
        client.send(ID)
        time.sleep(0.1)
        os.makedirs(os.path.abspath(os.getcwd() + '/' + id), exist_ok=True)
        with client, client.makefile('rb') as clientfile:
            while True:
                raw = clientfile.readline()
                if not raw: break  # no more files, server closed connection.

                filename = raw.strip().decode()
                length = int(clientfile.readline())

                path2 = os.path.join(os.path.abspath(os.getcwd() + '/' + id), filename)
                os.makedirs(os.path.dirname(path2), exist_ok=True)

                # Read the data in chunks so it can handle large files.
                with open(path2, 'wb') as f:
                    while length:
                        chunk = min(length, CHUNKSIZE)
                        data = clientfile.read(chunk)
                        if not data: break
                        f.write(data)
                        length -= len(data)
                    else:  # only runs if while doesn't break and length==0
                        client.close()
                        continue

                # socket was closed early.
                break

    if clientMessage == "update":
        client.send(b'2')
        ID = client.recv(128)
        ID = str(ID, 'utf-8')

        seqNum = str(client.recv(3), 'utf-8')

        clientPath = client.recv(500)
        clientPath = str(clientPath, 'utf-8')

        os.remove(ID + '/' + clientPath)

        f = open(ID + '/' + clientPath, 'w')  # Open in binary
        while (True):

            # We receive and write to the file.
            l = client.recv(1024)
            while (l):
                f.write(str(l, 'utf-8'))
                l = client.recv(1024)
            f.close()
            break


        updateList(ID, seqNum, "u", clientPath)

    if clientMessage == "delete":
        client.send(b'2')

        ID = client.recv(128)
        ID = str(ID, 'utf-8')

        relativePath = client.recv(500)
        relativePath = str(relativePath, 'utf-8')
        clientPath = ID + '/' + relativePath

        if (os.path.exists(clientPath)):
            if (os.path.isfile(clientPath)):
                os.remove(clientPath)
            else:
                deleteDirectory(clientPath)
                os.rmdir(clientPath)

        seqNum = str(client.recv(3),  'utf-8')
        updateList(ID, seqNum, "d", relativePath)


    if clientMessage == "create":
        client.send(b'2')
        ID = client.recv(128)
        ID = str(ID, 'utf-8')

        seqNum = str(client.recv(3), 'utf-8')

        clientPath = client.recv(500)
        clientPath = str(clientPath, 'utf-8')
        createFile(ID, clientPath, client)

        updateList(ID, seqNum, "c", clientPath)

    if clientMessage == "createDirectory":
        client.send(b'2')

        ID = client.recv(128)
        ID = str(ID, 'utf-8')

        seqNum = str(client.recv(3), 'utf-8')

        clientPath = client.recv(500)
        clientPath = str(clientPath, 'utf-8')
        path = ID + '/' + clientPath
        os.mkdir(path)


        updateList(ID, seqNum, "C", clientPath)

    if clientMessage == "changes":
        client.send(str.encode("2"))
        ID = client.recv(128)
        ID = str(ID, 'utf-8')

        seq = str(client.recv(3), 'utf-8')
        time.sleep(0.1)
        seq = int(seq)

        dict_Id = dictID[ID][seq]
        length = len(dict_Id)

        time.sleep(0.1)

        client.send(str.encode(str(length)))

        for change in dict_Id:
            time.sleep(0.1)
            try:
                client.send(str.encode(change))
            except:
                pass

            sign = change[0]
            thePath = change[1:]
            path1 = os.path.split(sys.argv[0])[0]
            changePath = os.path.join(path1, ID, thePath)

            if sign == 'd':
                on_deleted(client, changePath, changePath)

            try:
                if sign == 'c':
                    on_created(changePath, client)
            except:
                pass

            try:
                if sign == 'C':
                    on_created(changePath, client)
            except:
                pass

            try:
                dictID[ID][seq].remove(change)
            except:
                pass




