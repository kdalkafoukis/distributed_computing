#!/usr/bin/env python3.6


##tcp server almost finished
### error handling missing(part3)
import asyncio,sys,json,uuid

async def handle_echo(reader, writer):
    data = await reader.read(4096)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    #print("Received %r from %r" % (message, addr))

    req=json.loads(data.decode())
    keys=req.keys()

    res=json.dumps({'error':''})        #make sure there is a result to be sent
    if ('register' in keys):
        uid=str(uuid.uuid4())           #create a random id
        res=json.dumps({'uid':uid})     #put to result the uid
        users[uid]=req['register']      #save the user to the server

    elif(req['uid'] in users):

        if('list_groups' in keys):
            res=json.dumps({'list_groups':list(groups.keys())})

        elif('join_group' in keys):
            if req['join_group'] in groups:                              #elegxos an to group uparxei idi
                groups[req['join_group']].update({req['uid']:users[req['uid']]})
            else:
                groups[req['join_group']]={req['uid']:users[req['uid']]} #an den uparxei dimiourgise group

            res=json.dumps({'join_group':groups[req['join_group']]})

        elif('list_members' in keys):
            if (req['list_members'] in groups.keys()):                     #elegxos an uparxei to group
                for v in groups[req['list_members']].values():             #filtrare ta username apta group
                    members.append(v['username'])

            res=json.dumps({'list_members':members})

            del members[:]

        elif('exit_group' in keys):
            if (req['exit_group'] in groups.keys()):          #control if group exists
                for i in list(groups[req['exit_group']]):
                    if (req['uid']==i):                        #delete user from group
                        groups[req['exit_group']].pop(i,None)
                    if(groups.get(req['exit_group'])=={}):    #an itan o teleutaios
                        groups.pop(req['exit_group'])         #diegrapse to

            res=json.dumps({'exit_group':''})

        elif('quit' in keys):
            users.pop(req['uid'])                          #delete user from userlist
            for v in list(groups):
                print(groups[v])
                for value in list(groups[v]):
                    if (req['uid']==value):
                        groups[v].pop(value,None)
                    if(groups.get(v)=={}):    #an itan o teleutaios
                        groups.pop(v)         #diegrapse to

            res=json.dumps({'quit':''})

    print('groups:',groups)
    print('users:',users)

    print("Send: %r" % res)
    writer.write(res.encode())
    await writer.drain()

    #print("Close the client socket")
    writer.close()

users={}
groups={}
members=[]

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
server = loop.run_until_complete(coro)
# Serve requests until Ctrl+C is pressed
print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
