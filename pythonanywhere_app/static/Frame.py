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
                self.boardsize   = [8,8]
                self.boardscale  = 50
                self.owncolorid  = [0,255,0]
                self.boardcontrol = []
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
            if req.status==200:
                self.multiplayer = True
                dico = eval(req.text)
                if dico["action"] == "welcome":
                    self.session_id = dico["session_id"]
                    self.owncolorid = [int(dico["colorid_r"]),int(dico["colorid_g"]),int(dico["colorid_b"])]
                    self.boardsize  = [int(dico["boardsizex"]), int(dico["boardsizey"])]
                    self.boardcontrol = [[None for i in range(self.boardsize[1])] for j in range(self.boardsize[0])]

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
                        if k.ownership == self.owncolorid:
                            k.coord = [int(dico["clickx"]), int(dico["clicky"])]

        def drawBoard(self):
                self.newPan = doc.createElementNS("http://www.w3.org/2000/svg","svg")
                self.newPan.setAttribute("width",self.boardsize[0]*self.boardscale)
                self.newPan.setAttribute("height",self.boardsize[1]*self.boardscale)
                self.newPan.setAttribute("style","background-color:rgb(0,0,0);border-style:solid;border-width:1;border-color:#000;")
                currentDiv = doc.getElementById("div")
                temp = temp = "rgb("+str(255)+","+str(127)+","+str(39)+")"
                for x in range(self.boardsize[0]-1):
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke=temp)
                        line.setAttribute("x1",(x+1)*self.boardscale)
                        line.setAttribute("x2",(x+1)*self.boardscale)
                        line.setAttribute("y1", 0 )
                        line.setAttribute("y2", self.boardsize[1]*self.boardscale)
                        line.setAttribute("stroke-opacity", .17)
                        self.newPan.appendChild( line )
                for x in range(self.boardsize[1]-1):
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke=temp)
                        line.setAttribute("x1", 0 )
                        line.setAttribute("x2", self.boardsize[0]*self.boardscale)
                        line.setAttribute("y1",(x+1)*self.boardscale)
                        line.setAttribute("y2",(x+1)*self.boardscale)
                        line.setAttribute("stroke-opacity", .17)
                        self.newPan.appendChild( line )

                doc.body.insertBefore(self.newPan, currentDiv)

        def moveAlong(self):
            if self.multiplayer and self.session_id != None:
                req = ajax.ajax()
                req.bind('complete', self.upknownuniverse)
                req.open('POST',"/upknownuniverse",True)
                req.set_header('content-type','application/x-www-form-urlencoded')
                req.send({"action":"upknownuniverse", "session_id":str(self.session_id)})
            else:
                pass

            cnt = 0
            for k in self.planetlist:
                while cnt<self.newPan.childElementCount and self.newPan.children[cnt].tagName!="circle":
                    cnt = cnt + 1
                if cnt>=self.newPan.childElementCount:
                    crcl = svg.circle(cx=str((k.coord[0]+0.5)*self.boardscale), cy=str((k.coord[1]+0.5)*self.boardscale), r=str(self.boardscale/2))
                    self.newPan.appendChild( crcl )
                self.newPan.children[cnt].setAttribute("cx", (k.coord[0]+0.5)*self.boardscale)
                self.newPan.children[cnt].setAttribute("cy", (k.coord[1]+0.5)*self.boardscale)
                self.newPan.children[cnt].setAttribute("r", self.boardscale/2)
                temp = "rgb("+str(k.ownership[0])+","+str(k.ownership[1])+","+str(k.ownership[2])+")"
                self.newPan.children[cnt].setAttribute("fill", temp)
                self.newPan.children[cnt].setAttribute("fill-opacity", 1)
                #print("P: ", len(self.planetlist), " ", cnt, " / ", self.newPan.childElementCount, " = ", self.newPan.children[cnt].tagName)
                cnt = cnt + 1
            for k in range(cnt, self.newPan.childElementCount):
                if self.newPan.children[k].tagName=="circle":
                    self.newPan.children[k].setAttribute("fill", "rgb(255,255,255)")
                    self.newPan.children[k].setAttribute("fill-opacity", 0)
            cnt = 0
            for k in self.shiplist:
                while cnt<self.newPan.childElementCount and self.newPan.children[cnt].tagName!="polygon":
                    cnt = cnt + 1
                isinorbit = False
                for m in self.planetlist:
                    if k.coord[0] == m.coord[0] and k.coord[1] == m.coord[1]:
                        isinorbit = True
                        break
                if isinorbit:
                    temp = str((k.coord[0]+0.5)*self.boardscale) + "," + str((k.coord[1]+(5/8))*self.boardscale)
                    temp = temp + " " + str((k.coord[0]+0.75)*self.boardscale) + "," + str((k.coord[1]+0.5)*self.boardscale)
                    temp = temp + " " + str((k.coord[0]+0.75)*self.boardscale) + "," + str((k.coord[1]+0.75)*self.boardscale)
                else:
                    scale = 0.66
                    temp = str((k.coord[0]+(0.5-scale/2))*self.boardscale) + "," + str((k.coord[1]+0.5)*self.boardscale)
                    temp = temp + " " + str((k.coord[0]+(0.5+scale/2))*self.boardscale) + "," + str((k.coord[1]+(0.5-scale/2))*self.boardscale)
                    temp = temp + " " + str((k.coord[0]+(0.5+scale/2))*self.boardscale) + "," + str((k.coord[1]+(0.5+scale/2))*self.boardscale)
                if cnt>=self.newPan.childElementCount-1:
                    trgl = svg.polygon(points=temp)
                    self.newPan.appendChild( trgl )
                    #print("S: ", k.coord, " ",  cnt, " / ", self.newPan.childElementCount, " = ", self.newPan.children[cnt].tagName)
                self.newPan.children[cnt].setAttribute("points", temp)
                if isinorbit:
                    temp = "rgb(0,0,0)"
                else:
                    temp = "rgb("+str(k.ownership[0])+","+str(k.ownership[1])+","+str(k.ownership[2])+")"
                self.newPan.children[cnt].setAttribute("fill", temp)
                self.newPan.children[cnt].setAttribute("fill-opacity", 1)
                cnt = cnt + 1
            for k in range(cnt, self.newPan.childElementCount):
                if self.newPan.children[k].tagName=="polygon":
                    self.newPan.children[k].setAttribute("fill", "rgb(255,255,255)")
                    self.newPan.children[k].setAttribute("fill-opacity", 0)
                    #print("S: ", len(self.shiplist), " ", k, " / ", self.newPan.childElementCount, " = ", self.newPan.children[k].tagName)

            cnt = 0
            for k in range(self.boardsize[0]):
                for m in range(self.boardsize[1]):
                    if self.boardcontrol[k][m] != None:
                        for i in range(-1,2,2):
                            if k+i>=0 and k+i<self.boardsize[0] and self.boardcontrol[k+i][m] != self.boardcontrol[k][m]:
                                while ( cnt<self.newPan.childElementCount
                                    and ( self.newPan.children[cnt].tagName!="line"
                                        or ( abs(int(self.newPan.children[cnt].getAttribute("x1"))-int(self.newPan.children[cnt].getAttribute("x2")))==self.boardsize[0]*self.boardscale
                                            or abs(int(self.newPan.children[cnt].getAttribute("y1"))-int(self.newPan.children[cnt].getAttribute("y2")))==self.boardsize[1]*self.boardscale ) ) ):
                                    cnt = cnt + 1
                                if cnt>=self.newPan.childElementCount:
                                    line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke=temp)
                                    self.newPan.appendChild( line )
                                col = self.boardcontrol[k][m]
                                temp = "rgb("+str(col[0])+","+str(col[1])+","+str(col[2])+")"
                                self.newPan.children[cnt].setAttribute("stroke", temp)
                                self.newPan.children[cnt].setAttribute("x1", int(k+0.5+0.5*i)*self.boardscale)
                                self.newPan.children[cnt].setAttribute("x2", int(k+0.5+0.5*i)*self.boardscale)
                                self.newPan.children[cnt].setAttribute("y1", m*self.boardscale)
                                self.newPan.children[cnt].setAttribute("y2", (m+1)*self.boardscale)
                                self.newPan.children[cnt].setAttribute("stroke-opacity", 1)
                                if self.boardcontrol[k+i][m]==self.owncolorid: self.newPan.children[cnt].setAttribute("stroke-opacity", 0)
                                cnt = cnt + 1
                            if m+i>=0 and m+i<self.boardsize[1] and self.boardcontrol[k][m+i] != self.boardcontrol[k][m]:
                                while ( cnt<self.newPan.childElementCount
                                    and ( self.newPan.children[cnt].tagName!="line"
                                        or ( abs(int(self.newPan.children[cnt].getAttribute("x1"))-int(self.newPan.children[cnt].getAttribute("x2")))==self.boardsize[0]*self.boardscale
                                            or abs(int(self.newPan.children[cnt].getAttribute("y1"))-int(self.newPan.children[cnt].getAttribute("y2")))==self.boardsize[1]*self.boardscale ) ) ):
                                    cnt = cnt + 1
                                if cnt>=self.newPan.childElementCount:
                                    line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke=temp)
                                    self.newPan.appendChild( line )
                                col = self.boardcontrol[k][m]
                                temp = "rgb("+str(col[0])+","+str(col[1])+","+str(col[2])+")"
                                self.newPan.children[cnt].setAttribute("stroke", temp)
                                self.newPan.children[cnt].setAttribute("x1", k*self.boardscale)
                                self.newPan.children[cnt].setAttribute("x2", (k+1)*self.boardscale)
                                self.newPan.children[cnt].setAttribute("y1", int(m+0.5+0.5*i)*self.boardscale)
                                self.newPan.children[cnt].setAttribute("y2", int(m+0.5+0.5*i)*self.boardscale)
                                self.newPan.children[cnt].setAttribute("stroke-opacity", 1)
                                if self.boardcontrol[k][m+i]==self.owncolorid: self.newPan.children[cnt].setAttribute("stroke-opacity", 0)
                                cnt = cnt + 1
            for k in range(cnt, self.newPan.childElementCount):
                if ( self.newPan.children[k].tagName=="line"
                    and ( abs(int(self.newPan.children[k].getAttribute("x1"))-int(self.newPan.children[k].getAttribute("x2")))!=self.boardsize[0]*self.boardscale
                        or abs(int(self.newPan.children[k].getAttribute("y1"))-int(self.newPan.children[k].getAttribute("y2")))!=self.boardsize[1]*self.boardscale ) ):
                    self.newPan.children[k].setAttribute("fill", "rgb(255,255,255)")
                    self.newPan.children[k].setAttribute("fill-opacity", 0)

            for k in self.newPan.children:
                if k.tagName == "polygon":
                    temp = self.newPan.removeChild( k )
                    self.newPan.appendChild( temp )


        def upknownuniverse(self, req):
            if req.status==200:
                dico = eval(req.text)
                if dico["action"] == "upknownuniverse" and dico["session_id"] == self.session_id:
                    cnt=0
                    temp = "planet" + str( cnt )
                    while "n_"+temp in dico:
                        Unknown = True
                        for k in self.planetlist:
                            if k.coord[0] == int(dico["x_"+temp]) and k.coord[1] == int(dico["y_"+temp]):
                                Unknown = False
                                k.popul = int(dico["n_"+temp])
                                k.ownership = [int(dico["r_"+temp]), int(dico["g_"+temp]), int(dico["b_"+temp])]
                        if Unknown:
                            self.planetlist.append( P4X_Planet() )
                            self.planetlist[len(self.planetlist)-1].coord[0] = int(dico["x_"+temp])
                            self.planetlist[len(self.planetlist)-1].coord[1] = int(dico["y_"+temp])
                            self.planetlist[len(self.planetlist)-1].popul = int(dico["n_"+temp])
                            self.planetlist[len(self.planetlist)-1].ownership = [int(dico["r_"+temp]), int(dico["g_"+temp]), int(dico["b_"+temp])]
                        cnt = cnt + 1
                        temp = "planet" + str( cnt )
                    self.shiplist = []
                    cnt = 0
                    temp = "spaceship" + str( cnt )
                    while "n_"+temp in dico:
                        self.shiplist.append( P4X_Spaceship() )
                        self.shiplist[len(self.shiplist)-1].coord[0]  = int(dico["x_"+temp])
                        self.shiplist[len(self.shiplist)-1].coord[1]  = int(dico["y_"+temp])
                        self.shiplist[len(self.shiplist)-1].ucount    = int(dico["n_"+temp])
                        self.shiplist[len(self.shiplist)-1].ownership = [int(dico["r_"+temp]), int(dico["g_"+temp]), int(dico["b_"+temp])]
                        cnt = cnt + 1
                        temp = "spaceship" + str( cnt )

                    bcstr = dico["boardcontrol"]
                    for i, char in enumerate(bcstr):
                        if char == "x":
                            temp = ""
                            j = 1
                            while i-j>=0 and bcstr[i-j]!=" ":
                                temp = bcstr[i-j] + temp
                                j = j + 1
                            x = int( temp )
                            temp = ""
                            j = 1
                            while i+j<len(bcstr) and bcstr[i+j]!=":":
                                temp = temp + bcstr[i+j]
                                j = j + 1
                            y = int( temp )
                            col = [None,None,None]
                            temp = ""
                            while i+j<len(bcstr) and bcstr[i+j]!="[": j = j + 1
                            j = j + 1
                            while i+j<len(bcstr) and bcstr[i+j]!=",":
                                temp = temp + bcstr[i+j]
                                j = j+1
                            if temp != "None": col[0] = int(temp)
                            temp = ""
                            j = j + 1
                            while i+j<len(bcstr) and bcstr[i+j]!=",":
                                temp = temp + bcstr[i+j]
                                j = j+1
                            if temp != "None": col[1] = int(temp)
                            temp = ""
                            j = j + 1
                            while i+j<len(bcstr) and bcstr[i+j]!="]":
                                temp = temp + bcstr[i+j]
                                j = j+1
                            if temp != "None": col[2] = int(temp)
                            v = True
                            for k in col:
                                if k==None:
                                    v = False
                                    self.boardcontrol[x][y] = None
                                    break
                            if v: self.boardcontrol[x][y] = col

        def update(self,i):
                raf(self.update)
                self.moveAlong()

p4x=Planets4Xgame() #__init__ is called right here
p4x.update(0)

