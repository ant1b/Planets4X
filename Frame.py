#! /usr/bin/env python
#ant1 201411

import browser
import math
from browser import document as doc
from browser.timer import request_animation_frame as raf
from browser import svg



def IsOneTileMove(x1,y1,x2,y2):
        if (abs(x1-x2)==1 and y1==y2) or (x1==x2 and abs(y1-y2)==1):
                return True
        else:
                return False

class Spaceship():
        def __init__(self):
                self.coord = [2,2]

        def locateto(self, xpos, ypos):
                self.coord = [xpos,ypos]
        
class Planets4Xgame():
        def __init__(self):
                self.boardsize = [30, 30]
                self.boardscale = 50
                if math.floor(browser.window.innerWidth/self.boardsize[0]) < math.floor(browser.window.innerHeight/self.boardsize[1]):
                        self.boardscale  = math.floor(browser.window.innerWidth/(self.boardsize[0]+1))
                else:
                        self.boardscale  = math.floor(browser.window.innerHeight/(self.boardsize[1]+1))
                if self.boardscale < 10: self.boardscale = 10
                self.progress = [0,0]
                self.shiplist = []
                self.shiplist.append( Spaceship() )
                self.drawBoard()
                self.newPan.bind('click', self.macch)

        def macch(self, ev):
                #print("macchiato")
                #print(self.boardscale, ": ", math.floor((ev.clientX/self.boardscale)-0.5), " x ", math.floor((ev.clientY/self.boardscale)-0.5))
                for k in self.shiplist:
                        cx = math.floor((ev.clientX/self.boardscale)-0.5)
                        cy = math.floor((ev.clientY/self.boardscale)-0.5)
                        if IsOneTileMove(k.coord[0],k.coord[1],cx,cy):
                                k.locateto(cx,cy)

        def drawBoard(self):
                self.newPan = doc.createElementNS("http://www.w3.org/2000/svg","svg")
                self.newPan.setAttribute("width",self.boardsize[0]*self.boardscale)
                self.newPan.setAttribute("height",self.boardsize[1]*self.boardscale)
                self.newPan.setAttribute("style","background-color:rgb(0,0,0);border-style:solid;border-width:1;border-color:#000;")
                currentDiv = doc.getElementById("div")
                for x in range(self.boardsize[0]-1):
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke="brown", stroke_width="2")
                        line.setAttribute("x1",(x+1)*self.boardscale)
                        line.setAttribute("x2",(x+1)*self.boardscale)
                        line.setAttribute("y1", 0 )
                        line.setAttribute("y2", self.boardsize[1]*self.boardscale)
                        line.setAttribute("stroke-opacity", .2)
                        self.newPan.appendChild( line )
                for x in range(self.boardsize[1]-1):
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke="brown", stroke_width="2")
                        line.setAttribute("x1", 0 )
                        line.setAttribute("x2", self.boardsize[0]*self.boardscale)
                        line.setAttribute("y1",(x+1)*self.boardscale)
                        line.setAttribute("y2",(x+1)*self.boardscale)
                        line.setAttribute("stroke-opacity", .2)
                        self.newPan.appendChild( line )

                for k in self.shiplist:
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke="green", stroke_width="5")
                        line.setAttribute("x1", k.coord[0]*self.boardscale )
                        line.setAttribute("x2", (k.coord[0]+1)*self.boardscale )
                        line.setAttribute("y1", k.coord[1]*self.boardscale )
                        line.setAttribute("y2", (k.coord[1]+1)*self.boardscale )
                        self.newPan.appendChild( line )
                        line = svg.line(x1="0", y1="0", x2="1", y2="1", stroke="green", stroke_width="5")
                        line.setAttribute("x1", k.coord[0]*self.boardscale )
                        line.setAttribute("x2", (k.coord[0]+1)*self.boardscale )
                        line.setAttribute("y1", (k.coord[1]+1)*self.boardscale )
                        line.setAttribute("y2", k.coord[1]*self.boardscale )
                        self.newPan.appendChild( line )

                doc.body.insertBefore(self.newPan, currentDiv)

        def moveAlong(self):
                for k in self.shiplist:
                        criss = False
                        for j in range(self.newPan.childElementCount):
                                if self.newPan.children[j].getAttribute("stroke")=="green":
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

