import socket
import sys
import time
import threading
import pickle
import select

HOST_ipS1 = socket.gethostbyname(socket.gethostname())
######################## user input
HOST_ipS2="10.0.0.240"
#HOST_ipS2= input("Enter IP of Server 2: ")
PORT_CTS = 8885  # Port for client to connect
PORT_STS = 8890  # Port for server to connect
HEADER_LENGTH = 1024
server2Port = 8891
server2Port_fC=8889
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
        print("Server1 Cannot send response to client \n")


def recieve_message(client_socket):
    global message2
    try:
        print('recv messag')
        print('testing')
        message, ip = client_socket.recvfrom(HEADER_LENGTH)
        message2 = message
        print(ip)
        unpickle = pickle.loads(message)
        print(unpickle)
        return {"IP": ip, "message": unpickle}

    except:
        return False

def send_message_client_to_server(socket, addr_client):
    global message2
    print(message2)
    reply_client = message2
    try:
        socket.sendto(reply_client, addr_client)
    except socket.error as reply_client:
        print("Server 2 cannot send client response to server 1 \n")

############################################################################
# server 1 to communicate with server 2
def server_to_server(lock):
    #  global closeClientSocket
    global socket_client
    global serverOff
    socket_server2 = None
    # Create and bind socket with server 2
    try:
        socket_server2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket created : S1-S2 \n")
        socket_server2.bind((HOST_ipS1, PORT_STS))
        print("Socket bind complete : S1-S2 \n")
    except socket.error as msgS2:
        print("Failed to create socket or bind socket. Error Code : " + str(msgS2) + " Message " + msgS2)

    # Reveiving message from server 2
    while 1:
        ds2 = socket_server2.recvfrom(1024)
        messageS2 = ds2[0]
        addr_server2 = ds2[1]
        reply_server2 = str("sever 1 is sending message")

        # send reply to server 2 (if not shutdown)
        print("server 2 sent: " + str(messageS2.decode('utf-8')))

        if messageS2.decode('utf-8') == "are you running?":
            reply_server2 = 'yes'
            socket_server2.sendto(bytes(reply_server2, 'utf-8'), addr_server2)
            print("Telling server 2 that I'm running")

        print("server 1 is serving")
        endTime = time.time() + 25  # * 15    #15 means 15 minutes therefore for us we need to put it to 5
        count = 0  # this was just to test
        while time.time() < endTime:  # timer for server can catch updates on clients and server while not serving
            '''do whatever you do'''
        reply_server2 = "You take over"
        socket_server2.sendto(bytes(reply_server2, 'utf-8'), addr_server2)
        serverOff = True

        if serverOff == True:
            reply_server2 = "Alright, be back in 15 seconds"
            socket_server2.sendto(bytes(reply_server2, 'utf-8'), addr_server2)
            print("Server 1 is not serving")
            # time.sleep(30)
            endTime = time.time() + 25  # * 15    #15 means 15 minutes therefore for us we need to put it to 5
            count = 0  # this was just to test
            while time.time() < endTime:  # timer for server can catch updates on clients and server while not serving
                '''do whatever you do'''
                endTime2 = time.time() + 2
                while time.time() < endTime2:

                    if time.time() >= endTime2 or time.time() >= endTime:
                        break

                    ds2 = socket_server2.recvfrom(1024)
                    messageS2 = ds2[0]
                    addr_server2 = ds2[1]

                    if messageS2.decode('utf-8') == "You take over":
                        break;

                    if messageS2.decode('utf-8') == "Client info":
                        ds2 = socket_server2.recvfrom(1024)
                        messageS2 = ds2[0]
                        addr_server2 = ds2[1]
                        # server to server REGISTER
                        if messageS2.decode('utf-8') == "REGISTERED":
                            #receives all infos of client
                            message = recieve_message(socket_server2)
                            # code for server receiving info on client form other server while not serving
                            print(f"Recieved message from {message['message']['name']}: {message['message']}")
                            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"
                            if message['message']['Action'] == 'Register':
                                # Validate if name is already in use
                                userIsRegistered = False
                                with open("Datebase_Server1.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server1.txt", "w") as f:
                                    for line in lines:
                                        if f"{message['message']['name']}:" in line:
                                            userIsRegistered = True
                                        f.write(line)
                                    # Send Acceptance of Registration
                                    # reply_client(server_socket, msg, message['IP'])
                                    # Add message to database
                                writeFile = open('Datebase_Server1.txt', 'a')
                                # currently using client_address & socket instead of info sent by client
                                writeFile.write(reusedStr + '\n')
                                writeFile.close()
                                # Print action to console
                                msg = f"{message['message']['name']} is now registered"
                                print(msg)

                        #server to server DEREGISTER
                        if messageS2.decode('utf-8')=="deregistered":
                            message = recieve_message(socket_server2)
                            if message['message']['Action'] == 'Deregister':
                                # Remove message to database
                                inDatabase = False
                                with open("Datebase_Server1.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server1.txt", "w") as f:
                                    for line in lines:
                                        if f"{message['message']['name']}:" in line:
                                            pass
                                            # print(f"Removed {line}")
                                        else:
                                            f.write(line)
                                            inDatabase = True

                        # server to server UPDATE CLIENT INFO
                        if messageS2.decode('utf-8') == "UPDATE-CONFIRMED:":
                            message = recieve_message(socket_server2)
                            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"
                            if message['message']['Action'] == 'Update':
                                isUpdated = False
                                # Update info on database
                                with open("Datebase_Server1.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server1.txt", "w") as f:
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

                        # server to server UPDATE SUBJECTS
                        if messageS2.decode('utf-8') == "SUBJECT-UPDATED:":
                            message = recieve_message(socket_server2)
                            reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}, Socket:{message['IP'][1]}"
                            if message['message']['Action'] == 'Subjects':
                                subjectsUpdated = False
                                # Update info on database
                                with open("Datebase_Server1.txt", "r") as f:
                                    lines = f.readlines()
                                with open("Datebase_Server1.txt", "w") as f:
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
                                    continue
                            else:
                                continue


