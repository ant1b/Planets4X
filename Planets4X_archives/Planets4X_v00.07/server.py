from mastermind_import import *
from settings import *

import math
import random
import threading
from time import gmtime, strftime
from time import sleep

ip = "localhost"
port = 6317


def PlayerColour(playerID, col):
    bckgd = [0,0,0]
    fgd   = [255,127,39]
    neutral = [127,127,127]

    try:
        if len(col)>0: pass
        else: col = []
    except: col = []
    i=0
    while len(col)<playerID:
      i = i+1
      a = math.pow(2,i-1)
      belowmid = list(range(int(a/2-1),0,-2))
      abovemid = list(range(int(a-1),int(a/2),-2))
      j=[]
      for k in range(len(belowmid)+len(abovemid)):
          if int(math.fmod(k,2))==0: j.append(belowmid[int(k/2)])
          else: j.append(abovemid[int(k/2)])
      
      if len(j)<1:
        teinte = 255;
        col.append([0,0,teinte])
        col.append([0,teinte,0])        
        col.append([teinte,0,0])
        for grad in range(127,255,128):
            col.append([grad,0,teinte])
            col.append([0,teinte,grad])
            col.append([teinte,grad,0])
            
            col.append([0,grad,teinte])
            col.append([grad,teinte,0])
            col.append([teinte,0,grad])
      else:
        for k in j:
          teinte = int( 255 * (1-(1/(math.pow(2,i)))*k) );
          for m in j:
                grad = int(teinte-(teinte-64)*(m/a))
                col.append([grad,0,teinte])
                col.append([0,teinte,grad])
                col.append([teinte,grad,0])
            
                col.append([0,grad,teinte])
                col.append([grad,teinte,0])
                col.append([teinte,0,grad])

        temp = []
        for k in range(len(col)):
            doublon = False
            for m in range(k-1):
                if col[k] == col[m]: doublon = True
            if 64 > math.sqrt( math.pow(col[k][0]-fgd[0],2) + math.pow(col[k][1]-fgd[1],2) + math.pow(col[k][2]-fgd[2],2) ):
                doublon = True
            if not doublon: temp.append(col[k])
        col = temp

    return [col, col[playerID]]

def IsOneTileMove(x1, y1, x2, y2):
        if x1==x2-1 and y1==y2:
                #print("case click on tile to the right")
                return True
        elif x1==x2+1 and y1==y2:
                #print("case click on tile to the left")
                return True
        elif x1==x2 and y1==y2-1:
                #print("case click on below tile")
                return True
        elif x1==x2 and y1==y2+1:
                #print("case click on above tile")
                return True
        else:
                #print("case not adjacent tile:", x1, "x", y1, " VS.", x2, "x", y2)
                return False
            
