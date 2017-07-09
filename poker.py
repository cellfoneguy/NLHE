# Alex Bai
# Texas Hold'Em

import random
import classes
import string

values = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9,\
	'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

handRanks = {"high": 1, "pair":2, "twoPair":3, "trips":4, "straight":5,\
	"flush":6, "fullHouse":7, "quads":8, "straightFlush": 9}

def dealCard(table):
	#pops a random card from the remaining deck.
	out = random.choice(table.deck)
	table.deck.remove(out)
	return out

def dealTable(table):
	#deals the cards for each stage and updates player cards pools
	if(table.status is "ante"):
		for player in table.players.values():
			player.holeCards.append(dealCard(table))
			player.holeCards.append(dealCard(table))
		table.status = "pre"
	elif(table.status is "pre"):
		table.board.append(dealCard(table))
		table.board.append(dealCard(table))
		table.board.append(dealCard(table))
		table.status = "flop"
	elif(table.status is "flop"):
		table.board.append(dealCard(table))
		table.status = "turn"
	elif(table.status is "turn"):
		table.board.append(dealCard(table))
		table.status = "river"

	update(table)

def sortCards(pool):
	#sorts 7 cards by value, ignoring suit
	out = []
	for i in range(len(pool)):
		big = pool[0]
		for card in pool:
			value = card[0]
			if(values[value] > values[big[0]]):
				big = card
		out.append(big)
		pool.remove(big)
	return out


def findFlush(pool):
	s, h, d, c = [], [], [], []
	segregated = {"s":s, "h":h, "d":d, "c":c}
	for card in pool:
		suit = card[1]
		if(suit == 's'):
			s.append(card)
		elif(suit == 'h'):
			h.append(card)
		elif(suit == 'd'):
			d.append(card)
		else:
			c.append(card)
	for key in segregated:
		if(len(segregated[key]) >= 5):
			return (key, segregated[key])
	return False

def findStraight(pool):
	if("As" in pool):
		pool.append("1s")
	elif("Ah" in pool):
		pool.append("1h")
	elif("Ad" in pool):
		pool.append("1d")
	elif("Ac" in pool):
		pool.append("1c")

	out = []
	current = values[pool[0][0]]
	out.append(pool[0])
	for card in pool:
		value = values[card[0]]
		if(value == current):
			continue
		elif(value == (current - 1)):
			current = value
			out.append(card)
		else:
			if(len(out) >= 5):
				return out
			else:
				out = [card]
				current = value

	if(len(out) >= 5):
		return out
	else:
		return False

def findCounts(pool):
	counts = {}
	for card in pool:
		print(card)
		if(card[0] in counts):
			counts[card[0]].append(card)
		else:
			counts[card[0]] = [card]
	return counts

def findQuads(pool, counts):
	for key in counts:
		if(len(counts[key]) == 4):
			quads = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
			return quads + [removed[0]]
		else:
			return False

def findFullHouse(pool, counts):
	#assumes counts is sorted
	triple = {}
	double = {}
	for key in counts:
		if(len(counts[key]) == 3):
			triple = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
	if(triple is {}):
		return False
	counts = findCounts(removed)
	for key in counts:
		if(len(counts[key]) >= 2):
			double = [card for card in pool if card[0] == key]
			return triple + double
	return False


def evalHand(pool):
	flush = findFlush(pool)
	counts = findCounts(pool)
	if(flush):
		#at least a flush on table
		straightFlush = findStraight(flush[1])
		if(straightFlush):
			#wtf straight flush
			return ("straightFlush", straightFlush[:5])
		else:
			#check quads next
			quads = findQuads(pool, counts)
			if(quads):
				return ("quads", quads)
			else:
				#no quads, check fullHouse

				#regular flush
				return ("flush", flush[:5])
	else:
		#no flush
		straight = findStraight(pool)
		if(straight):
			return ("straight", straight[:5])

# def showdown(pool):


def update(table):
	#adds new card to pools and sorts pools
	for player in table.players.values():
		player.pool = player.holeCards + table.board
		player.pool = sortCards(player.pool)
		player.hand = evalHand(player.pool)

pool = ["Ah", "Ad", "Ac", "Ks", "Kc", "Qc", "Jh"]
counts = findCounts(pool)
print(counts)
print()
print(findFullHouse(pool, counts))



# wsop = classes.Table()
# p1 = classes.Player()
# p2 = classes.Player()
# wsop.players["hero"] = p1
# wsop.players["villian"] = p2

# noHand = True
# while(noHand):
# 	wsop.reset()
# 	dealTable(wsop)
# 	dealTable(wsop)
# 	dealTable(wsop)
# 	dealTable(wsop)

# 	print(wsop.players)
# 	print(wsop.board)

# 	print(wsop.players["hero"].pool)
# 	print(wsop.players["hero"].hand)
# 	if(wsop.players["hero"].hand is not None):
# 		noHand = False
# 	input()
