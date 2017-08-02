#Alex Bai
#poker classes


class Player():
	#holds information about each player

	def __init__(self):
		self.name = ""
		self.position = ""
		self.seat = ""
		self.stack = 1000
		self.holeCards = []
		self.pool = []
		self.hand = None
		self.canFold = False
		self.canRaise = False
		self.canCall = False
		self.canCheck = False
		self.curBet = 0
		self.turn = False

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
		self.canFold = False
		self.canRaise = False
		self.canCall = False
		self.canCheck = False
		self.curBet = 0
		self.turn = False

	def bet(self, amount):
		self.stack = self.stack - (amount - self.curBet)
		self.curBet = amount


class Table():
	#holds general table information

	def __init__(self):
		self.players = []
		self.inHand = []
		self.deck = "As Ah Ad Ac 2s 2h 2d 2c 3s 3h 3d 3c 4s 4h 4d 4c "\
			"5s 5h 5d 5c 6s 6h 6d 6c 7s 7h 7d 7c 8s 8h 8d 8c 9s 9h 9d 9c "\
			"Ts Th Td Tc Js Jh Jd Jc Qs Qh Qd Qc Ks Kh Kd Kc".split(" ")
		self.status = "ante"
		self.blinds = {"ante": 1, "sb": 2, "bb": 5}
		self.board = []
		self.curPot = 0
		self.prevPot = 0
		self.winner = None
		self.actionOn = None
		self.tableSet = False
		self.actOrder = []
		self.positions = {}
		self.lastRaiser = None
		self.action = "check"
		self.betAmount = 0
		self.raiseAmount = 0
		self.dealer = None
		self.first = None
		self.lookup = threeWayDict()

	def reset(self):
		self.deck = "As Ah Ad Ac 2s 2h 2d 2c 3s 3h 3d 3c 4s 4h 4d 4c "\
			"5s 5h 5d 5c 6s 6h 6d 6c 7s 7h 7d 7c 8s 8h 8d 8c 9s 9h 9d 9c "\
			"Ts Th Td Tc Js Jh Jd Jc Qs Qh Qd Qc Ks Kh Kd Kc".split(" ")
		self.status = "ante"
		self.board = []
		self.curPot = 0
		self.prevPot = 0
		self.winner = None
		for player in self.players:
			player.reset()
		self.inHand = []
		for player in self.players:
			self.inHand.append(player)
		self.actionOn = None
		self.tableSet = False
		self.actOrder = []
		self.positions = {}
		self.lastRaiser = None
		self.action = "check"
		self.betAmount = 0
		self.raiseAmount = 0
		self.dealer = None
		self.first = None
		self.lookup = threeWayDict()

	def addPlayer(self, player):
		self.players.append(player)
		self.inHand.append(player)
		self.lookup.add(player, player.seat, player.position)

	def calcPot(self):
		self.curPot = self.prevPot
		for player in self.players:
			self.curPot += player.curBet


class threeWayDict(dict):
	# can use any key to lookup other two keys, returned as a dict
	# not entirely useful with player as key, since player has info
	def add(self, player, seat, pos):
		if player in self:
			del self[player]
		if seat in self:
			del self[seat]
		if pos in self:
			del self[pos]
		dict.__setitem__(self, player, {"seat": seat, "position": pos})
		dict.__setitem__(self, seat, {"player": player, "position": pos})
		dict.__setitem__(self, pos, {"player": player, "seat": seat})

	def __delitem__(self, key):
		dict.__delitem__(self, self[key])
		dict.__delitem__(self, key)

	def __len__(self):
		"""Returns the number of connections"""
		return dict.__len__(self) // 3