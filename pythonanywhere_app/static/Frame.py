#! /usr/bin/env python
#ant1 201411

import browser
import math
from browser import document as doc
from browser.timer import request_animation_frame as raf
from browser import svg
from browser import ajax


def IsOneTileMove(x1,y1,x2,y2):
        if (abs(x1-x2)==1 and y1==y2) or (x1==x2 and abs(y1-y2)==1):
                return True
        else:
                return False

### SUPPORT CLASSES
class P4X_Spaceship():
    def __init__(self):
        self.ownership = None
        self.coord     = [2,2]
        self.ucount    = 100
        self.gocoord   = self.coord
        self.moveleft  = 1
        self.justsplit = False

class P4X_Planet():
    def __init__(self):
        self.ownership = None
        self.coord     = [1,1]
        self.initpop   = 1000
        self.popul     = self.initpop

class Planets4Xgame():
        def __init__(self):
                self.multiplayer = False
                self.session_id  = None
                self.boardsize   = [30, 30]
                self.boardscale  = 50
                self.owncolorid  = [0,255,0]
                if math.floor(browser.window.innerWidth/self.boardsize[0]) < math.floor(browser.window.innerHeight/self.boardsize[1]):
                        self.boardscale  = math.floor(browser.window.innerWidth/(self.boardsize[0]+1))
                else:
                        self.boardscale  = math.floor(browser.window.innerHeight/(self.boardsize[1]+1))
                if self.boardscale < 10: self.boardscale = 10

                self.planetlist = []
                self.shiplist   = []

                req = ajax.ajax()
                req.bind('complete',self.joingame)
                req.open('POST',"/newcomer",False)
                req.set_header('content-type','application/x-www-form-urlencoded')
                req.send({'action':'joingame', 'boardsizex':str(self.boardsize[0]), 'boardsizey':str(self.boardsize[1])})

                self.drawBoard()
                self.newPan.bind('click', self.click)

        def joingame(self, req):
            self.multiplayer = False
            self.session_id  = None
            self.planetlist.append( P4X_Planet() )
            self.shiplist.append( P4X_Spaceship() )
            if req.status==200:
                self.multiplayer = True
                dico = eval(req.text)
                if dico["action"] == "welcome":
                    self.session_id = dico["session_id"]
                    self.owncolorid = [int(dico["colorid_r"]),int(dico["colorid_g"]),int(dico["colorid_b"])]
                    self.boardsize  = [int(dico["boardsizex"]), int(dico["boardsizey"])]
                    self.planetlist[len(self.planetlist)-1].coord = [int(dico["homeplanetx"]),int(dico["homeplanety"])]
            self.shiplist[len(self.shiplist)-1].coord = self.planetlist[len(self.planetlist)-1].coord
            self.planetlist[len(self.planetlist)-1].ownership = self.owncolorid
            self.shiplist[len(self.shiplist)-1].ownership = self.owncolorid
