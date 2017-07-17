# Alex Bai
# Texas Hold'Em

import random
import classes
import string
import pygame
import os
import inputbox


#maps card number to its value
values = {'1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9,\
	'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}

#maps card rank
handRanks = {"high": 1, "pair":2, "twoPair":3, "trips":4, "straight":5,\
	"flush":6, "fullHouse":7, "quads":8, "straightFlush": 9}

#seats
seats = ("bm", "bl", "tl", "tm", "tr", "br")

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
GREEN    = (   0, 255,   0)
RED      = ( 255,   0,   0)
BLUE     = (   0,   0, 255)
GRAY	 = ( 220, 220, 220)

def dealCard(table):
	#pops a random card from the remaining deck.
	out = random.choice(table.deck)
	table.deck.remove(out)
	return out

def dealTable(table):
	#deals the cards for each stage and updates player cards pools
	if(table.status is "ante"):
		for player in table.players:
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
	elif(table.status is "river"):
		pass
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
	#returns a list of the flush cards, or False if none
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
	#only need to check once, because only one flush is possible
	for key in segregated:
		if(len(segregated[key]) >= 5):
			return segregated[key]
	return False

def findStraight(pool):
	#returns a list of the straight cards, or False if none
	poole = pool
	#hacky way to implement Aces counting as 1 or 14
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
	#list is sorted, so check consecutive indexes for consecutive values
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
	#finds the multiplicities of each card in the list
	#returns as a dict {card letter: [card1, card2]}
	counts = {}
	for card in pool:
		if(card[0] in counts):
			counts[card[0]].append(card)
		else:
			counts[card[0]] = [card]
	return counts

def findQuads(pool, counts):
	#finds quads or False
	for key in counts:
		if(len(counts[key]) == 4):
			quads = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
			return quads + removed[:1]
	return False

def findFullHouse(pool, counts):
	#finds fullHouse or False
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
	#finds trips or False
	for key in counts:
		if(len(counts[key]) == 3):
			trips = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
			return trips + removed[:2]
	return False

def findTwoPair(pool, counts):
	#finds twoPair or False
	pairhi = []
	pairlo = []
	removed = []
	for key in counts:
		if(len(counts[key]) == 2):
			pairhi = [card for card in pool if card[0] == key]
			removed = [card for card in pool if card[0] != key]
			break
	if(pairhi is []):
		return False
	counts = findCounts(removed)
	for key in counts:
		if(len(counts[key]) == 2):
			pairlo = [card for card in pool if card[0] == key]
			removed = [card for card in removed if card[0] != key]
			#unordered dicts kept reversing the order of pairhi/pairlo
			return sortCards(pairhi + pairlo) + removed[:1]
	return False

def findPair(pool, counts):
	#finds pair or False
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
	straightFlush = findStraight(flush) if flush else False
	quads = findQuads(pool, counts)
	fullHouse = findFullHouse(pool, counts)
	straight = findStraight(pool)
	trips = findTrips(pool, counts)
	twoPair = findTwoPair(pool, counts)
	pair = findPair(pool, counts)

	if(straightFlush):
		#wtf straight flush
		return ("straightFlush", straightFlush[:5])
	elif(quads):
		#check quads next
		return ("quads", quads)
	elif(fullHouse):
		#no quads, check fullHouse
		return ("fullHouse", fullHouse)
	elif(flush):
		#regular flush
		return ("flush", flush[:5])
	elif(straight):
		#no fullHouse and no flush
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

def multiShowdown(players):
	#can't handle 3-way chopped pots
	winner = players[0]
	chops = []
	for player in players[1:]:
		newWinner = showdown(winner, player)
		if(newWinner is None):
			chops.append(winner)
			chops.append(player)
			winner = player
		else:
			winner = newWinner
			chops = [winner]
	return chops

