#! /usr/bin/env python
#ant1 201410

import math
import random
import pygame
from PIL import Image
from ImageSupport import *

import traceback

from mastermind_import import *
from settings import *
import server

from time import time, sleep

client = None
box_server = None

already_printed_messages = [None]*scrollback

ip = "localhost"
port = 6317

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

class Planet():
        def __init__(self):
                self.coord   = [0,0]
                self.initpop = 1000
                self.popul   = 1000
                self.maxpop  = 10000
                self.popgrowthrate = 0.33 #sigmoidal
                self.known   = False
                self.owned   = False

        def locateto(self, xpos, ypos):
                self.coord   = [xpos, ypos]

        def popgrow(self):
                #Logistic Population Growth: Continuous and Discrete
                #http://amrita.vlab.co.in/?sub=3&brch=65&sim=1110&cnt=1
                self.popul  = self.popul+ int(math.ceil(self.popgrowthrate * ((self.popul-self.initpop+2)*(1-((self.popul-self.initpop+1)/(self.maxpop-self.initpop))))-0.5))

class Spaceship():
        def __init__(self):
                self.coord    = [0,0]
                self.ucount   = 100
                self.gocoord  = [0,0]
                self.moveleft = 1
                self.justsplit = False

        def locateto(self, xpos, ypos):
                self.coord    = [xpos, ypos]
                self.gocoord  = [xpos, ypos]

