#Alex Bai
#poker classes


class Player():
	#holds information about each player

	def __init__(self):
		self.name = ""
		self.position = ""
		self.seat = ""
		self.stack = 100
		self.holeCards = []
		self.pool = []
		self.hand = None
		self.canFold = False
		self.canRaise = False
		self.canCall = False
		self.canCheck = False

	def __repr__(self):
		if(self.holeCards):
			return ("{}: {} {}".format(self.name, self.holeCards[0], \
			self.holeCards[1]))
		else:
			return self.name
		

	def reset(self):
		self.holeCards = []
		self.pool = []
		self.hand = None



class Table():
	#holds general table information

	def __init__(self):
		self.players = []
		self.deck = "As Ah Ad Ac 2s 2h 2d 2c 3s 3h 3d 3c 4s 4h 4d 4c "\
			"5s 5h 5d 5c 6s 6h 6d 6c 7s 7h 7d 7c 8s 8h 8d 8c 9s 9h 9d 9c "\
			"Ts Th Td Tc Js Jh Jd Jc Qs Qh Qd Qc Ks Kh Kd Kc".split(" ")
		self.status = "ante"
		self.board = []
		self.pot = 0
		self.winner = None
		self.actionOn = None
		self.tableSet = False
		self.actOrder = []
		self.positions = {}
		self.lastRaiser = None
		self.action = "check"
		self.raiseAmount = 0

	def reset(self):
		self.deck = "As Ah Ad Ac 2s 2h 2d 2c 3s 3h 3d 3c 4s 4h 4d 4c "\
			"5s 5h 5d 5c 6s 6h 6d 6c 7s 7h 7d 7c 8s 8h 8d 8c 9s 9h 9d 9c "\
			"Ts Th Td Tc Js Jh Jd Jc Qs Qh Qd Qc Ks Kh Kd Kc".split(" ")
		self.status = "ante"
		self.board = []
		self.pot = 0
		self.winner = None
		for player in self.players:
			player.reset()
		self.actionOn = None
		self.tableSet = False
		self.actOrder = []
		self.positions = {}
		self.lastRaiser = None
		self.action = "check"
		self.raiseAmount = 0

	def addPlayer(self, name, seat):
		p = Player()
		p.name = name
		p.seat = seat
		self.players.append(p)

	def setLastActor(self, player):
		while(self.actOrder[0] is not player):
			self.actOrder.append(self.actOrder.pop())
		self.actOrder.append(self.actOrder.pop())