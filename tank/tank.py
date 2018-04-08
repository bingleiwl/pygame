import pygame,sys,time
from random import randint
from pygame.locals import *
class TankMain():
	width=600
	height=500
	my_tank_missile_list = []
	my_tank = None
	wall = None
	#爆炸
	explode_list = []
	# enemy_list=[]
	#敌方坦克的组
	enemy_list = pygame.sprite.Group()
	#增加敌方炮弹
	enemy_missile_list = pygame.sprite.Group()
	def startGame(self):
		pygame.init()
		screen=pygame.display.set_mode((TankMain.width,TankMain.height),0,32)#0为固定大小
		pygame.display.set_caption("Tank City")
		TankMain.my_tank = My_Tank(screen)
		#建设一堵墙
		TankMain.wall = Wall(screen,100,80,30,400)
		#把敌方的坦克放到组里面
		if len(TankMain.enemy_list) == 0:
			for i in range(1,6):
				#把敌方坦克放到组里面
				TankMain.enemy_list.add(Enemy_Tank(screen))
		while True:
			#对地方的坦克数量进行检测
			if len(TankMain.enemy_list) < 5:
				#小于五个则添加一个
				#把敌方坦克放到组里面
				TankMain.enemy_list.add(Enemy_Tank(screen))
			screen.fill((0,0,0))
			for i,text in enumerate(self.write_text(),0):
				screen.blit(text,(0,5+(15*i)))
			#显示游戏中的墙，并且对墙和其他对象进行碰撞检测
			TankMain.wall.display()
			TankMain.wall.hit_other()

			self.get_event(TankMain.my_tank,screen)

			#判断我方坦克是否存在
			if TankMain.my_tank:
				#对我方坦克和敌方坦克的炮弹进行碰撞检测
				TankMain.my_tank.hit_enemy_missile()
			#判断我方坦克状态
			if TankMain.my_tank and TankMain.my_tank.live:
				TankMain.my_tank.display()
				TankMain.my_tank.move()
			else:
				TankMain.my_tank=None
			for enemy in TankMain.enemy_list:
				enemy.display()
				enemy.random_move()
				#敌方炮弹的移动
				enemy.random_fire()
			for m in TankMain.my_tank_missile_list:
				if m.live:
					m.display()
					#炮弹打中敌方坦克
					m.hit_tank()
					m.move()
				else:
					TankMain.my_tank_missile_list.remove(m)
			#显示所有的敌方坦克
			for m in TankMain.enemy_missile_list:
				if m.live:
					m.display()
					m.move()
				else:
					TankMain.enemy_missile_list.remove(m)
			#爆炸
			for explode in TankMain.explode_list:
				explode.display()
			time.sleep(0.05)
			pygame.display.update()#界面更新
	def get_event(self,my_tank,screen):
		for event in pygame.event.get():
			if event.type == QUIT:
				self.stopGame()
			#判断我方坦克是否消灭了，
			if event.type == KEYDOWN and (not my_tank) and event.key == K_n:
				#在创建一个我方坦克
				TankMain.my_tank = My_Tank(screen)
			#我方坦克存在，即可进行
			if event.type == KEYDOWN and my_tank:
				if event.key == K_LEFT or event.key ==K_a:
					my_tank.direction ="L"
					my_tank.stop=False
				if event.key == K_RIGHT or event.key == K_d:
					my_tank.direction ="R"
					my_tank.stop=False
				if event.key == K_UP or event.key == K_w:
					my_tank.direction ="U"
					my_tank.stop=False
				if event.key == K_DOWN or event.key == K_s:
					my_tank.direction ="D"
					my_tank.stop=False
				#bug,只有我方坦克存在时，才能用esc键退出，不然无法退出。
				if event.key == K_ESCAPE:
					self.stopGame()
				if event.key == K_SPACE:
					#我方坦克发射的炮弹
					m = my_tank.fire()
					m.good = True
					TankMain.my_tank_missile_list.append(m)
					#TankMain.my_tank_missile_list.append(my_tank.fire())
			#我方坦克存在，即可进行
			if event.type == KEYUP and my_tank:
				if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_UP or event.key == K_DOWN:
					my_tank.stop = True
	def stopGame(self):
		sys.exit()
	def write_text(self):
		font = pygame.font.SysFont("simsunnsimsun",12)#字体，字号
		text_sf1 = font.render("敌方坦克数量为：%d"%len(TankMain.enemy_list),True,(255,0,0))
		text_sf2 = font.render("我方坦克炮弹数量为：%d"%len(TankMain.my_tank_missile_list),True,(255,0,0))
		return text_sf1,text_sf2