def showdown(p1, p2):
	#returns winning player
	print(p1)
	print(p2)
	print()
	p1HandRank = handRanks[p1.hand[0]]
	p2HandRank = handRanks[p2.hand[0]]
	p1Hand = p1.hand[1]
	p2Hand = p2.hand[1]

	if(p1HandRank > p2HandRank):
		return p1
	elif(p1HandRank < p2HandRank):
		return p2
	else:
		#hand ranks are the same, compare values or kickers
		for index in range(len(p1Hand)):
			p1Card = p1Hand[index]
			p2Card = p2Hand[index]
			p1Value = values[p1Card[0]]
			p2Value = values[p2Card[0]]
			if(p1Value > p2Value):
				return p1
			elif(p1Value < p2Value):
				return p2
		return None

def update(table):
	#adds new card to pools and sorts pools
	for player in table.players:
		player.pool = player.holeCards + table.board
		player.pool = sortCards(player.pool)
		player.hand = evalHand(player.pool)

def loadCard(screen, pics, card, cW, cH, topLeft):
	#loads a card and places it
	pics[card] = pygame.image.load(os.path.join("Cards", "{}.png".format(card)))
	pics[card] = pygame.transform.smoothscale(pics[card], (cW, cH))
	pics["{}Rect".format(card)] = pics[card].get_rect(topleft = topLeft)
	screen.blit(pics[card], pics["{}Rect".format(card)])

def loadBG(screen, pics, cW, cH):
	#loads images from file, resizes them, get_rects them
	pics["bg"] = pygame.image.load("graphics.png")
	pics["bgRect"] = pics["bg"].get_rect()
	screen.blit(pics["bg"], pics["bgRect"])

def loadUI(screen):
	#loads buttons and boxes
	mouse = pygame.mouse.get_pos()
	buttonFont = pygame.font.SysFont(None, 32)

	if(680<mouse[0]<780 and 470<mouse[1]<510):
		pygame.draw.rect(screen, BLACK, (678, 468, 104, 44))
	pygame.draw.rect(screen, GRAY, (680, 470, 100, 40))
	raiseText = buttonFont.render('Raise', False, BLACK)
	screen.blit(raiseText, (700, 480))

def text(screen, text, size, color, left, top):
	tempFont = pygame.font.SysFont(None, size)
	tempText = tempFont.render(text, False, color)
	screen.blit(tempText, left, top)

