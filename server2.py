import socket
import sys
import time
import threading
import pickle
import select

HOST_ipS2 = socket.gethostbyname(socket.gethostname())

#Sherby, put your IP address in HOST_ipS1 to make it work
HOST_ipS1= "10.0.0.240" #For testing purposes, will be deleted
#HOST_ipS1= input("Enter IP of Server 1: ")
PORT = 8889  # Port for client to connect
PORT1 = 8891  # Port for server to connect
HEADER_LENGTH = 1024
server1Port = 8890

# variable shared by all threads
socket_client: socket = None
# closeClientSocket: bool = None
serverOff = False
server2address = None
message2 = None

def reply_client(socket, message, addr_client):
    reply_client = pickle.dumps(message)
    try:
        socket.sendto(reply_client, addr_client)
    except socket.error as reply_client:
        print("Server2 Cannot send response to client \n")


def send_message_client_to_server(socket, addr_client):
    global message2
    print(message2)
    reply_client = message2
    try:
        socket.sendto(reply_client, addr_client)
    except socket.error as reply_client:
        print("Server 2 cannot send client response to server 1 \n")

def recieve_message2(client_socket):
    try:
        print('recv  meaage 2 2 2 2')


        print('testing server 2 extraaa')
        message, ip = client_socket.recvfrom(HEADER_LENGTH)


        #print(ip)

        # if not len(message_header[0]):
        #    return False

        # message_length = int(message_header[0].decode("utf-8").strip())
        # message = client_socket.recvfrom(message_length)
        unpickle = pickle.loads(message)
        #print(unpickle)
        # print({"Action": unpickle['Action'], "data": unpickle['name'], "ip": unpickle['ip'],"socket": unpickle['Socket']})
        return { "message": unpickle}

    except:
        return False

def recieve_message(client_socket):
    global message2
    try:
        print('recv message')


        print('testing server 2')
        message, ip = client_socket.recvfrom(HEADER_LENGTH)
        message2 = message
        print(ip)
        unpickle = pickle.loads(message)
        print(unpickle)
        return {"IP": ip, "message": unpickle}

    except:
        return False