# Server 1 talking to the client
def client(lock):
    # the first while loop runs the clients so that when we close the socket to change it
    # we are able to reset the binding
    while True:

        # global closeClientSocket
        global server_socket
        global serverOff
        global PORT_CTS
        global server2address
        global server2Port
        client_IP = (None,None)#None)

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('Socket created : S1- Client \n')
            print(HOST_ipS1)
            server_socket.bind((HOST_ipS1, 8885))
            print(PORT_CTS)
            print('Client Bind complete : S1 - Client \n')
            print(HOST_ipS1)


        except socket.error as msgC:
            print('Failed to create socket or bind socket. Error Code : ' + str(msgC) + ' Message ' + msgC)

        while 1:

            if serverOff == True:
                #server2address[0]=HOST_ipS2
                msg = f"CHANGE-SERVER|IP:{HOST_ipS2}|Socket:{server2Port_fC}"
                print(msg)
                # Send server is now off to client
                reply_client(server_socket, msg, message['IP'])
                server_socket.close()
                lock.acquire()
                serverOff = False
               # PORT_CTS = PORT_CTS - 1  # changing the port number

                lock.release()
                print(PORT_CTS)


                endTime = time.time() + 25   # * 15    #15 means 15 minutes therefore for us we need to put it to 5
                while time.time() < endTime:  # timer for server can catch updates on clients and server while not serving
                    '''do whatever you do'''
               # break

                # time.sleep(20)

            else:
                message = recieve_message(server_socket)

                if message is False:
                    #print(f"Closed connection from {message}")
                    break
                client_IP = message['IP']
                print(f"Recieved message from {message['message']['name']}: {message['message']}")
                reusedStr = f"{message['message']['name']}: Name: {message['message']['name']}, IP: {message['IP'][0]}"\
                            f" Socket:{message['IP'][1]} "

                if message['message']['Action'] == 'Register':
                    # Validate if name is already in use
                    userIsRegistered = False
                    with open("Datebase_Server1.txt", "r") as f:
                        lines = f.readlines()
                    with open("Datebase_Server1.txt", "w") as f:
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
                    else:
                        # Print action to console
                        msg = f"REGISTERED|#{message['message']['RQ']}"
                        msg_server = "REGISTERED"
                        reply = "Client info"
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        server_socket.sendto(bytes(msg_server, 'utf-8'), (HOST_ipS2, server2Port))
                        send_message_client_to_server(server_socket, (HOST_ipS2, server2Port))
                        # Send Acceptance of Registration
                        reply_client(server_socket, msg, message['IP'])
                        msg = f"REGISTERED|#{message['message']['RQ']}| {message['message']['name']}"
                        print(msg)
                        # Send info to other server
                        # msg = {"Action":"REGISTERED", "Name": message['message']['name'], "IP": message['IP'][0], "Socket":message['IP'][1]}
                        # reply_client(server_socket, msg, ("10.0.0.240", 8890))
                        # Add message to database
                        writeFile = open('Datebase_Server1.txt', 'a')
                        # currently using client_address & socket instead of info sent by client
                        writeFile.write(reusedStr + '\n')
                        writeFile.close()

                    continue

                if message['message']['Action'] == 'Update':
                    isUpdated = False
                    # Update info on database
                    with open("Datebase_Server1.txt", "r") as f:
                        lines = f.readlines()
                    with open("Datebase_Server1.txt", "w") as f:
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
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        reply = "UPDATE-CONFIRMED:"
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        send_message_client_to_server(server_socket, (HOST_ipS2, server2Port))
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
                    with open("Datebase_Server1.txt", "r") as f:
                        lines = f.readlines()
                    with open("Datebase_Server1.txt", "w") as f:
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
                        # Print action to console
                        reply = "Client info"
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        reply = "SUBJECT-UPDATED:"
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        send_message_client_to_server(server_socket, (HOST_ipS2, server2Port))
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
                    with open("Datebase_Server1.txt", "r") as f:
                        lines = f.readlines()
                    with open("Datebase_Server1.txt", "w") as f:
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
                        MESSAGE = f"{message['message']['name']} from {message['message']['subjects']} says " \
                                  f"{message['message']['message']}"
                        # print(MESSAGE)

                        # Check which users to send message
                        with open("Datebase_Server1.txt", "r") as f:
                            lines = f.readlines()
                        with open("Datebase_Server1.txt", "w") as f:
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
                    with open("Datebase_Server1.txt", "r") as f:
                        lines = f.readlines()
                    with open("Datebase_Server1.txt", "w") as f:
                        for line in lines:
                            if f"{message['message']['name']}:" in line:
                                inDatabase = True
                                # print(f"Removed {line}")
                            else:
                                f.write(line)
                                # print(f'Write {line}')

                    if inDatabase:
                        # Send De-Register to Client
                        msg = f"DE-REGISTERED|#{message['message']['RQ']}|{message['message']['name']}"
                        reply = "Client info"
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        reply = "deregistered"
                        server_socket.sendto(bytes(reply, 'utf-8'), (HOST_ipS2, server2Port))
                        send_message_client_to_server(server_socket, (HOST_ipS2, server2Port))
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