class P4X_Server(MastermindServerTCP):
    def __init__(self):
        MastermindServerTCP.__init__(self, 0.5,0.5,60.0) #server refresh, connections' refresh, connection timeout

        self.games = []
        self.queue = None
        self.currentIndex=0

        self.chat = [None]*scrollback
        self.mutex = threading.Lock()
        self.logmsg = self.chat

    def gamesetup(self, connection_object, data):
        self.mutex.acquire()
        #print(connection_object.gameid, "/", len(self.games))
        if connection_object == self.games[connection_object.gameid-1].playerlist[0]:
            self.games[connection_object.gameid-1].boardsize = [data["htiles"],data["vtiles"]]
            self.games[connection_object.gameid-1].maxplayer = data["maxplayer"]
            self.games[connection_object.gameid-1].populate()
            tempcol = PlayerColour(1,self.games[connection_object.gameid-1].colorlist)
            self.callback_client_send(connection_object, {"action": "joingame", "player":1, "playercolor": tempcol[1], "gameid": connection_object.gameid, "htiles":self.games[connection_object.gameid-1].boardsize[0], "vtiles":self.games[connection_object.gameid-1].boardsize[1]})
            for m in self.games[connection_object.gameid-1].planetlist:
                if m.ownership == self.games[connection_object.gameid-1].playerlist[0]:
                    self.callback_client_send(connection_object, {"action": "allocate", "object": "planet", "xcoord":m.coord[0],"ycoord":m.coord[1]})
            for m in self.games[connection_object.gameid-1].shiplist:
                if m.ownership == self.games[connection_object.gameid-1].playerlist[0]:
                    self.callback_client_send(connection_object, {"action": "allocate", "object": "spaceship", "xcoord":m.coord[0],"ycoord":m.coord[1]})
        else:
            for k in range(len(self.games[connection_object.gameid-1].playerlist)):
                if connection_object == self.games[connection_object.gameid-1].playerlist[k]:
                    self.games[connection_object.gameid-1].allconnectcensus = self.games[connection_object.gameid-1].allconnectcensus+1
                    self.games[connection_object.gameid-1].populate()
                    tempcol = PlayerColour(self.games[connection_object.gameid-1].allconnectcensus,self.games[connection_object.gameid-1].colorlist)
                    self.callback_client_send(connection_object, {"action": "joingame", "player":self.games[connection_object.gameid-1].allconnectcensus, "playercolor": tempcol[1],"gameid": connection_object.gameid, "htiles":self.games[connection_object.gameid-1].boardsize[0], "vtiles":self.games[connection_object.gameid-1].boardsize[1]})
                    for m in self.games[connection_object.gameid-1].planetlist:
                        if m.ownership == self.games[connection_object.gameid-1].playerlist[k]:
                            self.callback_client_send(connection_object, {"action": "allocate", "object": "planet", "xcoord":m.coord[0],"ycoord":m.coord[1]})
                    for m in self.games[connection_object.gameid-1].shiplist:
                        if m.ownership == self.games[connection_object.gameid-1].playerlist[k]:
                            self.callback_client_send(connection_object, {"action": "allocate", "object": "spaceship", "xcoord":m.coord[0],"ycoord":m.coord[1]})
        self.mutex.release()

    def shipmove(self, connection_object, data):
        self.mutex.acquire()
        knownplanets=[]
        for k in self.games[connection_object.gameid-1].shiplist:
            if data["type"] == "split":
                for j in range(len(data["from"])):
                    if k.coord[0]==data["from"][j].coord[0] and k.coord[1]==data["from"][j].coord[1]:
                        print(k.coord[0], " ", k.coord[1], " ", k.ownership, " VS. ", connection_object)
                        if k.ownership == connection_object:
                            print("Server splits")
                            self.games[connection_object.gameid-1].shiplist.append(Spaceship())
                            self.games[connection_object.gameid-1].shiplist[len(self.games[connection_object.gameid-1].shiplist)-1].locateto(k.coord[0],k.coord[1])
                            self.games[connection_object.gameid-1].shiplist[len(self.games[connection_object.gameid-1].shiplist)-1].ucount    = int(k.ucount - int(k.ucount/2))
                            self.games[connection_object.gameid-1].shiplist[len(self.games[connection_object.gameid-1].shiplist)-1].moveleft  = k.moveleft
                            self.games[connection_object.gameid-1].shiplist[len(self.games[connection_object.gameid-1].shiplist)-1].justsplit = True
                            self.games[connection_object.gameid-1].shiplist[len(self.games[connection_object.gameid-1].shiplist)-1].ownership = connection_object
                            k.locateto(data["to"][j].coord[0],data["to"][j].coord[1])
                            k.ucount    = int(k.ucount/2)
                            k.moveleft  = k.moveleft-1
                            k.justsplit = True
                            break
                        else:
                            print("Ownership mismatch")
            if data["type"] == "plain":
                for j in range(len(data["from"])):
                    if k.coord[0]==data["from"][j][0] and k.coord[1]==data["from"][j][1]:
                        print(k.coord[0], " ", k.coord[1], " ", k.ownership, " VS. ", connection_object)
                        if k.ownership == connection_object:
                            print("Server move")
                            k.locateto(data["to"][0],data["to"][1])
                            k.moveleft  = k.moveleft-1
                            k.justsplit = False
                            break
                        else:
                            print("Ownership mismatch")

            for j in self.games[connection_object.gameid-1].shiplist:
                if j!=k and k.coord[0] == j.coord[0] and k.coord[1] == j.coord[1] and  k.ownership == j.ownership:
                    k.ucount = k.ucount + j.ucount
                    if k.moveleft>j.moveleft:k.moveleft=j.moveleft
                    k.justsplit = False
                    self.games[connection_object.gameid-1].shiplist.remove(j)
            
            for m in self.games[connection_object.gameid-1].planetlist:
                if k.ownership==connection_object and IsOneTileMove(k.coord[0], k.coord[1], m.coord[0], m.coord[1]):
                    knownplanets.append([m.coord[0], m.coord[1], m.initpop, m.popul, m.maxpop, m.popgrowthrate])

        self.callback_client_send(connection_object, {"action": "upknown", "object": "planet", "list":knownplanets})
        self.mutex.release()

    def callback_connect          (self                                          ):
        print("This is callback_connect.")
        #Something could go here        
        return super(P4X_Server,self).callback_connect()
    def callback_disconnect       (self                                          ):
        print("This is callback_disconnect.")
        #Something could go here        
        return super(P4X_Server,self).callback_disconnect()
    def callback_connect_client   (self, connection_object                       ):
        print("This is callback_connect_client.")
        if self.queue==None:
            self.queue=Game(connection_object, len(self.games))
            self.games.append(self.queue)
            connection_object.gameid=len(self.games)
        else:
            connection_object.gameid=len(self.games)
            self.games[len(self.games)-1].playerlist.append(connection_object)
            if len(self.games[len(self.games)-1].playerlist) >= self.games[len(self.games)-1].maxplayer:
                print("Maximum number of players reached")
                self.queue = None
        #Something could go here
        return super(P4X_Server,self).callback_connect_client(connection_object)
    def callback_disconnect_client(self, connection_object                       ):
        print("This is callback_disconnect_client.")
        for k in range(len(self.games[connection_object.gameid-1].playerlist)-1):
                if connection_object == self.games[connection_object.gameid-1].playerlist[k]:
                    print("Player quits")
                    self.games[connection_object.gameid-1].playerlist.remove( connection_object )
        if len(self.games[connection_object.gameid-1].playerlist)<1:
            print("Game shuts")
            self.games.remove( self.games[connection_object.gameid-1] )
        if len(self.games)<1:
            print("No games left running on this server")
        #self.callback_client_send(connection_object, "IdleTimeoutNotification")
        #Something could go here
        return super(P4X_Server,self).callback_disconnect_client(connection_object)
    def callback_client_receive   (self, connection_object                       ):
        print("This is callback_client_receive.")
        #Something could go here
        return super(P4X_Server,self).callback_client_receive(connection_object)
    def callback_client_handle    (self, connection_object, data                 ):
        cmd = data[0]
        if cmd == "introduce":
            self.add_message("Server: "+data[1]+" has joined.")
        elif cmd == "gamesetup":
            #self.add_message(data[1])
            self.gamesetup(connection_object, data[1])
        elif cmd == "shipmove":
            self.shipmove(connection_object, data[1])
        elif cmd == "add":
            self.add_message(data[1])
        elif cmd == "bip":
            pass
        elif cmd == "leave":
            self.add_message("Server: "+data[1]+" has left.")
        self.callback_client_send(connection_object, self.chat)
    def callback_client_send      (self, connection_object, data,compression=None):
        print("This is callback_client_send.")
        #Something could go here
        return super(P4X_Server,self).callback_client_send(connection_object, data,compression)

