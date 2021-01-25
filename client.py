import socket  # for sockets
import sys  # for exit
from threading import Thread, Event
import time
import pickle
import errno

HEADER_LENGTH = 1024
Client_ip = socket.gethostbyname(socket.gethostname())
# host = 'localhost';
host1 = '192.168.133.2'  ######Client input here
host = "192.168.2.21"
PORT = 8885
RQ = 0


def ask_name():
    while True:
        name = input("Type in your username: ")
        if name.isalpha():
            return name
        else:
            print("Please use only letters, try again")


host = input("Please enter Server IP:")
sendto = (host, PORT)
try:

    my_username = (ask_name()).lower()  # input("Username: ")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print('Socket created')

except socket.error:
    print('Failed to create socket')
    sys.exit()

while 1:

    message = input(f"{my_username} > ").lower()  # wrtie the message to send
    pickled = False
    try:
        # To Exit the messaging type exit
        if message == "exit":
            print("Connection Closed by User")
            break

        # To Register type Register
        if message == "register":
            RQ += 1
            register = {"RQ": RQ, "Action": "Register", "name": my_username}
            message = pickle.dumps(register)
            pickled = True
            print(register)

        # To Deregister type Deregister
        if message == "deregister":
            RQ += 1
            deregister = {"RQ": RQ, "Action": "Deregister", "name": my_username}
            message = pickle.dumps(deregister)
            pickled = True
            print(deregister)

        # To Update info type Update
        if message == "update":
            RQ += 1
            update = {"RQ": RQ, "Action": "Update", "name": my_username}
            message = pickle.dumps(update)
            pickled = True
            print(update)

        # To Update Subjects type Subjects
        if message == "subjects":
            RQ += 1
            subj = (input("New Subjects: ")).lower()
            subjects = {"RQ": RQ, "Action": "Subjects", "name": my_username, "subjects": subj}
            message = pickle.dumps(subjects)
            pickled = True
            print(subjects)

        # To send a message type Publish,
        # Sends a message to users in same Subject
        if message == "publish":
            RQ += 1
            subj = (input("Subject: ")).lower()
            msg = input("Message: ")
            publish = {"RQ": RQ, "Action": "Publish", "name": my_username, "subjects": subj, "message": msg}
            message = pickle.dumps(publish)
            pickled = True
            print(publish)

        if message == '':
            continue

        if message:
            if not pickled:
                print("If you want to send a Message, please use Publish")
                continue
            else:
                try:
                    # This should send to all servers the first time, then once the server responds it sets send to the server IP that responded
                    client_socket.sendto(message, sendto)

                except socket.error as msg:
                    print('Error, Server is not activated')

        # Client Recieves message
        msg = client_socket.recvfrom(HEADER_LENGTH)
        hold_string = pickle.loads(msg[0])
        print(f"Sender info: {msg[1]}")
        print(f"Server> {hold_string}")

        if hold_string.find("CHANGE-SERVER") != -1:
           holdIP = hold_string[hold_string.find("|IP:")+4:hold_string.find("|Socket")]
           holdSocket = hold_string[hold_string.find("|Socket:")+8:]
           print(holdIP, "this" , holdSocket)

           sendto = (holdIP,int(holdSocket))


    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading Error', str(e))
            sys.exit()
        continue

    except Exception as e:
        print('General error', str(e))
        sys.exit()

sys.exit()
client_socket.close()
