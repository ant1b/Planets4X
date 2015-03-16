#ant1 201410
#Planets4X: revival of freeware downloaded from minitel on family Atari 520stf early 90s
#Move spaceships around on 2D grid(orange or green edges), find planets, grow more ships, battles when ships from opponent on same
#square, battle through random number generator in multiple successive skirmishes with piou-piou sound effect
#and graphically horizontal sorta fill-up bar with filling rebounding on both ends.
#Plan: keep simple mechanics, refine design, allow for extension.
#Based on http://www.raywenderlich.com/38732/multiplayer-game-programming-for-teens-with-python
#Tutotrial by Julian Meyer, November 11, 2013

#run Frame.py from Powershell using following two lines:
#cd "c:\...path-to-Planets4X-folder..."
#c:\...path-to-pythonXX..\python Frame.py
#Where XX stand for python version

#For multiplayer, launch server first:
#cd "c:\...path-to-Planets4X-folder..."
#c:\...path-to-pythonXX..\python server.py
#Then for each player from a separate console:
#cd "c:\...path-to-Planets4X-folder..."
#c:\...path-to-pythonXX..\python Frame.py
#Where XX stand for python version

#Developped and tested under python 3.2
#Requires pygame (dev and test 1.9.2)
#Requires PIL (dev and test Pillow 2.6.1)

#v00.00: 20141028, draws grid, places ship icon upon mouse click over grid.
#v00.01: 20141028, random places one planet inside grid, click places ships with line of sight 1 block h or v, click on planet for owning (color only).
#v00.02: 20141029, Works as a game, discover hidden planets moving ship around using mouse. Ship movement is cumbersome.
#v00.03: 20141030, Works as game. Ability to split ship fleets in half by right clicking next-door tile. 
#	Movements restricted to one tile per turn.
#	Fleet movement eased, left click on destination next-door tile.
#	Automerge fleets when more than one ship eligible (movement capcity undepleted) to reach left-clicked tile.
#	Explored and controlled area edges change to teamcolor.
#	Total fleet movement capacity left this turn counter.
#	Next turn button requires left clicking.
#	Planet population grows each turn.
#	Right-click on ship or planet prints corresponding info to standard output.
#v00.04: 20141031, Works as a game. Discover hidden planets and battle for their ownership.
#	Planetary battles decided by 1/2 chance, losing destroys ship, winning replenishes crew.
#	Exploit = use fleet splitting right-click rather than entire ship commiting left-clicking for attacking planet.
#	Ship movement capacity depicted by icon brightness.
#	Ship in orbit depicted.
#	Display total fleet crewmembership.
#v00.05: 20141102, Not tested as a game.
#	Wrap ability for ships through straight line trajectories devoid of obstacles across chartered territory in deep space.
#	Movement capacity sometimes not depleted upon merging fleets.
#	Victory by overwhelmingness effective in planetary battles.
#	Planetary battles odds less favorable to player Vs neutral planets (the only kind so far) i.e. better working defenses.
#v00.06: 20141103, Works as a game.
#	Movement capacity sometimes not depleted upon merging fleets.
#	May not wrap from being in orbit, posibly already the case in v00.05
#	Planet conquest appears to be taking too many turns on average.
#	FLeet icon (ship), size (small or large) depends on crew size compared to halfway value between entire fleet min and max.
#	Writing planetary battle reports in battlereports.txt
#v00.07: 20141112, Works as a game.
#	Embryonnic multiplayer added, server is separate python file.
#	Uses lightweight network protocols Mastermind v.4.1.3 by Ian Mallet.
#	Single player by default running original file, or if server not found, upon start.
#	Players explore map with identical planet locations.
#	Players may join anytime within the set maximum number of players.
#	Initial player settings decide on size of map and maximum number of players when first connect.
#	Player color distributed algorithmically.
#	Client (player side) needs to call server with shorter periodicity than server timeout.