#        .__init__(time_server_refresh=0.5,time_connection_refresh=0.5,time_connection_timeout=5.0):
#            --Creates a new server object.
#            --The argument "time_server_refresh" determines how quickly the server checks for an end condition (i.e., if you call .accepting_disallow(), "time_server_refresh" is the maximum time it will hang).  Larger numbers use less CPU time.
#            --The argument "time_connection_refresh" is how fast the connection checks for an end condition (i.e., if a connection times out, "time_connection_refresh" is the maximum time past the timeout time the connection will persist).  Larger numbers use less CPU time.
#            --The argument "time_connection_timeout" determines how long a connection is allowed to remain idle before being considered dead.  See "Notes.txt".
#        .__del__():
#            --Destructs the server object.  Issues a MastermindWarningServer if .accepting_disallow() or .disconnect() was not called first, or if there are still active connections.
#        .connect(ip,port):
#            --Connects the server to the network.  If the server is already connected, a MastermindWarningServer is issued and the call has no effect.  MastermindErrorSocket may be raised on failure.
#            --The argument "ip" is the ip to connect as.
#            --The argument "port" is the port to connect as.
#        .disconnect()
#            --Disconnects the server from the network.  If the server is already not connected, a MastermindWarningServer is issued and the call has no effect.  If the server is actively accepting new clients, MastermindWarningServer will be issued, and the call will proceed after automatically calling .accepting_disallow().  If there are active connections, MastermindWarningServer will be issued, and the call will proceed after automatically calling .disconnect_clients().
#        .disconnect_clients():
#            --Disconnects all current clients.  This is typically done before quitting the server; to be sure another client doesn't connect immediately after this call, you should call .accepting_disallow() first.
#        .callback_connect():
#            --Called when the server connects (i.e., when .connect(...) is successful).  This method can be overridden to provide useful information.  It's good practice to call "return super(MastermindServerTCP,self).callback_connect()" at the end of your override.
#        .callback_disconnect():
#            --Called when the server disconnects (i.e., when .disconnect(...) is called).  This method can be overridden to provide useful information.  It's good practice to call "return super(MastermindServerTCP,self).callback_disconnect()" at the end of your override.
#        .callback_connect_client(connection_object):
#            --Called when a new client connects.  This method can be overridden to provide useful information.  It's good practice to call "return super(MastermindServerTCP,self).callback_connect_client(connection_object)" at the end of your override.
#            --The argument "connection_object" represents the appropriate connection.  See the "Connection Objects" section for a description of useful properites.
#        .callback_disconnect_client(connection_object):
#            --Called when a client disconnects.  This method can be overridden to provide useful information.  It's good practice to call "return super(MastermindServerTCP,self).callback_disconnect_client(connection_object)" at the end of your override.
#            --The argument "connection_object" represents the appropriate connection.  See the "Connection Objects" section for a description of useful properites.
#        .callback_client_receive(connection_object):
#            --Called when data is about to be received from a connection.  A pickling or zlib error from Python is conceivable if the data is corrupted in transit.  This method can be overridden to provide useful information.  It's good practice (and in this case essential) to call "return super(MastermindServerTCP,self).callback_client_receive(connection_object)" at the end of your override.
#            --The argument "connection_object" represents the appropriate connection.  See the "Connection Objects" section for a description of useful properites.
#        .callback_client_handle(connection_object,data):
#            --Called to handle data received from a connection.  This method is often overridden to provide custom server logic and useful information.  It's good practice (and in this case essential) to call "return super(MastermindServerTCP,self).callback_client_handle(connection_object,data)" at the end of your override.
#            --The argument "connection_object" represents the appropriate connection.  See the "Connection Objects" section for a description of useful properites.
#            --The argument "data" is the data that the server received from the connection.
#        .callback_client_send(connection_object,data,compression=None):
#            --Called to when data is about to be sent to a connection.  If sending fails, the connection is silently terminated.  This method can be overridden to provide useful information.  It's good practice (and in this case essential) to call "return super(MastermindServerTCP,self).callback_client_send(connection_object,data,compression)" at the end of your override.
#            --The argument "connection_object" represents the appropriate connection.  See the "Connection Objects" section for a description of useful properites.
#            --The argument "data" is the data that the server is about to send to the connection.
#            --The argument "compression" determines whether the data should be compressed before sending.  See MastermindClientTCP.send(...).
#        .accepting_allow():
#            --Starts allowing clients to connect and create new connections to the server.
#        .accepting_allow_wait_forever():
#            --Uses the current thread to wait for new connections to the server and put them in their own threads.  This is used internally by .accepting_allow(), but is useful by itself if you want to start your own server in its own file, and you don't care if you don't get control back.
#        .accepting_disallow():
#            --Stops allowing new clients to connect.  This DOES NOT stop any current connections!  The effect of calling .accepting_allow() after this and then having a new client connect has not been tested.