class BaseItem(pygame.sprite.Sprite):
	def __init__(self,screen):
		pygame.sprite.Sprite.__init__(self)
		self.screen = screen
	def display(self):
		if self.live:
			self.image = self.images[self.direction]
			self.screen.blit(self.image, self.rect)
class Tank(BaseItem):
	width = 50
	height = 50
	def __init__(self,screen,left,top):
		super().__init__(screen)
		self.direction="D"
		self.speed=5
		self.stop=False
		self.images={}		
		self.images["L"]=pygame.image.load("images/tankL.gif")
		self.images["R"]=pygame.image.load("images/tankR.gif")
		self.images["U"]=pygame.image.load("images/tankU.gif")
		self.images["D"]=pygame.image.load("images/tankD.gif")
		self.image=self.images[self.direction]
		self.rect=self.image.get_rect()
		self.rect.left=left
		self.rect.top=top
		self.live=True
		# 坦克当前位置，获取到的位置有问题。
		self.oldtop=self.rect.top
		self.oldleft=self.rect.left
	#坦克停止
	def stay(self):
		self.rect.top= self.oldtop
		self.rect.left = self.oldleft
		# print(self.rect.top,self.rect.left)

	def move(self):
		if not self.stop:
			self.oldtop = self.rect.top
			self.oldleft = self.rect.left
			if self.direction =="L":
				if self.rect.left>0:
					self.rect.left -= self.speed
				else:
					self.rect.left=0
			elif self.direction =="R":
				if self.rect.right<TankMain.width:
					self.rect.right += self.speed
				else:
					self.rect.right=TankMain.width
			elif self.direction =="U":
				if self.rect.top>0:
					self.rect.top -= self.speed
				else:
					self.rect.top=0
			elif self.direction =="D":
				if self.rect.bottom < TankMain.height:
					self.rect.top += self.speed
				else:
					self.rect.bottom=TankMain.height
	def fire(self):
		m =Missile(self.screen,self)
		return m
		
class My_Tank(Tank):
	def __init__(self,screen):
		super().__init__(screen,275,400)
		self.stop = True
		#我方坦克状态
		self.live = True
	#我方坦克中弹
	def hit_enemy_missile(self):
		#有问题
		hit_list = pygame.sprite.spritecollide(self,TankMain.enemy_missile_list,False)
		#我方坦克中弹了
		for m in hit_list:
			m.live=False
			TankMain.enemy_missile_list.remove(m)
			self.live=False
			explode = Explode(self.screen,self.rect)
			TankMain.explode_list.append(explode)
class Enemy_Tank(Tank):
	def __init__(self,screen):
		super().__init__(screen,randint(1,5)*100,200)
		self.speed=4
		self.step=8
		self.get_random_direction()
	def get_random_direction(self):
		r = randint(0,4)
		if r == 4:
			self.stop =True
		elif r == 0 :
			self.direction = "R"
			self.stop = False
		elif r == 1 :
			self.direction = "L"
			self.stop=False
		elif r == 2 :
			self.direction = "U"
			self.stop=False
		elif r == 3 :
			self.direction = "D"
			self.stop=False
	def random_move(self):
		if self.live:
			if self.step==0:
				self.get_random_direction()
				self.step=6
			else:
				self.move()
				self.step-=1
	#敌方炮弹的出现次数控制
	def random_fire(self):
		r = randint(0,50)
		if r ==1 or r ==2 or r==3 or r==4 or r ==5:
			m = self.fire()
			TankMain.enemy_missile_list.add(m)
		else :
			return
