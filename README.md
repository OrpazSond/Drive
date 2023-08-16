# Drive

This project was coded using a single thread in Python on top of TCP protocol. The service support Linux.

- Cloud files backup services usually offer customers the option to download client software to the computer which allows them to select a folder on the computer and synchronize it automatically with the server at any change and between different computers.
- When the software is run and a folder is set up from the computer, the software uploads to the server all the files in the folder for backup and from now on the software monitors any change that takes place in the folder deeply. When such a change is detected, the software updates the server about the change so that the backup on the server will be updated accordingly.
- The software also knows to receive updates about changes that have occurred on other users' computers. That is, if the user installed the software on another computer, he selected an empty folder on the additional computer - to which the software downloads all the contents of the folder from the server, and then, as before, the software monitors the folder for any changes and updates the server.
- The client must keep the ID that the server gave him - and in any future contact he must identify himself with the help of the ID. The client then continues to monitor the folder and synchronize with the server. Any changes made to a folder on one computer will be synchronized with the server precisely and with the other computers of the same client.
- The server knows how to handle several different clients - whether they belong to the same user (same ID) or different users (different ID's) and knows how to synchronize any change in folders.