class Planet():
        def __init__(self):
                self.ownership = None
                self.coord   = [0,0]
                self.initpop = 1000
                self.popul   = 1000
                self.maxpop  = 10000
                self.popgrowthrate = 0.33 #sigmoidal

        def locateto(self, xpos, ypos):
                self.coord   = [xpos, ypos]

        def popgrow(self):
                #Logistic Population Growth: Continuous and Discrete
                #http://amrita.vlab.co.in/?sub=3&brch=65&sim=1110&cnt=1
                self.popul  = self.popul+ int(math.ceil(self.popgrowthrate * ((self.popul-self.initpop+2)*(1-((self.popul-self.initpop+1)/(self.maxpop-self.initpop))))-0.5))

class Spaceship():
        def __init__(self):
                self.ownership = None
                self.coord    = [0,0]
                self.ucount   = 100
                self.gocoord  = [0,0]
                self.moveleft = 1
                self.justsplit = False

        def locateto(self, xpos, ypos):
                self.coord    = [xpos, ypos]
                self.gocoord  = [xpos, ypos]

class Game:
    def __init__(self, player0, currentIndex):
        print("This is NEW game.")
        self.boardsize = [1,1]
        self.maxplayer = 1
        # whose turn (1 or 0)
        self.turn = 0
        #maps
        self.board        = [[0 for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
        self.planetlist   = []
        self.shiplist     = []
        #initialize the players including the one who started the game
        self.player0=player0
        self.player1=None
        self.playerlist = []
        self.playerlist.append(self.player0)
        self.allconnectcensus = 1
        self.colorlist = PlayerColour(self.allconnectcensus,[])
        self.colorlist = self.colorlist[0]
        print(self.colorlist)
        #gameid of game
        self.gameid=currentIndex

    def populate(self):
        if len(self.planetlist)<1 and self.boardsize[0]>0 and self.boardsize[1]>0:
            print("Distribute planet locations")
            coorddraw = random.sample(range(self.boardsize[0]*self.boardsize[1]), math.floor((self.boardsize[0]*self.boardsize[1])*0.1))
            for i in range(len(coorddraw)):
                #print(i, "\t", int(math.floor(i/self.boardsize[0])), " x ", self.boardsize[0], " + ", int(math.fmod(i,self.boardsize[0])))
                self.planetlist.append(Planet())
                self.planetlist[i].locateto(int(math.fmod(coorddraw[i],self.boardsize[0])), int(math.floor(coorddraw[i]/self.boardsize[0])))
                self.planetlist[i].ownership = None
        for i in range(len(self.playerlist)):
            planetowner = False
            for k in self.planetlist:
                if k.ownership == self.playerlist[i]:
                    planetowner = True
            if not planetowner and i<len(self.planetlist):
                print("Allocate home planet")
                self.planetlist[i].ownership = self.playerlist[i]
                planetowner = True
            
            shipowner = False
            for k in self.shiplist:
                if k.ownership == self.playerlist[i]:
                    shipowner = True
            if not shipowner:
                print("Allocate initial ship", self.playerlist[i])
                if planetowner:
                    self.shiplist.append(Spaceship())
                    self.shiplist[len(self.shiplist)-1].locateto(self.planetlist[i].coord[0], self.planetlist[i].coord[1])
                    self.shiplist[len(self.shiplist)-1].ownership = self.playerlist[i]
                else:
                    coorddraw = random.sample(range(self.boardsize[0]*self.boardsize[1]), math.floor(self.boardsize[0]*self.boardsize[1]))
                    for k in range(len(coorddraw)):
                        emptytile = True
                        for m in self.shiplist:
                            if m.coord[0] == int(math.fmod(coorddraw[k],self.boardsize[0])) and m.coord[1] == int(math.floor(coorddraw[k]/self.boardsize[0])):
                                emptytile = False
                        for m in self.planetlist:
                            if m.coord[0] == int(math.fmod(coorddraw[k],self.boardsize[0])) and m.coord[1] == int(math.floor(coorddraw[k]/self.boardsize[0])):
                                emptytile = False
                        if emptytile:
                            self.shiplist.append(Spaceship())
                            self.shiplist[len(self.shiplist)-1].locateto(int(math.fmod(coorddraw[k],self.boardsize[0])), int(math.floor(coorddraw[k]/self.boardsize[0])))
                            self.shiplist[len(self.shiplist)-1].ownership = self.playerlist[i]
                            break


if __name__ == "__main__":
    server = P4X_Server()
    server.connect(server_ip,port)
    try:
        server.accepting_allow_wait_forever()
    except:
        #Only way to break is with an exception
        pass
    server.accepting_disallow()
    server.disconnect_clients()
    server.disconnect()
