
#  ███████╗███╗   ██╗ █████╗ ██╗  ██╗███████╗
#  ██╔════╝████╗  ██║██╔══██╗██║ ██╔╝██╔════╝
#  ███████╗██╔██╗ ██║███████║█████╔╝ █████╗  
#  ╚════██║██║╚██╗██║██╔══██║██╔═██╗ ██╔══╝  
#  ███████║██║ ╚████║██║  ██║██║  ██╗███████╗
#  ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
# 
# by cnwang. 2024/05                                          


import curses
import keyboard
import numpy as np
import time

VERSION = 0.1

SPEED_FACTOR = 0.9
SPEED_STEPS = 20

DIR_UP = 0
DIR_RIGHT = 1
DIR_DOWN = 2
DIR_LEFT = 3

SYMBOL_HEAD = 'X'
SYMBOL_BODY = 'o'
SYMBOL_FOOD = '#'
SYMBOL_BG = ' '

SCREEN_MAX_R = 24
SCREEN_MAX_C = 80

COLLIDE_EAT_FOOD = 1
COLLIDE_EAT_SELF = 2
COLLIDE_HIT_WALL = 3
COOLIDE_NOTHING = 0

DIR_DELTA = [[-1,0],[0,1],[1,0],[0,-1]]

class Node():
	r = 0
	c = 0
	symbol = ''
	def __init__(self, r, c, symbol):
		self.r = r
		self.c = c
		self.symbol = symbol
	
class Snake():
	body = []
	score = 0
	direction = DIR_RIGHT
	scr = ''
	gg = False
	delay = 1.0
	totalSteps=0
	stageSteps = 0
	totalAtes=0
	status = 0	#0 normal, #1 eat food, #2 ateself
	def __init__(self,scr):
		self.scr = scr
		self.restart()

	def restart(self):
		self.score = 0
		self.body = [Node(int(SCREEN_MAX_R/2), int(SCREEN_MAX_C/2), symbol =SYMBOL_HEAD)]
		self.food = self.generateFood()
		self.gg = False
		self.totalSteps = 0
		self.stageSteps = 0
		self.totalAtes  = 0
		self.delay = 1.0
		self.drawSnake()
		self.drawNode(self.food)
		self.showScore()

	def move(self):
		newR = self.body[0].r + DIR_DELTA[self.direction][0]
		newC = self.body[0].c + DIR_DELTA[self.direction][1]
		if newR < 1 or newR > SCREEN_MAX_R or newC < 0 or newC > SCREEN_MAX_C:
			self.status = COLLIDE_HIT_WALL
			self.gameOver()

		else: 
			oldHead = self.body[0]
			oldHead.symbol = SYMBOL_BODY
			self.drawNode(oldHead)
			newHead = Node(newR,newC,SYMBOL_HEAD)
			self.body.insert(0,newHead )
			self.drawNode(newHead)
			
			ret = self.checkCollide()
			if ret == COLLIDE_EAT_FOOD:
				pass
			elif ret == COLLIDE_EAT_SELF:
				
				self.gameOver()
				pass
			else: # just move, earse tail
				tail = self.body.pop()
				tail.symbol = SYMBOL_BG
				self.drawNode(tail)
		self.showScore()
		self.totalSteps += 1
		self.stageSteps += 1
		self.checkSpeed()
	
	def checkCollide(self):
		head = self.body[0]
		self.status = COOLIDE_NOTHING
		if head.r == self.food.r and head.c == self.food.c:
			self.score += 100
			self.totalAtes += 1
			# self.scr.addstr(23,40,'Eat!')
			self.food = self.generateFood()
			self.drawNode(self.food,curses.A_BLINK)
			self.status = COLLIDE_EAT_FOOD
			return self.status
		else: 
			eatSelf = False
			for b in self.body[1:]:
				eatSelf = eatSelf or( head.r == b.r and head.c == b.c)
			if eatSelf:
				self.status = COLLIDE_EAT_SELF
				return self.status
			pass
		self.score += int(10/self.delay)

		return self.status
	

	def checkSpeed(self):
		if self.stageSteps == SPEED_STEPS:
			self.delay *= SPEED_FACTOR
			self.stageSteps = 0


	def showScore(self):
		score = f'Snake Ver{VERSION} by cnwang         Score : {self.score:6,}  s: {self.totalSteps:6,}  #: {self.totalAtes:6,}   {self.drawSnakeInString()}'
		scorelen = len(score)
		score = (' '* int((80-scorelen)/2) + score + ' '* int((80-scorelen)/2))[:SCREEN_MAX_C-1]
		self.putCenter(0, score, attr = curses.A_REVERSE)

	def changeDirection(self,ch):
		curseDir = [curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]
		if ch in curseDir:
			self.direction = curseDir.index(ch)
		else: 
			return

	def putCenter(self, r, msg, attr = curses.A_NORMAL):
		self.scr.addstr(r,int((SCREEN_MAX_C - len(msg))/2),msg, attr)
		
	def gameOver(self):
		self.gg = True
		self.putCenter(8, f'G A M E    O V E R',curses.A_BLINK)
		self.putCenter(12,f'SCORE: {self.score}')
		self.putCenter(14, f'Total steps : {self.totalSteps:,}')

		if self.status == COLLIDE_EAT_SELF:
			dead = 'Eat yourself'
		if self.status == COLLIDE_HIT_WALL:
			dead = 'Hit the wall'
		if self.status == COOLIDE_NOTHING:
			dead = 'bug...it\' a bug'
		self.putCenter(16, f'You are dead due to {dead}',curses.A_BLINK)

		self.putCenter(20,'Press any key to replay, q to quit')
		pass
		
	def drawSnake(self):
		for node in self.body:
			self.drawNode(node)

	def drawSnakeInString(self):
		bodyLength = len(self.body)
		ret = ''
		if bodyLength == 1:
			ret = SYMBOL_HEAD
		elif bodyLength == 2:
			ret = SYMBOL_HEAD+SYMBOL_BODY
		if bodyLength <=3:
			ret = f'{SYMBOL_HEAD}{SYMBOL_BODY*(bodyLength-1)}'
		else:
			ret = f'{SYMBOL_HEAD}{SYMBOL_BODY}({bodyLength-3}){SYMBOL_BODY}'
		return ret
	
	def drawNode(self, node, attr=curses.A_NORMAL):
		self.scr.move(node.r, node.c)
		self.scr.addch(node.symbol,attr)

	def generateFood(self):
		r = int(np.random.random()* (SCREEN_MAX_R -1)) +1 
		c = int(np.random.random()* SCREEN_MAX_C)
		overlap = True
		while overlap:
			for node in self.body:
				overlap = overlap and (node.r == r and node.c == c)
		food = Node(r = r, c=c, symbol= SYMBOL_FOOD)
		return food