# server 2 to communicate with server 1
def server_to_server(lock):
    #  global closeClientSocket
    global socket_client
    global serverOff
    socket_server1 = None
    # Create and bind socket with server 2
    try:
        socket_server1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket created : S2-S1 \n")
        socket_server1.bind((HOST_ipS2, PORT1))
        print("Socket bind complete : S2-S1 \n")
        print("Checking if server 1 is running")
        reply = "are you running?"
        socket_server1.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))


    except socket.error as msgS2:
        print("Failed to create socket or bind socket. Error Code : " + str(msgS2) + " Message " + msgS2)

    # Reveiving message from server 2
    while 1:

        ds1 = socket_server1.recvfrom(1024)
        messageS1 = ds1[0]
        addr_server1 = ds1[1]
        print("server 1 sent: " + str(messageS1.decode('utf-8')))
        if not messageS1:
            break

        svrmsg = messageS1.decode('utf-8')
        # If server 2 asks to sleep, server 1 will shutdown
        if svrmsg == "yes" :
           serverOff = True

        else:
            print("server 2 is serving")
            endTime = time.time() + 25  # * 15    #15 means 15 minutes therefore for us we need to put it to 5
            count = 0  # this was just to test
            while time.time() < endTime:  # timer for server can catch updates on clients and server while not serving
                '''do whatever you do'''
            reply = "You take over"
            socket_server1.sendto(bytes(reply, 'utf-8'), addr_server1)
            serverOff = True


        if serverOff == True:
            reply = "Alright, be back in 15 seconds"
            socket_server1.sendto(bytes(reply, 'utf-8'), addr_server1)
            print("Server 2 is not serving")
            endTime = time.time() + 25  # * 15    #15 means 15 minutes therefore for us we need to put it to 5
            count = 0  # this was just to test
            while time.time() < endTime:  # timer for server can catch updates on clients and server while not serving
                endTime2 = time.time() + 2
                while time.time() < endTime2:

                    if time.time() >= endTime2 or time.time() >= endTime:
                        break

                    ds1 = socket_server1.recvfrom(1024)
                    messageS1 = ds1[0]
                    addr_server2 = ds1[1]

                    if messageS1.decode('utf-8') == "You take over":
                        break;

                    if messageS1.decode('utf-8') == "Client info":
                        ds1 = socket_server1.recvfrom(1024)
                        messageS1 = ds1[0]
                        addr_server2 = ds1[1]
                        if messageS1.decode('utf-8') == "REGISTERED":
                            message = recieve_message(socket_server1)
                            # code for server receiving info on client form other server while not serving
                            print(f"Recieved message from {message['message']['name']}: {message['message']}")
                            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"
                            if message['message']['Action'] == 'Register':
                                # Validate if name is already in use
                                userIsRegistered = False
                                with open("Datebase_Server2.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server2.txt", "w") as f:
                                    for line in lines:
                                        if f"{message['message']['name']}:" in line:
                                            userIsRegistered = True
                                        f.write(line)
                                    # Send Acceptance of Registration
                                    # reply_client(server_socket, msg, message['IP'])
                                    # Add message to database
                                writeFile = open('Datebase_Server2.txt', 'a')
                                # currently using client_address & socket instead of info sent by client
                                writeFile.write(reusedStr + '\n')
                                writeFile.close()
                                # Print action to console
                                msg = f"{message['message']['name']} is now registered"
                                print(msg)
                         #server to server DEREGISTER
                        if messageS1.decode('utf-8') == "deregistered":
                            message = recieve_message(socket_server1)
                            if message['message']['Action'] == 'Deregister':
                                # Remove message to database
                                inDatabase = False
                                with open("Datebase_Server2.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server2.txt", "w") as f:
                                    for line in lines:
                                        if f"{message['message']['name']}:" in line:
                                            pass
                                            # print(f"Removed {line}")
                                        else:
                                            f.write(line)
                                            inDatabase = True

                        # server to server UPDATE CLIENT INFO
                        if messageS1.decode('utf-8') == "UPDATE-CONFIRMED:":
                            message = recieve_message(socket_server1)
                            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"
                            if message['message']['Action'] == 'Update':
                                isUpdated = False
                                # Update info on database
                                with open("Datebase_Server2.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server2.txt", "w") as f:
                                    for line in lines:
                                        if f"{message['message']['name']}:" in line:
                                            if line.find("Subjects") == -1:
                                                f.write(reusedStr + '\n')
                                                print("Old info was " + line.strip(
                                                    message['message']['name']))
                                                print("Updated Info is " + reusedStr)
                                            else:
                                                strHolder = line[line.find(", Subjects"):]
                                                print(strHolder)
                                                f.write(reusedStr + strHolder)
                                                print("Old info was " + line.strip(
                                                    message['message']['name']))
                                                print("Updated Info is " + reusedStr + strHolder)

                                            isUpdated = True
                                        else:
                                            f.write(line)

                        # server to server UPDATE SUBJECTS
                        if messageS1.decode('utf-8') == "SUBJECT-UPDATED:":
                            message = recieve_message(socket_server1)
                            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"
                            if message['message']['Action'] == 'Subjects':
                                subjectsUpdated = False
                                # Update info on database
                                with open("Datebase_Server2.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server2.txt", "w") as f:
                                    for line in lines:
                                        if f"{message['message']['name']}:" in line:
                                            if line.find("Subjects") == -1:
                                                f.write(
                                                    reusedStr + f", Subjects:{message['message']['subjects']} \n")
                                                subjectsUpdated = True
                                            else:
                                                f.write(
                                                    reusedStr + f", Subjects:{message['message']['subjects']} \n")
                                                print(
                                                    f"Old Subjects are {line.strip(message['message']['name'])}")
                                                print(
                                                    f"Updated Subjects are {message['message']['subjects']}")
                                                subjectsUpdated = True
                                        else:
                                            f.write(line)
                                            # print(f'Write {line}')
                                continue
                            else:
                                continue
            #serverOff = False





        # reply_server1 = str("sever 2 is sending message")
        # send reply to server 2 (if not shutdown)



