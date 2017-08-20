#!/usr/bin/python
import socket,sys,threading,signal

connections=[]
all_threads=[]

quit_now = False

def quit_gracefully(signal=None,frame=None):
	print("Quiting Gracefully")
	quit_now = True
	for conn in connections:
		conn.shutdown()
		conn.close()	
	s.close()
	ws.close()
	for th in all_threads:
		th.exit()
	sys.exit(0)

signal.signal(signal.SIGINT,quit_gracefully)
signal.signal(signal.SIGTERM,quit_gracefully)

try:
    listening_port = int(raw_input("Enter the port for the proxy to listen: "))
except KeyboardInterrupt :
    print "**Program execution interupted by user!!!!\nExiting now..."

buffer_size = 4096
max_connections = 5
flag = 0

all_sites = []
fp = open("blocked_sites.txt","r")
for line in fp:
	all_sites.append(line.strip())

def conn_receive(con):
    buff=''
    if quit_now:
	sys.exit(12)
    while True:
        data=con.recv(4096)
        buff=buff + data
        if len(data) < 4096:
            break
    return buff

def data_transfer(b_sock, w_sock):
	b_sock.setblocking(0)
	w_sock.setblocking(0)
	
	while True:
		try:
			request = conn_receive(b_sock)
			if len(request)>0:
				#print "Browser's request............................................"
				#print str(request)
				w_sock.sendall(request)
		except socket.error as err:
			pass

		try:
			reply = conn_receive(w_sock)
			if len(reply)>0:
				#print "Server's Reply..............................................."
				#print str(reply)
				b_sock.sendall(reply)
		except socket.error as err:
			pass
				

def start():
    host = ""
    try:
        # creating the socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # binding the socket
        s.bind((host, listening_port))
        s.listen(max_connections)
        print("Listening on port: " + str(listening_port))
    except socket.error as err:
        print("Error in setting up the socket!!!" + str(err))

    # accepting an incoming connection
    while True:
        try:
            conn, addr = s.accept()
	    connections.append(conn)
            print "Connection established with: " + addr[0] + " at port: " + str(addr[1])
            data = conn.recv(buffer_size)
            '''
            try:
                data = str(data, "utf-8")
                t = threading.Thread(target=resolve_request, args=(conn, data, addr))
            except:
                print("Exception")
                data = data
                flag = 1
                t = threading.Thread(target=resolve_request, args=(conn, data, addr))

            #data = str(data,"utf-8")
            t.start()
            '''
            t = threading.Thread(target=resolve_request, args=(conn, data, addr))
            all_threads.append(t)
            t.start()
        except KeyboardInterrupt:
            print("Exception in accepting incoming connections!!!")
            print("Exiting now...")
            sys.exit(2)
    s.close()


def resolve_request(conn,data,addr):
    try:
        # resolving the first line
        '''
        if (flag == 1):
            data1 = data
            try:
                data = str(data, "utf-8")
            except:
                print("Execption again -_- ")
        '''
        block = False
        first_line = data.split("\n")[0]
	method = first_line.split(" ")[0]
        http_addr = first_line.split(" ")[1]
        #print(http_addr)
        http_pos = http_addr.find("://")  # finding the position of ://
        if (http_pos == -1):
            temp_url = http_addr
        else:
            temp_url = http_addr[(http_pos+3):]
        #port_pos = temp_url.find(":")
        webserver_pos = temp_url.find("/")

        if (webserver_pos == -1):
            webserver_pos = len(temp_url)

        t_url = temp_url[:webserver_pos]
        port_pos = t_url.find(":")
        webserver=""
        port=-1
        if (port_pos == -1):
            port = 80
            webserver = t_url[:webserver_pos]
        else:
            port = int(t_url[(port_pos+1):])
            webserver = temp_url[:port_pos]
	
	print webserver
	print str(port)

	'''
        for site in fp:
	    site = str(site[:site.find("/n")])
            if site == webserver or site in webserver:
                count_site = count_site+1
                break
	
	for site in all_sites:
		res = site.find(webserver)
		if res == -1:
			continue
		else:
			block = True
			break
	'''
	#if count_site !=0:	
	#if "porn" in webserver:
	#print block
	if webserver in all_sites:
	    print "Blocking the site : " + webserver
	    #if port == 443:
	    	#first_https_reply = "HTTP/1.1 200 Connection established\r\n\r\n"
	    	#conn.send(first_https_reply)
	    block_reply = "<!doctype HTML><html><head><title>Access Denied</title></head><body><h1>Acess Denied</h1><h2>The Website you are trying to open is RESTRICTED</h2></body></html>"
	    conn.send(block_reply)
	    conn.close()
	    count_site = 0
	else:
	    print "Allowing the site : " + webserver
	    proxy_server(webserver, port, conn, data, addr, method)
	
    except Exception as e:
        pass


def proxy_server(webserver, port, conn, data, addr, method):
    try:
        ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webaddress = socket.gethostbyname(webserver)
        print "Trying to connect to: " + webserver + " at port: " + str(port)
        ws.connect((webaddress, port))
	print data
        '''
        if (flag == 0):
            s.send(str.encode(data))
        else:
            s.send(data)
        '''
	'''
        s.send(data)

        while True:
            reply = s.recv(buffer_size)

            if (len(reply) > 0):
                conn.send(reply)
                print "Request completed !!!\n" + reply
            else:
                break  # Breaking the connection if recieving data failed
	'''
	
	if method == "CONNECT" or port == 443:
		first_https_reply = "HTTP/1.1 200 Connection established\r\n\r\n"
		conn.send(first_https_reply)
		print "Https Connection"
		data_transfer(conn, ws)
	else:
		ws.send(data)
		data_transfer(conn, ws)
	
        ws.close()
        conn.close()

    except socket.error:
        ws.close()
        conn.close()
        sys.exit(1)

start()
