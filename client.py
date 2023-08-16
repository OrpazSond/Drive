import socket
import sys
import os
from watchdog.events import PatternMatchingEventHandler
import time
from watchdog.observers import Observer


watch = "1"
ip = sys.argv[1]
port = int(sys.argv[2])
orpaz = sys.argv[3]
packagePath = sys.argv[3]
len1 = len(packagePath)
timeToUpdate = int(sys.argv[4])
socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket1.connect((ip, port))
myNum = "0"
CHUNKSIZE = 1_000_000
if len(sys.argv) == 6:
    ID = sys.argv[5]
    socket1.send(str.encode(ID))
    time.sleep(0.1)
    myNum = socket1.recv(10)
    time.sleep(0.1)
    myNum = str(myNum, 'utf-8')

    # Make a directory for the received files.
    parent_dir = packagePath
    path = os.path.join(parent_dir, ID)
    # os.makedirs(path, exist_ok=True)
    with socket1, socket1.makefile('rb') as clientfile:
        while True:
            raw = clientfile.readline(300)
            if not raw: break  # no more files, server closed connection.

            filename = raw.strip().decode()
            length = int(clientfile.readline())

            path2 = os.path.join(parent_dir, filename)
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
                    continue

            break

else:
    myNum = "1"
    socket1.send(str.encode("new client"))
    time.sleep(0.1)
    ID = socket1.recv(128)
    s = 5
    parent_dir = packagePath
    # path = os.path.join(parent_dir, 'newID')
    with socket1:
        for path, dirs, files in os.walk(packagePath):
            for file in files:
                filename = os.path.join(path, file)
                # relpath = os.path.relpath(filename, '/home/orpaz/CLionProjects/abc')
                relpath = os.path.relpath(filename, packagePath)
                filesize = os.path.getsize(filename)

                with open(filename, 'rb') as f:
                    socket1.sendall(relpath.encode() + b'\n')
                    time.sleep(0.1)
                    socket1.sendall(str(filesize).encode() + b'\n')
                    time.sleep(0.1)
                    # Send the file in chunks so large files can be handled.
                    while True:
                        data = f.read(CHUNKSIZE)
                        if not data: break
                        socket1.sendall(data)
                        time.sleep(0.1)
    socket1.close()

socket1.close()

patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
myList = []
dict = {
    "created": "",
    "deleted": "",
    "modified": "",
    "moved": ("", "")

}


def on_created(event):
    if watch == "1":
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((ip, port))
        if (os.path.isfile(event.src_path)):
            soc.send(str.encode("create"))
            soc.recv(3)
            time.sleep(0.1)

            if (type(ID) == str):
                soc.send(str.encode(ID))
            else:
                soc.send(ID)
            time.sleep(0.1)

            soc.send(str.encode(str(myNum)))
            time.sleep(0.1)
            create(soc, event.src_path)

        else:
            soc.send(str.encode("createDirectory"))
            time.sleep(0.1)
            soc.recv(3)
            time.sleep(0.1)
            if (type(ID) == str):
                soc.send(str.encode(ID))
            else:
                soc.send(ID)
            time.sleep(0.1)

            soc.send(str.encode(str(myNum)))
            time.sleep(0.1)
            createDirectory(soc, event.src_path)
        time.sleep(0.01)

        soc.close()

def on_deleted(event):
    if watch == "1":
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((ip, port))

        delete(soc, event)

        soc.send(str.encode(str(myNum)))
        time.sleep(0.1)
        soc.close()

def on_modified(event):
    if watch == "1":
        myList.append("modified")
        myList.append(event.src_path[len1 + 1:])
        dict["modified"] = event.src_path
        if (os.path.isfile(event.src_path)):
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((ip, port))

            soc.send(str.encode("update"))
            soc.recv(3)
            time.sleep(0.1)
            if (type(ID) == str):
                soc.send(str.encode(ID))
            else:
                soc.send(ID)
            time.sleep(0.1)
            soc.send(str.encode(str(myNum)))
            time.sleep(0.1)
            soc.send(str.encode(event.src_path[len1 + 1:]))
            time.sleep(0.1)
            f = open(event.src_path, "rb")
            l = f.read(1024)
            while (l):
                soc.send(l)
                l = f.read(1024)
            f.close()

            time.sleep(0.1)
            soc.close()