def run(table):
	#set graphics variables
	screenW = 800
	screenH = 600
	dividerH = 450
	cW = 56
	cH = 76
	bTop = dividerH/2 - cH/2
	bf1 = (250, bTop)
	bf2 = (310, bTop)
	bf3 = (370, bTop)
	bt = (430, bTop)
	br = (490, bTop)

	size = (screenW, screenH)
	cPos = {"flop1": bf1, "flop2": bf2, "flop3": bf3, "turn": bt, "river": br,\
		"bm": (((screenW/2 - cW), 350), ((screenW/2), 350)),\
		"bl": ((100, 300), (156, 300)),\
		"tl": ((100, 70), (156, 70)),\
		"tm": (((screenW/2 - cW), 30), ((screenW/2), 30)),\
		"tr": ((580, 70), (636, 70)),\
		"br": ((580, 300), (636, 300))\
		}
	pics = {}

	pygame.init()
	pygame.font.init()
	winFont = pygame.font.SysFont(None, 40)
	winText = winFont.render('Winner', False, BLACK)
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Texas Hold'em")

	# Loop until the user clicks the close button.
	done = False

	# Used to manage how fast the screen updates
	clock = pygame.time.Clock()

	# -------- Main Program Loop -----------
	while not done:
		# --- Main event loop
		for event in pygame.event.get(): # User did something
			if event.type == pygame.QUIT:
				done = True
			elif event.type == pygame.KEYDOWN:
				key = event.key
				if(key == pygame.K_ESCAPE):
					wsop.reset()
				elif(key == pygame.K_SPACE):
					dealTable(table)
				elif(key == pygame.K_q):
					done = True
				elif(key == pygame.K_a and table.status == "ante" and\
					len(table.players) < 6):
					name = inputbox.ask(screen, "Player Name: ")
					table.addPlayer(name, seats[len(table.players)])
			elif event.type == pygame.MOUSEBUTTONDOWN:
				click = event.pos
				if(680<click[0]<780 and 470<click[1]<510):
					dealTable(table)
				print(event.pos)


		# --- Game logic should go here
		if(table.status == "river"):
			#debug
			# p1.holeCards = ["Td", "3d"]
			# p2.holeCards = ["9c", "Qc"]
			# wsop.board = ["7d", "4s", "7c", "3h", "4h"]
			# update(wsop)

			print("Players: {}".format(wsop.players))
			print("Board: {}".format(wsop.board))

			#print(wsop.players["hero"].pool)
			#print("Hero: {}".format(wsop.players[0].hand))
			#print("Villain: {}".format(wsop.players[1].hand))

			print()
			winner = multiShowdown(wsop.players)
			if(len(winner) == 1):
				print("Winner: {}".format(winner[0].hand))
				table.winner = winner[0]
			else:
				print("Chop")
			table.status = "done"

		# Clear screen
		#screen.fill(WHITE)

		# --- Drawing code should go here
		loadBG(screen, pics, cW, cH)
		loadUI(screen)
		for player in table.players:
			text = player.name

			if(player.holeCards):
				loadCard(screen, pics, player.holeCards[0],\
					cW, cH, cPos[player.seat][0])
				loadCard(screen, pics, player.holeCards[1],\
					cW, cH, cPos[player.seat][1])
		if(table.status == "flop"):
			loadCard(screen, pics, table.board[0], cW, cH, cPos["flop1"])
			loadCard(screen, pics, table.board[1], cW, cH, cPos["flop2"])
			loadCard(screen, pics, table.board[2], cW, cH, cPos["flop3"])
		elif(table.status == "turn"):
			loadCard(screen, pics, table.board[0], cW, cH, cPos["flop1"])
			loadCard(screen, pics, table.board[1], cW, cH, cPos["flop2"])
			loadCard(screen, pics, table.board[2], cW, cH, cPos["flop3"])
			loadCard(screen, pics, table.board[3], cW, cH, cPos["turn"])
		elif(table.status == "river"):
			loadCard(screen, pics, table.board[0], cW, cH, cPos["flop1"])
			loadCard(screen, pics, table.board[1], cW, cH, cPos["flop2"])
			loadCard(screen, pics, table.board[2], cW, cH, cPos["flop3"])
			loadCard(screen, pics, table.board[3], cW, cH, cPos["turn"])
			loadCard(screen, pics, table.board[4], cW, cH, cPos["river"])
		elif(table.status == "done"):
			loadCard(screen, pics, table.board[0], cW, cH, cPos["flop1"])
			loadCard(screen, pics, table.board[1], cW, cH, cPos["flop2"])
			loadCard(screen, pics, table.board[2], cW, cH, cPos["flop3"])
			loadCard(screen, pics, table.board[3], cW, cH, cPos["turn"])
			loadCard(screen, pics, table.board[4], cW, cH, cPos["river"])
			if(table.winner):
				#text(screen, "Winner", 40, BLACK, )
				screen.blit(winText,(cPos[table.winner.seat][0][0] + 5,\
					cPos[table.winner.seat][0][1] - 27))

		# --- Go ahead and update the screen with what we've drawn.
		pygame.display.flip()

		# --- Limit to 60 frames per second
		clock.tick(60)
	pygame.quit()




wsop = classes.Table()

p1 = classes.Player()
p2 = classes.Player()
p3 = classes.Player()
p1.name = "Hero"
p1.seat = "bm"
p2.name = "Villain"
p2.seat = "bl"
p3.name = "Villain 2"
p3.seat = "tl"
wsop.players.append(p1)
wsop.players.append(p2)
wsop.players.append(p3)


wsop.reset()
run(wsop)

#debug
# p1.holeCards = ["2d", "3s"]
# p2.holeCards = ["2d", "8d"]
# wsop.board = ["Qc", "Ad", "Jc", "Ts", "7d"]
# update(wsop)

# userInput = input("continue? y/n\n")
# if(userInput != "y"):
# 	go = False