def showMsg(scr, text):
	scr.addstr(SCREEN_MAX_R,0,text)

def showStart(scr):
	scr.clear()
	curses.noecho()
	msg=[
'  _________                 __             ',
' /   _____/  ____  _____   |  | __  ____   ',
' \_____  \  /    \ \__  \  |  |/ /_/ __ \  ',
' /        \|   |  \ / __ \_|    < \  ___/  ',
'/_______  /|___|  /(____  /|__|_ \ \___  > ',
'        \/      \/      \/      \/     \/   ',
'',
f'       Ver {VERSION}, by cnwang in Python',	
'','',
'		    Press any key start']

	for i in range(0,len(msg)):
		scr.addstr(i+5,14,msg[i],curses.A_BOLD)
	scr.nodelay(False)
	ch = scr.getch()
	scr.clear()


def main(stdscr):
	showStart(stdscr)
	stdscr.nodelay(True)
	stdscr.refresh()
	snake = Snake(stdscr)
	
	counter  = time.time()

	count = 0
	keepPlaying = True 

	while keepPlaying:
		while not snake.gg:
			curses.noecho()
			a = stdscr.getch()
			snake.changeDirection(a)
			if time.time() - counter > snake.delay:
				snake.move()
				# showMsg(stdscr,f'move {snake.stageSteps}/{snake.totalSteps}/{snake.delay:.2} {snake.direction},sl={len(snake.body)} s{snake.body[0].r},{snake.body[0].c} f{snake.food.r},{snake.food.c} ,status {snake.status}')
				counter = time.time()
				count +=1

		stdscr.nodelay(False)
		ch = stdscr.getch()

		if ch == 113 or ch == 81: #q or Q
			keepPlaying = False
		else:
			stdscr.clear()
			stdscr.nodelay(True)
			snake.restart()

# Initialize the library
curses.wrapper(main)
