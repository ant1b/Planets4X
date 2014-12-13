
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, redirect, render_template, request, jsonify
import math
import string
import random
import threading

### SUPPORT FUNCTIONS
def id_generator(size=64, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def IsOneTileMove(x1,y1,x2,y2):
    if (abs(x1-x2)==1 and y1==y2) or (x1==x2 and abs(y1-y2)==1):
        return True
    else:
        return False

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
            if 64 > math.sqrt( math.pow(col[k][0]-bckgd[0],2) + math.pow(col[k][1]-bckgd[1],2) + math.pow(col[k][2]-bckgd[2],2) ):
                doublon = True
            if 64 > math.sqrt( math.pow(col[k][0]-neutral[0],2) + math.pow(col[k][1]-neutral[1],2) + math.pow(col[k][2]-neutral[2],2) ):
                doublon = True
            if not doublon: temp.append(col[k])
        col = temp
    return [col, col[playerID]]

### SUPPORT CLASSES
class P4X_Spaceship():
    def __init__(self):
        self.ownership = None
        self.coord     = [0,0]
        self.ucount    = 100
        self.gocoord   = [0,0]
        self.moveleft  = 1
        self.justsplit = False

    def locateto(self, xpos, ypos):
        self.coord    = [xpos, ypos]
        self.gocoord  = [xpos, ypos]

class P4X_Planet():
    def __init__(self):
        self.ownership = None
        self.coord     = [0,0]
        self.initpop   = 1000
        self.popul     = 1000
        self.maxpop    = 10000
        self.popgrowthrate = 0.33

    def locateto(self, xpos, ypos):
        self.coord = [xpos,ypos]

    def popgrow(self):
        #Logistic Population Growth: Continuous and Discrete
        #http://amrita.vlab.co.in/?sub=3&brch=65&sim=1110&cnt=1
        self.popul  = self.popul + int(math.ceil(self.popgrowthrate * ((self.popul-self.initpop+2)*(1-((self.popul-self.initpop+1)/(self.maxpop-self.initpop))))-0.5))

class P4X_Player():
    def __init__(self):
        self.session_id = None
        self.color = [255,255,255]

    def ownedP4Xelements(self, Elist):
        Owned = []
        for k in Elist:
            if k.ownership == self.session_id:
                Owned.append( k )
        return Owned


class P4X_Game():
    def __init__(self):
        self.playerlist = []
        self.colorlist  = []
        self.boardsize  = [1,1]
        self.planetlist = []
        self.shiplist   = []

    def defineBoard(self, x, y):
        self.boardsize = [x,y]
        #Distribute planet locations
        coorddraw = random.sample(range(self.boardsize[0]*self.boardsize[1]), math.floor((self.boardsize[0]*self.boardsize[1])*0.1))
        for i in range(len(coorddraw)):
            self.planetlist.append( P4X_Planet() )
            self.planetlist[i].locateto(int(math.fmod(coorddraw[i],self.boardsize[0])), int(math.floor(coorddraw[i]/self.boardsize[0])))
            self.planetlist[i].ownership = None

    def freePlanetsCount(self):
        NotOwned = []
        for k in self.planetlist:
            if k.ownership == None:
                NotOwned.append( k )
        return len(NotOwned)

    def thisPlayerColor(self, session_id):
        for k in self.playerlist:
            if k.session_id == session_id:
                return k.color

class P4X_Server():
    def __init__(self):
        self.session_list = []
        self.games = []
        #self.mutex = threading.Lock()

    def newcomer(self, x, y):
        #self.mutex.acquire()
        #generate and register unique random id
        temp = id_generator()
        while temp in self.session_list: temp = id_generator()
        self.session_list.append( temp )
        #Create new game when previous is full of players
        if len(self.games)==0 or self.games[len(self.games)-1].freePlanetsCount() < 1:
            self.games.append( P4X_Game() )
            self.games[len(self.games)-1].defineBoard(x, y)
        #assign player to game
        a = len(self.games)-1
        self.games[a].playerlist.append( P4X_Player() )
        b = len(self.games[a].playerlist)-1
        self.games[a].playerlist[b].session_id = temp
        temp = PlayerColour(b+1, self.games[a].colorlist)
        self.games[a].colorlist = temp[0]
        self.games[a].playerlist[b].color = temp[1]
        #assign home planet to player
        for k in self.games[a].planetlist:
            if k.ownership == None:
                k.ownership = self.games[a].playerlist[b].session_id
                #assign one ship to player
                self.games[a].shiplist.append( P4X_Spaceship() )
                self.games[a].shiplist[len(self.games[a].shiplist)-1].ownership = self.games[a].playerlist[b].session_id
                self.games[a].shiplist[len(self.games[a].shiplist)-1].locateto(k.coord[0], k.coord[1])
                return
        #self.mutex.release()

    def ThisGameThisPlayer(self, session_id):
        for g in range(len(self.games)):
            for p in range(len(self.games[g].playerlist)):
                if self.games[g].playerlist[p].session_id == session_id:
                    gp = [g,p]
                    return gp
        return False


app = Flask(__name__)
p4x_server = P4X_Server()

@app.route('/')
def launch():
    return redirect('/Planets4X')
#def hello_world():
#    return 'Hello from Flask!'

@app.route('/Planets4X')
def index():
    #return 'This works like a charm.'
    #return render_template('index.html')
    #user = {'nickname': 'Miguel'}  # fake user
    #return render_template('index.html', title='Home', user=user)
    return render_template('index.html', title='Planets4X')

@app.route('/newcomer', methods=['GET', 'POST'])
def register():
    data = {'action': 'undefined'}
    if request.method == 'POST' and request.form.get('action')=='joingame':
        p4x_server.newcomer(int(request.form.get('boardsizex')), int(request.form.get('boardsizey')))
        L = p4x_server.games[len(p4x_server.games)-1].playerlist[len(p4x_server.games[len(p4x_server.games)-1].playerlist)-1].ownedP4Xelements(p4x_server.games[len(p4x_server.games)-1].planetlist)
        data = {'action':'welcome',
            'session_id':str(p4x_server.session_list[len(p4x_server.session_list)-1]),
#            'game_id':str(len(p4x_server.games)),
#            'freeplanets':str(p4x_server.games[len(p4x_server.games)-1].freePlanetsCount()),
#            'players':str(len(p4x_server.games[len(p4x_server.games)-1].playerlist)),
            'colorid_r':str(p4x_server.games[len(p4x_server.games)-1].playerlist[len(p4x_server.games[len(p4x_server.games)-1].playerlist)-1].color[0]),
            'colorid_g':str(p4x_server.games[len(p4x_server.games)-1].playerlist[len(p4x_server.games[len(p4x_server.games)-1].playerlist)-1].color[1]),
            'colorid_b':str(p4x_server.games[len(p4x_server.games)-1].playerlist[len(p4x_server.games[len(p4x_server.games)-1].playerlist)-1].color[2]),
            'boardsizex':str(p4x_server.games[len(p4x_server.games)-1].boardsize[0]),
            'boardsizey':str(p4x_server.games[len(p4x_server.games)-1].boardsize[1]),
#            'ownedplanets':str(len(L)),
            'homeplanetx':str( L[0].coord[0] ),
            'homeplanety':str( L[0].coord[1] )}
    return jsonify(data)

@app.route('/upknownuniverse', methods=['GET', 'POST'])
def upknownuniverse():
    data = {'action': 'undefined'}
    if request.method == 'POST' and request.form.get('action')=='upknownuniverse':
        gp = p4x_server.ThisGameThisPlayer( request.form.get('session_id') )
        if gp:
            a = gp[0]
            b = gp[1]
        else:
            return jsonify(data)
        data = {'action':'upknownuniverse', 'session_id':request.form.get('session_id')}
        cnt = 0
        for k in p4x_server.games[a].planetlist:
            if k.ownership == request.form.get('session_id'):
                temp = "planet" + str( cnt )
                data["x_"+temp] = str( k.coord[0] )
                data["y_"+temp] = str( k.coord[1] )
                data["n_"+temp] = str( k.popul )
                col = p4x_server.games[a].thisPlayerColor( k.ownership )
                if col==None: col = [127,127,127]
                data["r_"+temp] = str( col[0] )
                data["g_"+temp] = str( col[1] )
                data["b_"+temp] = str( col[2] )
                cnt = cnt + 1
            else:
                for j in p4x_server.games[a].shiplist:
                    if j.ownership == request.form.get('session_id'):
                        if IsOneTileMove(j.coord[0], j.coord[1], k.coord[0], k.coord[1]):
                            temp = "planet" + str( cnt )
                            data["x_"+temp] = str( k.coord[0] )
                            data["y_"+temp] = str( k.coord[1] )
                            data["n_"+temp] = str( k.popul )
                            col = p4x_server.games[a].thisPlayerColor( k.ownership )
                            if col==None: col = [127,127,127]
                            data["r_"+temp] = str( col[0] )
                            data["g_"+temp] = str( col[1] )
                            data["b_"+temp] = str( col[2] )
                            cnt = cnt + 1
        #return jsonify(data)
        cnt = 0
        for k in p4x_server.games[a].shiplist:
            if k.ownership == request.form.get('session_id'):
                temp = "spaceship" + str( cnt )
                data["x_"+temp] = str( k.coord[0] )
                data["y_"+temp] = str( k.coord[1] )
                data["n_"+temp] = str( k.ucount )
                col = p4x_server.games[a].thisPlayerColor( k.ownership )
                if col==None: col = [127,127,127]
                data["r_"+temp] = str( col[0] )
                data["g_"+temp] = str( col[1] )
                data["b_"+temp] = str( col[2] )
                cnt = cnt + 1
            else:
                for j in p4x_server.games[a].shiplist:
                    if j.ownership == request.form.get('session_id'):
                        if IsOneTileMove(j.coord[0], j.coord[1], k.coord[0], k.coord[1]):
                            temp = "spaceship" + str( cnt )
                            data["x_"+temp] = str( k.coord[0] )
                            data["y_"+temp] = str( k.coord[1] )
                            data["n_"+temp] = str( k.ucount )
                            col = p4x_server.games[a].thisPlayerColor( k.ownership )
                            if col==None: col = [127,127,127]
                            data["r_"+temp] = str( col[0] )
                            data["g_"+temp] = str( col[1] )
                            data["b_"+temp] = str( col[2] )
                            cnt = cnt + 1
    return jsonify(data)

@app.route('/clickonboard', methods=['POST'])
def incaseofclick():
    data = False
    if request.method == 'POST' and request.form.get('action')=='clickonboard':
        data = {"action":"moveover",
            "session_id":request.form.get('session_id'),
            "clickx":request.form.get('clickx'),
            "clicky":request.form.get('clicky')}
        gp = p4x_server.ThisGameThisPlayer( request.form.get('session_id') )
        if not gp: return jsonify(data)
        for k in p4x_server.games[gp[0]].shiplist:
            if k.ownership == request.form.get('session_id'):
                k.locateto( int(request.form.get('clickx')),int(request.form.get('clicky')) )
    return jsonify(data)

if __name__ == '__main__':
    app.run()


###