class Missile(BaseItem):
	width = 12
	height = 12
	def __init__(self,screen,tank):
		super().__init__(screen)
		self.tank = tank
		self.direction = tank.direction
		self.speed = 12
		self.images={}		
		self.images["L"]=pygame.image.load("images/missileL.gif")
		self.images["R"]=pygame.image.load("images/missileR.gif")
		self.images["U"]=pygame.image.load("images/missileU.gif")
		self.images["D"]=pygame.image.load("images/missileD.gif")
		self.image=self.images[self.direction]
		self.rect=self.image.get_rect()
		self.rect.left=tank.rect.left + (tank.width -self.width)/2
		self.rect.top=tank.rect.top + (tank.height - self.height)/2
		self.live=True
		self.good = False
	def move(self):
		if self.live:
			if self.direction =="L":
				if self.rect.left>0:
					self.rect.left -= self.speed
				else:
					self.live = False
			elif self.direction =="R":
				if self.rect.right<TankMain.width:
					self.rect.right += self.speed
				else:
					self.live=False
			elif self.direction =="U":
				if self.rect.top>0:
					self.rect.top -= self.speed
				else:
					self.live = False
			elif self.direction =="D":
				if self.rect.bottom < TankMain.height:
					self.rect.top += self.speed
				else:
					self.live = False

	#炮弹击中坦克
	def hit_tank(self):
		#我方炮弹
		if self.good:
			hit_list = pygame.sprite.spritecollide(self,TankMain.enemy_list,False)
			for e in hit_list:
				#击中敌方
				e.live = False
				#删除敌方坦克
				TankMain.enemy_list.remove(e)
				self.live = False
				#产生爆炸效果
				explode = Explode(self.screen,e.rect)
				TankMain.explode_list.append(explode)

# 爆炸类
class Explode(BaseItem):

	def __init__(self,screen,rect):
		super().__init__(screen)
		self.live=True
		self.images=[pygame.image.load("images/0.gif"),\
					 pygame.image.load("images/1.gif"),\
					 pygame.image.load("images/2.gif"),\
					 pygame.image.load("images/3.gif"),\
					 pygame.image.load("images/4.gif"),\
					 pygame.image.load("images/5.gif"),\
					 pygame.image.load("images/6.gif"),\
					 pygame.image.load("images/7.gif"),\
					 pygame.image.load("images/8.gif"),\
					 pygame.image.load("images/9.gif"),\
					 pygame.image.load("images/10.gif")]
		self.step=0
		#爆咋的位置和发生爆炸前碰到坦克的位置一样，传入坦克位置即可
		self.rect = rect
	#display方法在整个游戏中，循环调用，隔0.1秒调用一次
	def display(self):
		if self.live:
			#最后一张图片显示了
			if self.step == len(self.images):
				self.live =False
			else:
				self.image = self.images[self.step]
				self.screen.blit(self.image,self.rect)
				self.step+=1
		else:
			# 删除该对象
			pass
#游戏中的墙
class Wall(BaseItem):
	def __init__(self,screen,left,top,width,height):
		super().__init__(screen)
		self.rect = Rect(left,top,width,height)
		self.color = (255,0,0)
	def display(self):
		self.screen.fill(self.color,self.rect)
	def hit_other(self):
		if TankMain.my_tank:
			is_hit = pygame.sprite.collide_rect(self,TankMain.my_tank)
			if is_hit:
				TankMain.my_tank.stop=True
				TankMain.my_tank.stay()
		if len(TankMain.enemy_list)!=0:
			hit_list=pygame.sprite.spritecollide(self,TankMain.enemy_list,False)
			for e in hit_list:
				e.stop = True
				e.stay()

game= TankMain()
game.startGame()