def on_moved(event):
    if watch == "1":
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((ip, port))

        if (os.path.isfile(event.dest_path)):
            soc.send(str.encode("create"))

            time.sleep(0.1)
            if (type(ID) == str):
                soc.send(str.encode(ID))

            else:
                soc.send(ID)
            time.sleep(0.1)

            soc.send(str.encode(str(myNum)))
            time.sleep(0.1)
            create(soc, event.dest_path)

            soc.close()
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((ip, port))
            delete(soc, event)

            soc.send(str.encode(str(myNum)))
            soc.close()
        else:
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((ip, port))
            soc.send(str.encode("createDirectory"))
            soc.recv(3)
            time.sleep(0.1)

            time.sleep(0.1)
            if (type(ID) == str):
                soc.send(str.encode(ID))
            else:
                soc.send(ID)
            time.sleep(0.1)

            soc.send(str.encode(str(myNum)))
            time.sleep(0.1)
            createDirectory(soc, event.dest_path)
            soc.send(str.encode(str(myNum)))
            time.sleep(0.1)
            soc.close()
            soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            soc.connect((ip, port))
            delete(soc, event)

            time.sleep(0.1)

            soc.close()


def createDirectory(soc, path):
    soc.send(str.encode(path[len1 + 1:]))
    time.sleep(0.1)

    # soc.send(str.encode("off"))
    time.sleep(0.05)


def create(soc, path):
    soc.send(str.encode(path[len1 + 1:]))
    time.sleep(0.1)

    soc.send(str.encode("1"))
    time.sleep(0.05)

    f = open(path, "rb")
    l = f.read(1024)
    while (l):
        soc.send(l)
        time.sleep(0.05)
        l = f.read(1024)
    f.close()
    time.sleep(0.1)


def delete(soc, event):
    soc.send(str.encode("delete"))
    soc.recv(3)
    time.sleep(0.1)
    if (type(ID) == str):
        soc.send(str.encode(ID))
    else:
        soc.send(ID)
    time.sleep(0.1)
    soc.send(str.encode(event.src_path[len1 + 1:]))
    time.sleep(0.1)


# my_event_handler.on_any_event = on_any_event
my_event_handler.on_created = on_created
my_event_handler.on_deleted = on_deleted
my_event_handler.on_modified = on_modified
my_event_handler.on_moved = on_moved

path = packagePath
go_recursively = True
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=go_recursively)

my_observer.start()

def deleteDirectory(path):
    for file in os.listdir(path):
        currenFilePath = path + '/' + file
        if (os.path.isfile(currenFilePath)):
            os.remove(currenFilePath)
        else:
            deleteDirectory(currenFilePath)
            os.rmdir(currenFilePath)

def d(soc, changePath):
    soc.send(b'2')

    ID = soc.recv(128)
    ID = str(ID, 'utf-8')

    relativePath = soc.recv(500)
    relativePath = str(relativePath, 'utf-8')
    clientPath = relativePath
    if (os.path.exists(changePath)):
        if (os.path.isfile(changePath)):
            os.remove(changePath)
        else:
            deleteDirectory(changePath)
            os.rmdir(changePath)

    seqNum = str(soc.recv(3),  'utf-8')

def createFile1(clientPath, client):

    flag = client.recv(10)
    flag = str(flag, 'utf-8')

    if (flag == "1"):
        f = open(clientPath, 'w')  # Open in binary
        while (True):

            # We receive and write to the file.
            l = client.recv(1024)
            while (l):
                f.write(str(l, 'utf-8'))
                l = client.recv(1024)
            f.close()
            break

def c(soc, changePath):

    createFile1(changePath, soc)

def C(soc, changePath):

    path = changePath
    os.mkdir(path)

try:
    while True:
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.connect((ip, port))
        time.sleep(0.1)
        soc.send(str.encode("changes"))
        time.sleep(0.1)
        soc.recv(3)
        time.sleep(0.1)

        if (type(ID) == str):
            soc.send(str.encode(ID))
        else:
            soc.send(ID)
        time.sleep(0.1)

        soc.send(str.encode(str(myNum)))
        time.sleep(0.1)

        length = soc.recv(4)
        length = str(length, 'utf-8')
        length = int(length)

        watch = "0"
        if length != 0:
            try:
                for i in range(length):
                    theChange = soc.recv(300)
                    theChange = str(theChange, 'utf-8')
                    sign = theChange[0]
                    thePath = theChange[1:]
                    changePath = os.path.join(orpaz, thePath)

                    if sign == 'd':

                        d(soc, changePath)

                    if sign == 'c':
                        c(soc, changePath)

                    if sign == 'C':
                        C(soc, changePath)
            except:
                pass


        soc.close()
        watch = "1"
        time.sleep(timeToUpdate)

except KeyboardInterrupt:
    my_observer.stop()
    my_observer.join()

