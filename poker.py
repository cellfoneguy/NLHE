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
			return segregated[key]
			#return (key, segregated[key])
	return False

def findStraight(pool):
	poole = pool
	if("As" in poole):
		poole.append("1s")
	elif("Ah" in poole):
		poole.append("1h")
	elif("Ad" in poole):
		poole.append("1d")
	elif("Ac" in poole):
		poole.append("1c")

	out = []
	current = values[poole[0][0]]
	out.append(poole[0])
	for card in poole:
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
			return quads + removed[:1]
		else:
			return False

def findFullHouse(pool, counts):
	#assumes counts is sorted
	triple = []
	double = []
	removed = []
	for key in counts:
		if(len(counts[key]) == 3):
			triple = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
	if(triple is []):
		return False
	counts = findCounts(removed)
	for key in counts:
		if(len(counts[key]) >= 2):
			double = [card for card in pool if card[0] == key]
			return triple + double
	return False

def findTrips(pool, counts):
	for key in counts:
		if(len(counts[key]) == 3):
			trips = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
			return trips + removed[:2]
		else:
			return False

def findTwoPair(pool, counts):
	pairhi = []
	pairlo = []
	removed = []
	for key in counts:
		if(len(counts[key]) == 2):
			pairhi = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
	if(pairhi is []):
		return False
	counts = findCounts(removed)
	for key in counts:
		if(len(counts[key]) == 2):
			pairlo = [card for card in pool if card[0] == key]
			removed = [card for card in removed if card[0] != key]
			return pairhi + pairlo + removed[:1]
	return False

def findPair(pool, counts):
	pair = []
	for key in counts: 
		if(len(counts[key]) == 2):
			pair = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
			return pair + removed[:3]
	return False

def evalHand(pool):
	#finds all hands first. inefficient but prettier.
	#separates finding different hands. also inefficient but prettier.
	counts = findCounts(pool)
	flush = findFlush(pool)
	if(flush):
		straightFlush = findStraight(flush)
	quads = findQuads(pool, counts)
	fullHouse = findFullHouse(pool, counts)
	straight = findStraight(pool)
	trips = findTrips(pool, counts)
	twoPair = findTwoPair(pool, counts)
	pair = findPair(pool, counts)

	if(flush):
		#at least a flush on table
		if(straightFlush):
			#wtf straight flush
			return ("straightFlush", straightFlush[:5])
		elif(quads):
			#check quads next
			return ("quads", quads)
		elif(fullHouse):
			#no quads, check fullHouse
			return ("fullHouse", fullHouse)
		else:
			#regular flush
			return ("flush", flush[:5])
	else:
		#no flush
		if(straight):
			return ("straight", straight[:5])
		elif(trips):
			#check for trips
			return ("trips", trips)
		elif(twoPair):
			#check for two pair
			return ("twoPair", twoPair)
		elif(pair):
			#at least a pair?
			return ("pair", pair)
		else:
			#no hand at all
			return ("high", pool[:5])

def showdown(p1, p2):
	#returns winning player
	p1HandRank = handRanks[p1.hand.keys()[0]]
	p2HandRank = handRanks[p2.hand.keys()]
	p1Hand = p1.hand.values()[0]
	p2Hand = p2.hand.values()[0]

	if(p1HandRank > p2HandRank):
		return p1
	elif(p1HandRank < p2HandRank):
		return p2
	else:
		pass



def update(table):
	#adds new card to pools and sorts pools
	for player in table.players.values():
		player.pool = player.holeCards + table.board
		player.pool = sortCards(player.pool)
		player.hand = evalHand(player.pool)



wsop = classes.Table()
p1 = classes.Player()
p2 = classes.Player()
wsop.players["hero"] = p1
wsop.players["villian"] = p2

go = True
while(go):
	wsop.reset()
	dealTable(wsop)
	dealTable(wsop)
	dealTable(wsop)
	dealTable(wsop)

	print(wsop.players)
	print(wsop.board)

	print(wsop.players["hero"].pool)
	print(wsop.players["hero"].hand)
	userInput = input("continue? y/n\n")
	if(userInput != "y"):
		go = False