#            print("session_id: ", self.session_id)
#            print("game_id: ", int(dico["game_id"]))
#            print("freeplanets: ", int(dico["freeplanets"]))
#            print("players: ", int(dico["players"]))
            print("homeplanet", self.planetlist[len(self.planetlist)-1].coord)


        def click(self, ev):
            cx = math.floor((ev.clientX/self.boardscale)-0.5)
            cy = math.floor((ev.clientY/self.boardscale)-0.5)
            if self.multiplayer and self.session_id != None:
                req = ajax.ajax()
                req.bind('complete', self.moveover)
                req.open('POST',"/clickonboard",True)
                req.set_header('content-type','application/x-www-form-urlencoded')
                req.send({"action":"clickonboard", "session_id":str(self.session_id), "clickx":str(cx), "clicky":str(cy)})
            else:
                for k in self.shiplist:
                    if IsOneTileMove(k.coord[0], k.coord[1], cx, cy):
                        k.coord = [cx,cy]

        def moveover(self, req):
            if req.status==200:
                dico = eval(req.text)
                if dico["action"] == "moveover" and dico["session_id"] == self.session_id:
                    for k in self.shiplist:
                        k.coord = [int(dico["clickx"]), int(dico["clicky"])]

        def drawBoard(self):
                self.newPan = doc.createElementNS("http://www.w3.org/2000/svg","svg")
                self.newPan.setAttribute("width",self.boardsize[0]*self.boardscale)
                self.newPan.setAttribute("height",self.boardsize[1]*self.boardscale)
                self.newPan.setAttribute("style","background-color:rgb(0,0,0);border-style:solid;border-width:1;border-color:#000;")
                currentDiv = doc.getElementById("div")
                for x in range(self.boardsize[0]-1):
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke="brown")
                        line.setAttribute("x1",(x+1)*self.boardscale)
                        line.setAttribute("x2",(x+1)*self.boardscale)
                        line.setAttribute("y1", 0 )
                        line.setAttribute("y2", self.boardsize[1]*self.boardscale)
                        line.setAttribute("stroke-opacity", .2)
                        self.newPan.appendChild( line )
                for x in range(self.boardsize[1]-1):
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke="brown")
                        line.setAttribute("x1", 0 )
                        line.setAttribute("x2", self.boardsize[0]*self.boardscale)
                        line.setAttribute("y1",(x+1)*self.boardscale)
                        line.setAttribute("y2",(x+1)*self.boardscale)
                        line.setAttribute("stroke-opacity", .2)
                        self.newPan.appendChild( line )

                for k in self.shiplist:
                        temp = "rgb("+str(self.owncolorid[0])+","+str(self.owncolorid[1])+","+str(self.owncolorid[2])+")"
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke=temp)
                        line.setAttribute("x1", k.coord[0]*self.boardscale )
                        line.setAttribute("x2", (k.coord[0]+1)*self.boardscale )
                        line.setAttribute("y1", k.coord[1]*self.boardscale )
                        line.setAttribute("y2", (k.coord[1]+1)*self.boardscale )
                        line.setAttribute("stroke-width", 5)
                        self.newPan.appendChild( line )
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke=temp)
                        line.setAttribute("x1", k.coord[0]*self.boardscale )
                        line.setAttribute("x2", (k.coord[0]+1)*self.boardscale )
                        line.setAttribute("y1", (k.coord[1]+1)*self.boardscale )
                        line.setAttribute("y2", k.coord[1]*self.boardscale )
                        line.setAttribute("stroke-width", 5)
                        self.newPan.appendChild( line )

                doc.body.insertBefore(self.newPan, currentDiv)

        def moveAlong(self):
                for k in self.shiplist:
                        criss = False
                        for j in range(self.newPan.childElementCount):
                                temp = "rgb("+str(self.owncolorid[0])+","+str(self.owncolorid[1])+","+str(self.owncolorid[2])+")"
                                if self.newPan.children[j].getAttribute("stroke")==temp:
                                        if not criss:
                                                self.newPan.children[j].setAttribute("x1", k.coord[0]*self.boardscale )
                                                self.newPan.children[j].setAttribute("x2", (k.coord[0]+1)*self.boardscale )
                                                self.newPan.children[j].setAttribute("y1", k.coord[1]*self.boardscale )
                                                self.newPan.children[j].setAttribute("y2", (k.coord[1]+1)*self.boardscale )
                                                criss = True
                                        else:
                                                self.newPan.children[j].setAttribute("x1", k.coord[0]*self.boardscale )
                                                self.newPan.children[j].setAttribute("x2", (k.coord[0]+1)*self.boardscale )
                                                self.newPan.children[j].setAttribute("y1", (k.coord[1]+1)*self.boardscale )
                                                self.newPan.children[j].setAttribute("y2", k.coord[1]*self.boardscale )
                                                criss = False

        def update(self,i):
                raf(self.update)
                self.moveAlong()

p4x=Planets4Xgame() #__init__ is called right here
p4x.update(0)