class Planets4XGame():        
        def initGraphics(self):
                self.edgepixel         = pygame.image.load("EdgePixel.png").convert(24)
                self.edgepixel.set_alpha(32)
                tempicon               = Image.open("EdgePixel.png")
                tempicon.convert("RGBA")
                tempicon = ColorSwitch(tempicon, [255, 127, 39, 255], self.teamcolor)
                tempicon = ColorAsAlpha(tempicon, self.teamcolor, 196)
                self.ownborderpixel = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                tempicon = ColorAsAlpha(tempicon, self.teamcolor, 64)
                self.ownedgepixel = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                tempicon               = Image.open("NewTurnButton.png")
                tempicon.convert("RGBA")
                tempicon = ColorAsAlpha(tempicon, [255, 255, 255], 0)
                tempicon = ColorSwitch(tempicon, [0, 0, 0, 255], [255,127,39])
                tempicon = ColorSwitch(tempicon, [127, 127, 127, 255], [127,64,19])
                self.newturnbutton = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                
                self.shipicon          = self.loadP4Xicon("Ship.png", self.teamcolor)
                tempicon               = Image.open("Ship.png")
                tempicon = ColorAsAlpha(tempicon, [255, 255, 255], 0)
                self.inorbiticon = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                tempicon = ColorSwitch(tempicon, [0, 0, 0, 255], self.teamcolor)
                if self.boardscale/(2*tempicon.size[0])>1 and self.boardscale/(2*tempicon.size[1])>1:                        
                        if self.boardscale/(2*tempicon.size[1])<self.boardscale/(2*tempicon.size[0]):                                
                                tempicon = DisplayZoom( tempicon, math.floor(self.boardscale/(2*tempicon.size[1])) )
                        else:
                                tempicon = DisplayZoom( tempicon, math.floor(self.boardscale/(2*tempicon.size[0])) )
                self.smallcrewicon = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                tempicon = ColorAsAlpha(tempicon, self.teamcolor, 128)
                self.smallcrewnofuel = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                tempicon               = Image.open("Ship.png")
                tempicon = ColorAsAlpha(tempicon, [255, 255, 255], 0)
                tempicon = ColorSwitch(tempicon, [0, 0, 0, 255], self.teamcolor)
                tempicon = ColorAsAlpha(tempicon, self.teamcolor, 128)
                if self.boardscale/tempicon.size[0]>1 and self.boardscale/tempicon.size[1]>1:                        
                        if self.boardscale/tempicon.size[1]<self.boardscale/tempicon.size[0]:                                
                                tempicon = DisplayZoom( tempicon, math.floor(self.boardscale/tempicon.size[1]) )
                        else:
                                tempicon = DisplayZoom( tempicon, math.floor(self.boardscale/tempicon.size[0]) )
                self.nofuelshipicon = pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)
                self.ownplaneticon     = self.loadP4Xicon("Planet.png", self.teamcolor)
                self.neutralplaneticon = self.loadP4Xicon("Planet.png", [128, 128, 128])

        def populate(self):
                self.boardoffset  = [math.floor((self.width-self.boardsize[0]*self.boardscale)/2), math.floor((self.height-self.boardsize[1]*self.boardscale)/2)]
                self.board        = [[False for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
                self.boardcontrol = [[False for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
                self.planetscoord = [[False for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
                self.planetlist   = []
                coorddraw = random.sample(range(self.boardsize[0]*self.boardsize[1]), math.floor((self.boardsize[0]*self.boardsize[1])*self.planetdensity))
                for i in range(len(coorddraw)):
                        #print(i, "\t", int(math.floor(i/self.boardsize[0])), " x ", self.boardsize[0], " + ", int(math.fmod(i,self.boardsize[0])))
                        self.planetlist.append(Planet())
                        self.planetlist[i].locateto(int(math.fmod(coorddraw[i],self.boardsize[0])), int(math.floor(coorddraw[i]/self.boardsize[0])))
                        self.planetscoord[self.planetlist[i].coord[1]][self.planetlist[i].coord[0]] = True
                self.shiplist     = []
                self.shiplist.append(Spaceship())
                self.shiplist[0].locateto(self.planetlist[0].coord[0], self.planetlist[0].coord[1])
                self.planetlist[0].owned = True
                self.board[self.planetlist[0].coord[1]][self.planetlist[0].coord[0]] = True
                self.boardcontrol[self.shiplist[0].coord[1]][self.shiplist[0].coord[0]] = True

        def __init__(self):
                pass
                #1
                pygame.init()
                pygame.font.init()
                width, height = 389, 489
                self.width = width
                self.height = height
                #2
                #initialize the screen
                self.screen = pygame.display.set_mode((width, height))
                pygame.display.set_caption("Planets4X")
                #3
                #initialize pygame clock
                self.clock=pygame.time.Clock()

                self.playerID     = 1
                self.teamcolor    = [0, 0, 255]
                self.boardscale   = 30
                self.planetdensity = 0.1
                self.boardsize    = [math.floor(self.width/self.boardscale), math.floor(self.height/self.boardscale)]
                self.populate()

                #connect to server
                global server
                self.client = MastermindClientTCP(client_timeout_connect,client_timeout_receive)
                try:
                    print("Client connecting on \""+client_ip+"\", port "+str(port)+" . . .")
                    self.client.connect(client_ip,port)
                    self.connection_status = True
                    print("Client connected!")
                    self.client.send(["gamesetup", {"htiles":self.boardsize[0],"vtiles":self.boardsize[1],"maxplayer":3}], None)
                    reply = self.client.receive(True)
                    if not reply == None and reply["action"]=="joingame":
                            self.playerID = reply["player"]
                            self.teamcolor = reply["playercolor"]
                            self.boardsize = [reply["htiles"], reply["vtiles"]]
                            if math.floor(self.width/self.boardsize[0]) < math.floor(self.height/self.boardsize[1]):
                                    self.boardscale  = math.floor(self.width/(self.boardsize[0]+1))
                            else:
                                    self.boardscale  = math.floor(self.height/(self.boardsize[1]+1))
                            self.boardoffset  = [math.floor((self.width-self.boardsize[0]*self.boardscale)/2), math.floor((self.height-self.boardsize[1]*self.boardscale)/2)]
                            self.board        = [[False for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
                            self.boardcontrol = [[False for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
                            self.planetscoord = [[False for x in range(self.boardsize[0])] for y in range(self.boardsize[1])]
                            self.planetlist   = []
                            self.shiplist     = []
                            reply = self.client.receive(True)
                            if not reply == None and reply["action"]=="allocate" and reply["object"]=="planet":
                                self.planetlist.append(Planet())
                                self.planetlist[len(self.planetlist)-1].locateto(reply["xcoord"], reply["ycoord"])
                                self.planetscoord[self.planetlist[len(self.planetlist)-1].coord[1]][self.planetlist[len(self.planetlist)-1].coord[0]] = True
                                self.planetlist[len(self.planetlist)-1].owned = True                                
                                self.boardcontrol[self.planetlist[len(self.planetlist)-1].coord[1]][self.planetlist[len(self.planetlist)-1].coord[0]] = True
                            reply = self.client.receive(True)
                            if not reply == None and reply["action"]=="allocate" and reply["object"]=="spaceship":
                                    self.shiplist.append(Spaceship())
                                    self.shiplist[len(self.shiplist)-1].locateto(reply["xcoord"], reply["ycoord"])
                                    self.board[self.shiplist[len(self.shiplist)-1].coord[1]][self.shiplist[len(self.shiplist)-1].coord[0]] = True
                                    self.boardcontrol[self.shiplist[len(self.shiplist)-1].coord[1]][self.shiplist[len(self.shiplist)-1].coord[0]] = True
                            print("I am player nb:", self.playerID)
                            
                except MastermindError:
                    print("No server found, playing single-player locally")
                    self.connection_status = False
                    #print("No server found; starting server!")                    
                    #server = P4X_server.BoxesServer()
                    #server.connect(server_ip,port)
                    #server.accepting_allow()

                    #print("Client connecting on \""+client_ip+"\", port "+str(port)+" . . .")
                    #self.client.connect(client_ip,port)
                
                self.latestbeat = pygame.time.get_ticks()
                
                #initialize the graphics
                self.initGraphics()

        def loadP4Xicon(self, iconpath, MainColor):
                tempicon = Image.open(iconpath)
                tempicon.convert("RGBA")
                tempicon = ColorAsAlpha(tempicon, [255, 255, 255], 0)
                tempicon = ColorSwitch(tempicon, [0, 0, 0, 255], MainColor)
                if self.boardscale/tempicon.size[0]>1 and self.boardscale/tempicon.size[1]>1:                        
                        if self.boardscale/tempicon.size[1]<self.boardscale/tempicon.size[0]:                                
                                tempicon = DisplayZoom( tempicon, math.floor(self.boardscale/tempicon.size[1]) )
                        else:
                                tempicon = DisplayZoom( tempicon, math.floor(self.boardscale/tempicon.size[0]) )
                return pygame.image.frombuffer(tempicon.tostring(), tempicon.size, tempicon.mode)

        def GenNewTurn(self):
                for k in self.shiplist:
                        k.moveleft = 1
                for k in self.planetlist:
                        k.popgrow()
                        if k.popul > 1000: k.initpop = 1000
                        if k.owned and math.floor(((k.popul/k.maxpop)-0.1)*10)>0:
                                self.shiplist.append(Spaceship())
                                self.shiplist[len(self.shiplist)-1].ucount = math.floor(((k.popul/k.maxpop)-0.1)*10)
                                self.shiplist[len(self.shiplist)-1].locateto(k.coord[0],k.coord[1])
                                k.popul = k.popul - 2

        def planetaryBattle(self, planet, ship):
                if planet.coord[0]==ship.coord[0] and planet.coord[1]==ship.coord[1] and not planet.owned:
                        planetreport = []
                        shipreport   = []
                        print("\n Planetary battle ", ship.ucount ," VS. ", planet.popul)
                        while not planet.owned and ship.ucount>0:
                                planetreport.append(planet.popul)
                                shipreport.append(ship.ucount)
                                shipengageunit = random.randint(1,math.ceil(ship.ucount/2))
                                balanceofpower = planet.popul/ship.ucount
                                outcome = random.randint(1,100)
                                if random.randint(1,10000) == 1:
                                        print("Miraculous victory due to heroic action.")
                                        planet.owned = True
                                elif outcome < 25*(shipengageunit/ship.ucount):
                                        if ship.ucount > shipengageunit:
                                                ship.ucount = ship.ucount - shipengageunit
                                        else:
                                                ship.ucount = 0
                                        if random.randint(1,planet.popul) < math.ceil(shipengageunit * (balanceofpower/5)):
                                                planet.owned = True
                                                print("Victory by overwhelmingness")
                                                ship.ucount = ship.ucount + shipengageunit
                                        if planet.popul > math.ceil(shipengageunit * (balanceofpower/5)):
                                                planet.popul = planet.popul - math.ceil(shipengageunit * (balanceofpower/5))
                                        else:
                                                planet.popul = 1
                                                planet.owned = True
                                                print("Victory by attrition")
                                        print("won ", shipengageunit, "\tvs.\t", math.ceil(shipengageunit * (balanceofpower/5)))
                                        if planet.popul < planet.initpop:
                                                planet.initpop = planet.popul
                                else:
                                        if ship.ucount > shipengageunit:
                                                ship.ucount = ship.ucount - shipengageunit
                                        else:
                                                ship.ucount = 0
                                        if planet.popul > int(shipengageunit * (balanceofpower/20)):
                                                planet.popul = planet.popul - int(shipengageunit * (balanceofpower/20))
                                        else:
                                                planet.popul = 1
                                                planet.owned = True
                                                print("Victory by attrition")
                                                ship.ucount = ship.ucount + shipengageunit
                                        print("lost", shipengageunit, "\tvs.\t", int(shipengageunit * (balanceofpower/20)))
                                        if planet.popul < planet.initpop:
                                                planet.initpop = planet.popul
                        if ship.ucount < 1:
                                print("Ship destroyed")
                                self.shiplist.remove(ship)
                        thefile = open('battlereports.txt', 'a')
                        for item in planetreport: thefile.write("%s\t" % str(item))
                        thefile.write("NaN\n")
                        for item in shipreport: thefile.write("%s\t" % str(item))
                        thefile.write("NaN\n")
                        thefile.close()
                        print()

        def shipCanWrap(self, ship, xpos, ypos):
                #print()
                #print("Wrap checking", ship.coord[0], "x", ship.coord[1], " VS. ", xpos, "x", ypos, "   control=", self.boardcontrol[ypos][xpos], "     planet=", self.planetscoord[ypos][xpos])
                isdeepspace = True
                wrapinit = []
                wrapdest = []
                if ship.coord[0]==xpos and ship.coord[1]!=ypos and self.boardcontrol[ypos][xpos] and not self.planetscoord[ypos][xpos] and not self.planetscoord[ship.coord[1]][ship.coord[0]]:
                        if ship.coord[1]>ypos:
                                wrapinit = ypos
                                wrapdest = ship.coord[1]
                        else:
                                wrapinit = ship.coord[1]
                                wrapdest = ypos
                        for cursor in range(1,wrapdest-wrapinit):
                                for k in self.shiplist:
                                        if k!=ship and (k.coord[1] == wrapinit+cursor and k.coord[0] == xpos) or not self.boardcontrol[wrapinit+cursor][xpos]:
                                                isdeepspace = False
                                                #print(isdeepspace, " ", xpos, "x", wrapinit+cursor, " ship in the way.")
                                for k in self.planetlist:
                                         if (k.coord[1] == wrapinit+cursor and k.coord[0] == xpos) or not self.boardcontrol[wrapinit+cursor][xpos]:
                                                isdeepspace = False
                                                #print(isdeepspace, " ", xpos, "x", wrapinit+cursor, " planet in the way.")
                                #if isdeepspace: print(isdeepspace, " ", wrapinit+cursor, "x", ypos, " no obstacle")
                elif ship.coord[1] == ypos and ship.coord[0]!=xpos and self.boardcontrol[ypos][xpos] and not self.planetscoord[ypos][xpos] and not self.planetscoord[ship.coord[1]][ship.coord[0]]:
                        if ship.coord[0]>xpos:
                                wrapinit = xpos
                                wrapdest = ship.coord[0]
                        else:
                                wrapinit = ship.coord[0]
                                wrapdest = xpos
                        for cursor in range(1,wrapdest-wrapinit):
                                for k in self.shiplist:
                                        if k!=ship and (k.coord[0] == wrapinit+cursor and k.coord[1] == ypos) or not self.boardcontrol[ypos][wrapinit+cursor]:
                                                isdeepspace = False
                                                #print(isdeepspace, " ", wrapinit+cursor, "x", ypos, " ship in the way.")
                                for k in self.planetlist:
                                         if (k.coord[0] == wrapinit+cursor and k.coord[1] == ypos) or not self.boardcontrol[ypos][wrapinit+cursor]:
                                                isdeepspace = False
                                                #print(isdeepspace, " ", wrapinit+cursor, "x", ypos, " planet in the way.")
                                #if isdeepspace: print(isdeepspace, " ", wrapinit+cursor, "x", ypos, " no obstacle")
                else:
                        return False
                        pass
                return isdeepspace

        def drawBoard(self):
                for x in range(self.boardsize[0]*self.boardscale):
                        for y in range(self.boardsize[1]):
                                if y>0:
                                        self.screen.blit(self.edgepixel, [self.boardoffset[0]+x, self.boardoffset[1]+y*self.boardscale])
                for y in range(self.boardsize[1]*self.boardscale):
                        for x in range(self.boardsize[0]):
                                if x>0:
                                        self.screen.blit(self.edgepixel, [self.boardoffset[0]+x*self.boardscale, self.boardoffset[1]+y])

                # Merge ships having identical location and solve planetary battles
                for k in self.shiplist:
                        k.justsplit = False
                        for m in self.shiplist:
                                if m!=k and k.coord[0]==m.coord[0] and k.coord[1]==m.coord[1]:
                                        k.ucount = k.ucount + m.ucount
                                        self.shiplist.remove(m)
                        for m in self.planetlist:
                                if k.coord[0]==m.coord[0] and k.coord[1]==m.coord[1] and not m.owned:
                                        self.planetaryBattle(m,k)
                
                for x in range(self.boardsize[0]):
                        for y in range(self.boardsize[1]):
                                if self.boardcontrol[y][x]:
                                        try:
                                                if not self.boardcontrol[y-1][x]:
                                                        for xx in range(self.boardscale):
                                                                self.screen.blit(self.ownborderpixel, [self.boardoffset[0]+x*self.boardscale+xx, self.boardoffset[1]+y*self.boardscale])
                                                else:
                                                        for xx in range(self.boardscale):
                                                                self.screen.blit(self.ownedgepixel, [self.boardoffset[0]+x*self.boardscale+xx, self.boardoffset[1]+y*self.boardscale])            
                                        except:
                                                pass
                                        try:
                                                if not self.boardcontrol[y+1][x]:
                                                        for xx in range(self.boardscale):
                                                                self.screen.blit(self.ownborderpixel, [self.boardoffset[0]+x*self.boardscale+xx, self.boardoffset[1]+(y+1)*self.boardscale])
                                                else:
                                                        for xx in range(self.boardscale):
                                                                self.screen.blit(self.ownedgepixel, [self.boardoffset[0]+x*self.boardscale+xx, self.boardoffset[1]+(y+1)*self.boardscale])
                                        except:
                                                pass
                                        try:
                                                if not self.boardcontrol[y][x-1]:
                                                        for yy in range(self.boardscale):
                                                                self.screen.blit(self.ownborderpixel, [self.boardoffset[0]+x*self.boardscale, self.boardoffset[1]+y*self.boardscale+yy])
                                                else:
                                                        for yy in range(self.boardscale):
                                                                self.screen.blit(self.ownedgepixel, [self.boardoffset[0]+x*self.boardscale, self.boardoffset[1]+y*self.boardscale+yy])
                                        except:
                                                pass
                                        try:
                                                if not self.boardcontrol[y][x+1]:
                                                        for yy in range(self.boardscale):
                                                                self.screen.blit(self.ownborderpixel, [self.boardoffset[0]+(x+1)*self.boardscale, self.boardoffset[1]+y*self.boardscale+yy])
                                                else:
                                                        for yy in range(self.boardscale):
                                                                self.screen.blit(self.ownedgepixel, [self.boardoffset[0]+(x+1)*self.boardscale, self.boardoffset[1]+y*self.boardscale+yy])
                                        except:
                                                pass


                                mincrewcount = 0
                                maxcrewcount = 0
                                thiscrewcount = 0
                                nofuelleft = True
                                self.board[y][x] = False
                                for k in range(len(self.shiplist)):
                                        if mincrewcount>self.shiplist[k].ucount: mincrewcount = self.shiplist[k].ucount
                                        if maxcrewcount == 0 or maxcrewcount<self.shiplist[k].ucount: maxcrewcount = self.shiplist[k].ucount
                                        if self.shiplist[k].coord[0] == x and self.shiplist[k].coord[1] == y:
                                                self.board[y][x] = True
                                                thiscrewcount = self.shiplist[k].ucount
                                                if self.shiplist[k].moveleft>0:
                                                        nofuelleft = False
                                midcrewcount = math.floor((mincrewcount+maxcrewcount)/2)
 
                                isinsight = False
                                if self.planetscoord[y][x]:
                                        try:
                                                if self.board[y-1][x]:
                                                        isinsight = True
                                        except:
                                                pass
                                        try:
                                                if self.board[y+1][x]:
                                                        isinsight = True
                                        except:
                                                pass
                                        try:
                                                if self.board[y][x-1]:
                                                        isinsight = True
                                        except:
                                                pass
                                        try:
                                                if self.board[y][x+1]:
                                                        isinsight = True
                                        except:
                                                pass
                                knownplanet = False
                                ownedplanet = False
                                for k in range(len(self.planetlist)):
                                        if self.planetlist[k].coord[0] == x and self.planetlist[k].coord[1] == y and self.planetlist[k].owned:
                                                knownplanet = True
                                                ownedplanet = True
                                        elif self.planetlist[k].coord[0] == x and self.planetlist[k].coord[1] == y and self.planetlist[k].known:
                                                knownplanet = True
                                if ownedplanet:
                                        iconsize = self.ownplaneticon.get_size()
                                        self.screen.blit(self.ownplaneticon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                elif knownplanet:
                                        iconsize = self.neutralplaneticon.get_size()
                                        self.screen.blit(self.neutralplaneticon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                if self.planetscoord[y][x] and self.board[y][x]:
                                        for k in range(len(self.planetlist)):
                                                if self.planetlist[k].coord[0] == x and self.planetlist[k].coord[1] == y:
                                                        self.planetlist[k].known = True                                                        
                                                        self.planetlist[k].owned = True
                                        iconsize = self.ownplaneticon.get_size()
                                        self.screen.blit(self.ownplaneticon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                        iconsize = self.inorbiticon.get_size()
                                        if iconsize[0]<self.boardscale/2 and iconsize[1]<self.boardscale/2:
                                                offset = int(self.boardscale/iconsize[0])
                                                self.screen.blit(self.inorbiticon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2+offset, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2+offset])
                                        else:
                                                self.screen.blit(self.inorbiticon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])                                                
                                elif self.planetscoord[y][x] and isinsight and not ownedplanet:
                                        for k in range(len(self.planetlist)):
                                                if self.planetlist[k].coord[0] == x and self.planetlist[k].coord[1] == y:
                                                        self.planetlist[k].known = True
                                        iconsize = self.neutralplaneticon.get_size()
                                        self.screen.blit(self.neutralplaneticon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                elif self.board[y][x]:
                                        if thiscrewcount<midcrewcount:
                                                if nofuelleft:
                                                        iconsize = self.smallcrewnofuel.get_size()
                                                        self.screen.blit(self.smallcrewnofuel, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                                else:
                                                        iconsize = self.smallcrewicon.get_size()
                                                        self.screen.blit(self.smallcrewicon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                        elif nofuelleft:
                                                iconsize = self.nofuelshipicon.get_size()
                                                self.screen.blit(self.nofuelshipicon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])
                                        else:
                                                iconsize = self.shipicon.get_size()
                                                self.screen.blit(self.shipicon, [self.boardoffset[0]+x*self.boardscale+self.boardscale/2-iconsize[0]/2, self.boardoffset[1]+y*self.boardscale+self.boardscale/2-iconsize[1]/2])

        def drawHUD(self):
                #create font
                myfont = pygame.font.SysFont(None, 14)
                
                knowncount = 0
                ownedcount = 0
                for k in self.planetlist:
                        if k.known: knowncount = knowncount+1
                        if k.owned: ownedcount = ownedcount+1
                moveleft  = 0
                fleetsize = 0
                for k in self.shiplist:
                        moveleft  = moveleft + k.moveleft
                        fleetsize = fleetsize + k.ucount
                #create text surface
                label = myfont.render("~ " + str(fleetsize) + " : " + str(moveleft) + " ~        " + str(ownedcount) + " / " + str(knowncount) + " / " + str(len(self.planetlist)), 1, (255,255,255))                
                #draw surface
                self.screen.blit(label, (5, self.height-10))

                iconsize = self.newturnbutton.get_size()
                self.screen.blit(self.newturnbutton, [self.width-(iconsize[0]+2), self.height-(iconsize[1]+2)])

                if moveleft==0: self.GenNewTurn()

        def update(self):
                if self.connection_status:
                        reply = self.client.receive(False)
                        #if not reply == None : print("in update", reply)
                        if pygame.time.get_ticks()>self.latestbeat+30000:
                                self.client.send(["bip"], None)
                                self.latestbeat = pygame.time.get_ticks()
                
                #sleep to make the game 60 fps
                self.clock.tick(60)
                #clear the screen
                self.screen.fill(0)
                #draw the board
                self.drawBoard()
                self.drawHUD()
         
                for event in pygame.event.get():
                        #quit if the quit button was pressed
                        if event.type == pygame.QUIT:
                                exit()

                #1
                mouse = pygame.mouse.get_pos()
                #2
                xpos = int(math.ceil( (mouse[0] - self.boardoffset[0]) / self.boardscale )) - 1
                ypos = int(math.ceil( (mouse[1] - self.boardoffset[1]) / self.boardscale )) - 1
                #3
                isoutofbounds=False

                #4
                if pygame.mouse.get_pressed()[0]:
                        #Left click
                        try:
                                iconsize = self.newturnbutton.get_size()
                                if mouse[0] >= self.width-(iconsize[0]+2) and mouse[1] >= self.height-(iconsize[1]+2):
                                        #New turn button pressed
                                        self.GenNewTurn()
                                        pass
                                else:
                                        wraplist = []
                                        movefrom = []
                                        for k in self.shiplist:
                                                if IsOneTileMove(k.coord[0], k.coord[1], xpos, ypos) and k.moveleft>0:
                                                        movefrom.append([k.coord[0], k.coord[1]])
                                                        #Move one tile over
                                                        k.locateto(xpos,ypos)
                                                        k.moveleft = k.moveleft - 1
                                                        self.boardcontrol[ypos][xpos] = True
                                                elif self.shipCanWrap(k, xpos, ypos) and k.moveleft>0:                                                        
                                                        wraplist.append(k)
                                        for k in wraplist:
                                                movefrom.append([k.coord[0], k.coord[1]])
                                                #Move on longer distances across own territory
                                                self.board[k.coord[1]][k.coord[0]] = False
                                                k.locateto(xpos,ypos)
                                                k.moveleft = k.moveleft - 1
                                                self.boardcontrol[ypos][xpos] = True
                                        
                                        if self.connection_status and len(movefrom)>0:
                                                print("Transmit move")
                                                self.client.send(["shipmove", {"type":"plain","from":movefrom,"to":[xpos,ypos]}], None)
                                                reply = self.client.receive(True)
                                                if not reply==None and reply["action"]=="upknown" and reply["object"]=="planet":
                                                        for k in reply["list"]:
                                                                prevunknown=True
                                                                for j in self.planetlist:
                                                                        if k[0]==j.coord[0] and k[1]==j.coord[1]:
                                                                                prevunknown=False
                                                                                break
                                                                if prevunknown:
                                                                        self.planetlist.append(Planet())
                                                                        self.planetlist[len(self.planetlist)-1].locateto(k[0], k[1])
                                                                        self.planetscoord[self.planetlist[len(self.planetlist)-1].coord[1]][self.planetlist[len(self.planetlist)-1].coord[0]] = True
                                                                        self.planetlist[len(self.planetlist)-1].known = True
                        except:
                                isoutofbounds=True
                                pass
                        pygame.time.wait(150)
                elif pygame.mouse.get_pressed()[2]:
                        #right click
                        try:
                                reporting = False
                                for k in self.planetlist:
                                        if k.known and k.coord[0] == xpos and k.coord[1] == ypos:
                                                print("planet ", k.popul, " inhabit.\t", k.popgrowthrate, "rate of growth \t@ ", k.coord[0], " x ", k.coord[1])
                                                reporting = True
                                for k in self.shiplist:
                                        if k.coord[0] == xpos and k.coord[1] == ypos:
                                                print("ship   ", k.ucount, " units\t", k.moveleft, "moves left\t@ ", k.coord[0], " x ", k.coord[1])
                                                reporting = True
                                if not reporting:
                                        splitfrom=[]
                                        splitgoto=[]
                                        for k in self.shiplist:
                                                if IsOneTileMove(k.coord[0], k.coord[1], xpos, ypos) and k.moveleft>0 and k.ucount>1 and not k.justsplit:
                                                        self.shiplist.append(Spaceship())
                                                        self.shiplist[len(self.shiplist)-1].locateto(k.coord[0],k.coord[1])
                                                        self.shiplist[len(self.shiplist)-1].ucount    = int(k.ucount - int(k.ucount/2))
                                                        self.shiplist[len(self.shiplist)-1].moveleft  = k.moveleft
                                                        self.shiplist[len(self.shiplist)-1].justsplit = True
                                                        splitfrom.append(self.shiplist[len(self.shiplist)-1])
                                                        k.locateto(xpos,ypos)                                                
                                                        k.ucount    = int(k.ucount/2)
                                                        k.moveleft  = k.moveleft-1
                                                        k.justsplit = True
                                                        self.boardcontrol[ypos][xpos] = True
                                                        splitgoto.append(k)
                                        if self.connection_status and len(splitfrom)>0 and len(splitgoto)>0:
                                                print("Transmit split")
                                                self.client.send(["shipmove", {"type":"split","from":splitfrom,"to":splitgoto}], None)
                                                reply = self.client.receive(True)
                                                if not reply==None and reply["action"]=="upknown" and reply["object"]=="planet":
                                                        for k in reply["list"]:
                                                                prevunknown=True
                                                                for j in self.planetlist:
                                                                        if k[0]==j.coord[0] and k[1]==j.coord[1]:
                                                                                prevunknown=False
                                                                                break
                                                                if prevunknown:
                                                                        self.planetlist.append(Planet())
                                                                        self.planetlist[len(self.planetlist)-1].locateto(k[0], k[1])
                                                                        self.planetscoord[self.planetlist[len(self.planetlist)-1].coord[1]][self.planetlist[len(self.planetlist)-1].coord[0]] = True
                                                                        self.planetlist[len(self.planetlist)-1].known = True
                                                                        #self.board[self.shiplist[len(self.shiplist)-1].coord[1]][self.shiplist[len(self.shiplist)-1].coord[0]] = True
                                                                        #self.boardcontrol[self.shiplist[len(self.shiplist)-1].coord[1]][self.shiplist[len(self.shiplist)-1].coord[0]] = True
                                pygame.time.wait(150)
                        except:
                                pass               
                

                #update the screen
                pygame.display.flip()


p4x=Planets4XGame() #__init__ is called right here
while 1:
    p4x.update()

