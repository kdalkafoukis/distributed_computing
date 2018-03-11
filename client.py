#!/usr/bin/env python3.6

##tcp server,tcp client,udp client
####udp client fifo missing (phase2)
import asyncio
import sys
import json

class UDPserver:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('udp server Received %r from %s' % (message, addr))
        print('udp server Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)

class UDPclient:
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('udp client Send:', self.message)
        self.transport.sendto(self.message.encode())

    def datagram_received(self, data, addr):
        print("udp client Received:", data.decode())

        print("udp client Close the socket")
        self.transport.close()

    def error_received(self, exc):
        print('udp client Error received:', exc)

    def connection_lost(self, exc):
        print("udp client Socket closed")
        #loop = asyncio.get_event_loop()
        #loop.stop()

async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888,loop=loop)

    #print('tcp client Send: %r' % message)
    writer.write(message.encode())
    await writer.drain()
    data = await reader.read(4096)

    req=json.loads(data.decode())
    key=req.keys()
    if(('uid' not in key )and('quit' not in key )and('exit_group' not in key)):   #control when data from
        print(data.decode())                                                    #server should be printed

    if('join_group' in key ):
        groups.update({current_group[0]:req['join_group']})

    # print('tcp client Received: %r' % data.decode())
    #print('tcp client Close the socket')
    writer.close()
    return data.decode()

def fileCallback(loop,uid):
    message=input()         #when you press enter create either tcp,udp client

    try:
        if(message[0]=='!'):    #control for creating tcp or udp client
            m=json.loads(uid)   #handle the uid in json format
            flag=message.replace('\n','').split(' ')    #catch the input,break the line
                                                        #into words remove '\n' char
            if (flag[0]=='!lg'):    #control the commands
                m['list_groups']=''

            elif (flag[0]=='!j'):
                if (flag[1:]):
                    m['join_group']=flag[1]
                    current_group[0]=flag[1]

                else:
                    return

            elif (flag[0]=='!lm'):
                if (flag[1:]):
                    m['list_members']=flag[1]
                else:
                    return

            elif (flag[0]=='!w'):
                if (flag[1:]):
                    global multicast_group
                    multicast_group=[]
                    for v in groups[flag[1]].values():
                        multicast_group.append((v['ip'],v['port']))

                return

            elif (flag[0]=='!e'):
                if (flag[1:]):
                    m['exit_group']=flag[1]
                else:
                    return

            elif (flag[0]=='!q'):
                m['quit']=''

            else:
                return

            m=json.dumps(m)
            loop.create_task(tcp_echo_client(m, loop))

        else:
            # print(multicast_group)
            try:
                connect=[]
                for g in multicast_group:
                    connect.append(loop.create_datagram_endpoint(
                        lambda: UDPclient(message, loop),
                        remote_addr=g))

                asyncio.gather(*connect)
            except:
                pass
                # print('you haven't selected a group yet')
    except:
        pass

addr='127.0.0.1'
port=9999
username='konsta'
groups={}
current_group=['']

loop = asyncio.get_event_loop()

listen = loop.create_datagram_endpoint(UDPserver, local_addr=(addr, port))   #create udp server
transport, protocol = loop.run_until_complete(listen)

message={'register':{'ip':addr,'port':str(port),'username':username}}   #initial register info
m=json.dumps(message)
uid=loop.run_until_complete(tcp_echo_client(m, loop)) #register

loop.add_reader(sys.stdin,fileCallback,loop,uid)      #add asynchronous input

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
transport.close()
loop.close()