# Server 1 talking to the client
def client(lock):
    # global closeClientSocket
    global server_socket
    global serverOff
    global server1Port
    global server1address

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print('Socket created : S2- Client \n')
        print(HOST_ipS2)
        server_socket.bind((HOST_ipS2, 8889))
        print('Client Bind complete : S2 - Client \n')
        print(HOST_ipS2)


    except socket.error as msgC:
        print('Failed to create socket or bind socket. Error Code : ' + str(msgC) + ' Message ' + msgC)

    while 1:
        if serverOff == True:
           # msg = f"CHANGE-SERVER|IP:{server2address[0]}|Socket:{8889}"
            #print(msg)
            # Send server is now off to client
            #reply_client(server_socket, msg, message['IP'])
            lock.acquire()
            serverOff = False
            lock.release()
            # Send server is now off to client
            endTime = time.time() + 25  # * 15    #15 means 15 minutes therefore for us we need to put it to 5
            while time.time() < endTime:  # timer for server can catch updates on clients and server while not serving
                '''do whatever you do'''
            #break


        else:

            message = recieve_message(server_socket)
            #message2 = recieve_message2(server_socket)


            if message is False:
                print(f"Closed connection from {message['message']['name']}")
                continue

            print(f"Recieved message from {message['message']['name']}: {message['message']}")
            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"

            if message['message']['Action'] == 'Register':
                # Validate if name is already in use
                userIsRegistered = False
                with open("Datebase_Server2.txt", "r") as f:
                    lines = f.readlines()
                with open("Datebase_Server2.txt", "w") as f:
                    for line in lines:
                        if f"{message['message']['name']}:" in line:
                            userIsRegistered = True
                        f.write(line)

                if userIsRegistered:
                    # Print action to console
                    msg = f"REGISTER-DENIED|#{message['message']['RQ']}| {message['message']['name']} is " \
                          f"already registered"
                    print(msg)
                    # Send Denial of Registration
                    reply_client(server_socket, msg, message['IP'])
                    # Send info to other server
                   # reply_client(server_socket, msg, ("10.0.0.240", 8890))
                else:
                    # Print action to console
                    msg = f"REGISTERED|#{message['message']['RQ']}"
                    msg_server = "REGISTERED"
                    reply = "Client info"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    server_socket.sendto(bytes(msg_server, 'utf-8'), (HOST_ipS1, server1Port))
                    send_message_client_to_server(server_socket, (HOST_ipS1, server1Port))
                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])
                    msg = f"REGISTERED|#{message['message']['RQ']}| {message['message']['name']}"
                    print(msg)
                    # Send info to other server
                    #msg = {"Action":"REGISTERED", "Name": message['message']['name'], "IP": message['IP'][0], "Socket":message['IP'][1]}
                   # reply_client(server_socket, msg, ("10.0.0.240", 8890))
                    # Add message to database
                    writeFile = open('Datebase_Server2.txt', 'a')
                    # currently using client_address & socket instead of info sent by client
                    writeFile.write(reusedStr + '\n')
                    writeFile.close()
                continue

            if message['message']['Action'] == 'Update':
                isUpdated = False
                # Update info on database
                with open("Datebase_Server2.txt", "r") as f:
                    lines = f.readlines()
                with open("Datebase_Server2.txt", "w") as f:
                    for line in lines:
                        if f"{message['message']['name']}:" in line:
                            if line.find("Subjects") == -1:
                                f.write(reusedStr + '\n')
                                print("Old info was " + line.strip(message['message']['name']))
                                print("Updated Info is " + reusedStr)
                            else:
                                strHolder = line[line.find(", Subjects"):]
                                print(strHolder)
                                f.write(reusedStr + strHolder)
                                print("Old info was " + line.strip(message['message']['name']))
                                print("Updated Info is " + reusedStr + strHolder)

                            isUpdated = True
                        else:
                            f.write(line)
                            # print(f'Write {line.strip("\n")}')

                if isUpdated:
                    pass
                    # Send Update Confirmed to Client
                    msg = f"UPDATE-CONFIRMED|#{message['message']['RQ']}| {message['message']['name']} " \
                          f"{message['IP']}"
                    reply = "Client info"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    reply = "UPDATE-CONFIRMED:"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    send_message_client_to_server(server_socket, (HOST_ipS1, server1Port))
                    # Print action to console
                    print(msg)
                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])
                else:
                    pass
                    # Send Update Denied to Client
                    msg = f"UPDATE-DENIED|#{message['message']['RQ']}| {message['message']['name']} " \
                          f"is not Registered"
                    # Print action to console
                    print(msg)
                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])
                # Send info to other server
                """
                Send to other server code here
                """
                continue

            if message['message']['Action'] == 'Subjects':
                subjectsUpdated = False
                # Update info on database
                with open("Datebase_Server2.txt", "r") as f:
                    lines = f.readlines()
                with open("Datebase_Server2.txt", "w") as f:
                    for line in lines:
                        if f"{message['message']['name']}:" in line:
                            if line.find("Subjects") == -1:
                                f.write(reusedStr + f", Subjects:{message['message']['subjects']} \n")
                                subjectsUpdated = True
                            else:
                                f.write(reusedStr + f", Subjects:{message['message']['subjects']} \n")
                                print(f"Old Subjects are {line.strip(message['message']['name'])}")
                                print(f"Updated Subjects are {message['message']['subjects']}")
                                subjectsUpdated = True
                        else:
                            f.write(line)
                            # print(f'Write {line}')

                if subjectsUpdated:
                    pass
                    # Send Update Confirmed to Client
                    msg = f"SUBJECTS-UPDATED|#{message['message']['RQ']}| {message['message']['name']} " \
                          f"Subject(s): {message['message']['subjects']}"
                    reply = "Client info"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    reply = "SUBJECT-UPDATED:"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    send_message_client_to_server(server_socket, (HOST_ipS1, server1Port))
                    # Print action to console
                    print(msg)
                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])
                else:
                    pass
                    # Send Subjects Update Denied to Client
                    msg = f"SUBJECTS-REJECTED|#{message['message']['RQ']}| {message['message']['name']} " \
                          f"is not Registered"
                    # Print action to console
                    print(msg)
                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])

                # Send info to other server
                """
                Send to other server code here
                """
                continue

            if message['message']['Action'] == 'Publish':
                registered = False
                hasSubject = False
                publish = False

                # Check which users to send message
                with open("Datebase_Server2.txt", "r") as f:
                    lines = f.readlines()
                with open("Datebase_Server2.txt", "w") as f:
                    for line in lines:
                        f.write(line)
                        if f"{message['message']['name']}:" in line:
                            registered = True
                            if line.find("Subjects") == -1:
                                pass
                            else:
                                hasSubject = True
                                if line.find(message['message']['subjects']) == -1:
                                    pass
                                else:
                                    publish = True
                                    pass
                        else:
                            pass

                if publish:
                    # Send Message to the other clients with same subject
                    # Printing Message to send
                    MESSAGE = f"{message['message']['name']} from {message['message']['subjects']} says {message['message']['message']}"
                    # print(MESSAGE)

                    # Check which users to send message
                    with open("Datebase_Server2.txt", "r") as f:
                        lines = f.readlines()
                    with open("Datebase_Server2.txt", "w") as f:
                        for line in lines:
                            f.write(line)
                            if f"{message['message']['name']}:" in line:
                                # Don't send ourselves a message
                                pass
                            else:
                                if line.find("Subjects") == -1:
                                    pass
                                else:
                                    if line.find(message['message']['subjects']) == -1:
                                        pass
                                    else:
                                        x = line.find('IP')
                                        y = line.find(',', x)
                                        w = line.find('Socket')
                                        z = line.find(',', w)
                                        clinet_addr = (line[(x + 4):y], int(line[(w + 7):z]))
                                        print(MESSAGE, clinet_addr)
                                        reply_client(server_socket, MESSAGE, clinet_addr)

                    # Send PUBLISH to Client
                    msg = f"PUBLISHED|#{message['message']['RQ']}| {message['message']['name']} " \
                          f"sent {message['message']['message']}"
                    # Print action to console
                    print(msg)

                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])

                else:
                    if hasSubject:
                        # Send PUBLISH-DENIED to Client
                        msg = f"PUBLISH-DENIED|#{message['message']['RQ']}| {message['message']['name']} " \
                              f"does not have {message['message']['subjects']} in its subjects"
                        # Print action to console
                        print(msg)
                        # Send Acceptance of Registration
                        reply_client(server_socket, msg, message['IP'])

                    elif registered:
                        # Send PUBLISH-DENIED to Client
                        msg = f"PUBLISH-DENIED|#{message['message']['RQ']}| {message['message']['name']} " \
                              f"has no Subjects"
                        # Print action to console
                        print(msg)

                        # Send Acceptance of Registration
                        reply_client(server_socket, msg, message['IP'])
                    else:
                        # Send PUBLISH-DENIED to Client
                        msg = f"PUBLISH-DENIED|#{message['message']['RQ']}| {message['message']['name']} " \
                              f"is not Registered"
                        # Print action to console
                        print(msg)
                        # Send Acceptance of Registration
                        reply_client(server_socket, msg, message['IP'])

                        # Send info to other server
                """
                Send to other server code here
                """
                continue

            if message['message']['Action'] == 'Deregister':
                # Remove message to database
                inDatabase = False
                with open("Datebase_Server2.txt", "r") as f:
                    lines = f.readlines()
                with open("Datebase_Server2.txt", "w") as f:
                    for line in lines:
                        if f"{message['message']['name']}:" in line:
                            pass
                            # print(f"Removed {line}")
                        else:
                            f.write(line)
                            inDatabase = True
                            # print(f'Write {line}')

                if inDatabase:
                    # Send De-Register to Client
                    msg = msg = f"DE-REGISTERED|#{message['message']['RQ']}|{message['message']['name']}"
                    reply = "Client info"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    reply = "deregistered"
                    server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS1, server1Port))
                    send_message_client_to_server(server_socket, (HOST_ipS1, server1Port))
                    # Print action to console
                    print(msg)

                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])
                else:
                    # Send De-Register to Client
                    msg = f"DE-REGISTERED REJECTED|#{message['message']['RQ']}|" \
                          f"{message['message']['name']} was not found in the Database"
                    # Print action to console
                    print(msg)

                    # Send Acceptance of Registration
                    reply_client(server_socket, msg, message['IP'])

                # Send info to other server
                """
                Send to other server code here
                """

                continue


if __name__ == "__main__":
    # initialization

    lock = threading.Lock()

    p1 = threading.Thread(target=client, args=(lock,))
    p1.start()
    #
    p2 = threading.Thread(target=server_to_server, args=(lock,))
    p2.start()
    #
    p1.join()
    p2.join()



