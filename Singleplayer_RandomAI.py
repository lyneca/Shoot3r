import pygame, random, math, os
from spritesheet import * # The only thing in this project not mine, I couldn't be bothered to make my own spritesheet grabbing file
from pygame.locals import *
from constants import *
os.chdir('Resources') # Change the working directory to the place where all the sounds, pictures etc are
pygame.init()
fullscreen_size = pygame.display.list_modes()[0]
SCREEN_WIDTH = G_SCREEN_WIDTH
SCREEN_HEIGHT = G_SCREEN_HEIGHT
fullscreen = False
font = pygame.font.SysFont('courier', 30) # Fooooont
font.set_bold(True)
clock = pygame.time.Clock() # Frame limiter blah blah
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
p1score = 0
p2score = 0
class Game(): # Game functions
	def end(player):
		if player == 1:
			winner = 2
			global p2score
			p2score += 1
		else:
			winner = 1
			global p1score # Ooh, global variables, now isn't this interesting
			p1score += 1
		for player in iter(players):
			player.kill()
		global player1 # Rare creatures, these Globals
		global player2
		player1 = Player(1)
		player2 = Player(2)
		bullets.empty()
		bombs.empty()
class Block(pygame.sprite.Sprite): # Those grey moving rectangle thingies
	def __init__(self,x):
		self.image = pygame.Surface((BLOCK_WIDTH,BLOCK_HEIGHT))
		self.image.fill(BLOCK_COLOUR)
		self.rect = self.image.get_rect()
		self.rect.y = screen.get_rect().centery
		self.rect.x = x
		pygame.sprite.Sprite.__init__(self)
		blocks.add(self)
	def update(self):
		self.rect.x -= BLOCK_SPEED # Move left
		if self.rect.x <= 0-self.rect.width: # Loop
			self.rect.x = SCREEN_WIDTH
class StaticObjects(): # All the static things that aren't part of the gameplay
	class Screen():
		def draw():
			pygame.draw.rect(screen,STATUS_BAR_COLOUR,(0,SCREEN_HEIGHT-50,SCREEN_WIDTH,SCREEN_HEIGHT)) # Draw the status bar
	class Heart(pygame.sprite.Sprite):
		def __init__(self,player,n):
			self.image = pygame.image.load('heart.png') # Aw <3
			self.image.set_colorkey((195,195,195)) # I should have probably stuck to a consistent colourkey
			self.rect = self.image.get_rect()
			self.rect.y = SCREEN_HEIGHT-45
			if player == 1:
				self.rect.x = 10 + n*50
			else:
				self.rect.x = SCREEN_WIDTH-(n+1)*50
			pygame.sprite.Sprite.__init__(self)
			hearts.add(self)
	class Status(): # Stuff on the grey status bar
		def draw_hearts(): # The magical heart-placeing algorithm
			for i in range(math.ceil(player1.life)):
				heart = StaticObjects.Heart(1,i)
			for i in range(math.ceil(player2.life)):
				heart = StaticObjects.Heart(2,i)
			# Score text
			p1scoretext = font.render(str(p1score),0,(0,0,255))
			screen.blit(p1scoretext,(screen.get_rect().centerx - p1scoretext.get_rect().width - 10,SCREEN_HEIGHT-45))
			p2scoretext = font.render(str(p2score),0,(255,0,0))
			screen.blit(p2scoretext,(screen.get_rect().centerx+p1scoretext.get_rect().width + 10,SCREEN_HEIGHT-45))
class Sounds(): # Sounds made in Sfxr, a retro synth
	lazer1 = pygame.mixer.Sound('Lazer1.ogg') # Pew
	lazer2 = pygame.mixer.Sound('Lazer2.ogg') # Pew pew
	explosion = pygame.mixer.Sound('Explosion.ogg')
	hit = pygame.mixer.Sound('Hit.ogg')
	bomb = pygame.mixer.Sound('Bomb.ogg')
	whistle = pygame.mixer.Sound('Whistle.ogg')
	theme = pygame.mixer.Sound('Theme.wav') # <-- This one was made in Musagi, retro sequencer and synth
class Explosion(pygame.sprite.Sprite): # Magical spawn-anywhere explosion object
	def __init__(self,x,y,type):
		self.sprites = []
		if type == 'player': # The player explosion is a bigger one
			self.spritesheet = Spritesheet('ship_explosion_spritesheet.png')
			for i in range(4):
				self.sprites.append(self.spritesheet.get_image(i*75,0,75,75))
		else:
			self.spritesheet = Spritesheet('explosion_spritesheet.png')
			for i in range(4):
				self.sprites.append(self.spritesheet.get_image(i*15,0,15,15))
		self.current_sprite = 0
		self.sprite_change_cooldown = 0 # This may or may not work
		self.image = self.sprites[0]
		self.image.set_colorkey((255,255,255)) # See? Inconsistent transparencies
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		pygame.sprite.Sprite.__init__(self)
		explosions.add(self)
	def update(self):
		if pygame.time.get_ticks() - self.sprite_change_cooldown > EXPLOSION_COOLDOWN:
			self.xpos = self.rect.x # THESE TWO LINES ARE IMPORTANT
			self.ypos = self.rect.y # When a sprite changes images it resets it's coordinates, so I had to store them and then re-move them
			self.current_sprite += 1
			if self.current_sprite >= 4: # When the animation is done
				self.kill()
				return
			self.image = self.sprites[self.current_sprite]
			self.image.set_colorkey((255,255,255))
			self.rect = self.image.get_rect()
			self.rect.x = self.xpos
			self.rect.y = self.ypos
class Player(pygame.sprite.Sprite): # The player
	def __init__(self,playern):
		self.pn = playern # 1 or 2
		self.life = PLAYER_LIFE
		if playern == 1:
			self.spritesheet = Spritesheet('player1_spritesheet.png')
		else:
			self.spritesheet = Spritesheet('player2_spritesheet.png')
		self.fly_sprites = {}
		for i in range(3):
			self.fly_sprites[i + 1] = self.spritesheet.get_image(i*SPRITE_SIZE,0,SPRITE_SIZE,SPRITE_SIZE) # How fancy is THAT?
		self.fire_sprites = {}
		for i in range(3):
			self.fire_sprites[i + 1] = self.spritesheet.get_image(i*SPRITE_SIZE,SPRITE_SIZE,SPRITE_SIZE,SPRITE_SIZE) # There it is again!
		self.current_sprite = 0
		self.active_sprites = self.fly_sprites
		self.image = self.active_sprites[1]
		self.rect = self.image.get_rect()
		self.rect.x = screen.get_rect().centerx
		self.sprite_change_cooldown = 0
		self.bombs = NUMBER_OF_BOMBS
		self.fire_cooldown = 0
		self.bomb_cooldown = 0
		self.vx = 0
		self.firing = False
		pygame.sprite.Sprite.__init__(self)
		players.add(self)
	def update(self): # The player update function
		# Old deprecated velocity stuff
		#self.vx *= 0.8
		#if self.vx <= -0.1 and self.vx >= -0.2:
		#   self.vx = 0
		#self.rect.x += round(self.vx,1)
		self.xpos = self.rect.x
		self.ypos = self.rect.y
		if self.pn == 1:
			self.rect.y = SCREEN_HEIGHT - SPRITE_SIZE - STATUS_BAR - GAP
		else:
			self.rect.y = GAP
		if self.life <= 0:
			death = Explosion(self.rect.x,self.rect.y,'player') # Boom
			Sounds.explosion.play()
			self.kill()
			Game.end(self.pn)
		if self.firing: # These two ifs control which sprite set is active, the firing one or the basic flight one
			self.active_sprites = self.fire_sprites
			self.current_sprite += 1
		else:
			self.active_sprites = self.fly_sprites
			self.current_sprite = random.randrange(1,4)
		if self.current_sprite == 4:
			if self.firing:
				self.firing = False
			self.current_sprite = 1
		if pygame.time.get_ticks() - self.sprite_change_cooldown > SPRITE_COOLDOWN:
			self.image = self.active_sprites[self.current_sprite]
			self.rect = self.image.get_rect()
			self.rect.x = self.xpos
			self.rect.y = self.ypos
			self.sprite_change_cooldown = pygame.time.get_ticks() # This was hard to remember
	def bomb(self):
		if pygame.time.get_ticks() - self.bomb_cooldown > BOMB_COOLDOWN and self.bombs > 0:
			Sounds.whistle.play()
			self.bombs -= 1
			if self.pn == 1:
				bomb = Bomb(self.rect.centerx - 12,self.rect.y, True)
			else:   
				bomb = Bomb(self.rect.centerx - 12,self.rect.y + SPRITE_SIZE, False)
			self.bomb_cooldown = pygame.time.get_ticks()
	def fire(self): # Pew pew
		if pygame.time.get_ticks() - self.fire_cooldown > FIRE_COOLDOWN:
			if self.pn == 1:
				Sounds.lazer1.play()
			else:
				Sounds.lazer2.play()
			self.firing = True
			self.current_sprite = 0
			if self.pn == 1:
				bullet = Bullet(self.rect.centerx - 15,self.rect.y, True) # Offsetting the bullets so they appear to be fired out of the ship's guns
				bullet = Bullet(self.rect.centerx + 5,self.rect.y, True)
			else:
				bullet = Bullet(self.rect.centerx - 15,self.rect.y + SPRITE_SIZE, False)
				bullet = Bullet(self.rect.centerx + 5,self.rect.y + SPRITE_SIZE, False)
			self.fire_cooldown = pygame.time.get_ticks()
def check_if_hit(): # COLLISION CHECKING FUNCTION. VERY VERY IMPORTANT
	# Player-bomb
	player1_hit_list = pygame.sprite.spritecollide(player1,bomb_explosions,False)
	for bomb in iter(player1_hit_list):
		player1.life -= 2
		explosion = Explosion(bomb.rect.x,bomb.rect.y,'player')
		bomb.kill()
	player2_hit_list = pygame.sprite.spritecollide(player2,bomb_explosions,False)
	for bomb in iter(player2_hit_list):
		player2.life -= 2
		explosion = Explosion(bomb.rect.x,bomb.rect.y,'player')
		bomb.kill()
	# Player-bullet
	player1_hit_list = pygame.sprite.spritecollide(player1,bullets,False)
	for bullet in iter(player1_hit_list):
		player1.life -= 0.5
		explosion = Explosion(bullet.rect.x,bullet.rect.y,'bullet')
		Sounds.hit.play()
		bullet.kill()
	player2_hit_list = pygame.sprite.spritecollide(player2,bullets,False)
	for bullet in iter(player2_hit_list):
		player2.life -= 0.5
		explosion = Explosion(bullet.rect.x,bullet.rect.y,'bullet')
		Sounds.hit.play()
		bullet.kill()
	# Block-bomb
	for block in iter(blocks):
		block_hit_list = pygame.sprite.spritecollide(block,bombs,False)
		for bomb in iter(block_hit_list):
			explosion = Explosion(bomb.rect.x,bomb.rect.y,'player')
			Sounds.bomb.play()
			bomb.kill()
	# BLock-bullet
	for block in iter(blocks):
		block_hit_list = pygame.sprite.spritecollide(block,bullets,False)
		for bullet in iter(block_hit_list):
			explosion = Explosion(bullet.rect.x,bullet.rect.y,'bullet')
			bullet.kill()
class Bullet(pygame.sprite.Sprite): # Bullet sprite
	def __init__(self,px,py,d):
		if d:
			self.image = pygame.image.load('bullet_blue.png')
		else:
			self.image = pygame.image.load('bullet_red.png')
		self.image.set_colorkey((0,0,0))
		self.rect = self.image.get_rect()
		self.rect.x = px
		self.rect.y = py
		self.going_up = d
		pygame.sprite.Sprite.__init__(self)
		bullets.add(self)
	def update(self):
		if self.going_up: # Goin' up
			self.rect.y -= BULLET_SPEED
		else:
			self.rect.y += BULLET_SPEED
class Bomb(pygame.sprite.Sprite):
	def __init__(self,px,py,d):
		if d:
			self.image = pygame.image.load('bomb_blue.png')
		else:
			self.image = pygame.image.load('bomb_red.png')
		self.image.set_colorkey((0,0,0))
		self.rect = self.image.get_rect()
		self.rect.x = px
		self.rect.y = py
		self.going_up = d
		pygame.sprite.Sprite.__init__(self)
		bombs.add(self)
	def update(self):
		if self.going_up:
			if self.rect.y <= player2.rect.y:
				Sounds.bomb.play()
				explosion = Explosion(self.rect.x,self.rect.y,'player')
				bomb_explosions.add(explosion)
				self.kill()
		else:
			if self.rect.y >= player1.rect.y:
				Sounds.bomb.play()
				explosion = Explosion(self.rect.x,self.rect.y,'player')
				bomb_explosions.add(explosion)
				self.kill()
		if self.going_up:
			self.rect.y -= BOMB_SPEED
		else:
			self.rect.y += BOMB_SPEED
# Groups and player instantiation
players = pygame.sprite.Group()
bomb_explosions = pygame.sprite.Group()
blocks = pygame.sprite.Group()
for i in range(BLOCK_NUMBER):
	# block = Block(SCREEN_WIDTH/BLOCK_NUMBER*i)
	block = Block(random.randrange(0,SCREEN_WIDTH))
#block = Block(SCREEN_WIDTH - 100)
explosions = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bombs = pygame.sprite.Group()
hearts = pygame.sprite.Group()
update_groups = [bombs,bullets,explosions,bomb_explosions,blocks,players]
player1 = Player(1)
player2 = Player(2)
time_to_choose = True
done = False
Sounds.theme.play(-1) # Bleeeep blooooop
while not done: # HERE'S something familiar, eh?
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_F11:
				# Fullscreen flag imported from pygame.locals
				if fullscreen:
					screen = pygame.display.set_mode((G_SCREEN_WIDTH,G_SCREEN_HEIGHT))
					fullscreen = False
					SCREEN_WIDTH = G_SCREEN_WIDTH
					SCREEN_HEIGHT = G_SCREEN_HEIGHT
					BLOCK_WIDTH = 100
				else:
					screen = pygame.display.set_mode(fullscreen_size,FULLSCREEN)
					fullscreen = True
					SCREEN_WIDTH,SCREEN_HEIGHT = fullscreen_size
					BLOCK_WIDTH /= G_SCREEN_WIDTH/SCREEN_WIDTH
				blocks.empty()
				for i in range(BLOCK_NUMBER):
					block = Block(random.randrange(0,SCREEN_WIDTH))
			if event.key == pygame.K_ESCAPE:
				done = True
	pressed = pygame.key.get_pressed() # Oh now what's this?
	# A different keyboard listener?
	# Well well.
	# This enables MUCH smoother movement and key detection.
	# Player 1
	if pressed[pygame.K_LEFT] and player1.rect.x > 0:
		player1.rect.x -= P1_MOVE
	if pressed[pygame.K_RIGHT] and player1.rect.x < SCREEN_WIDTH - player1.rect.width:
		player1.rect.x += P1_MOVE
	if pressed[pygame.K_UP]:
		player1.fire()
	if pressed[pygame.K_RSHIFT] or pressed[pygame.K_DOWN]:
		player1.bomb()
	# And player 2
	if pressed[pygame.K_a] and player2.rect.x > 0:
		player2.rect.x -= P2_MOVE
	if pressed[pygame.K_d] and player2.rect.x < SCREEN_WIDTH - player2.rect.width:
		player2.rect.x += P2_MOVE
	if pressed[pygame.K_s]:
		player2.fire()
	if pressed[pygame.K_SPACE] or pressed[pygame.K_LSHIFT] or pressed[pygame.K_w]:
		player2.bomb()
	for group in update_groups:
		group.update()
	if time_to_choose:
		ai_move = random.randrange(0,SCREEN_WIDTH/2)
		ai_dir = random.choice([True,False])
		time_to_choose = False
	if not time_to_choose:
		if ai_move <= 0:
			time_to_choose = True
		elif ai_dir:
			if player2.rect.x >= SCREEN_WIDTH-player2.rect.width:
				ai_dir = not ai_dir
			ai_move -= P2_MOVE
			player2.rect.x += P2_MOVE
		else:
			if player2.rect.x <= 0:
				ai_dir = not ai_dir
			ai_move -= P2_MOVE
			player2.rect.x -= P2_MOVE
	if random.randrange(10) == 9: player2.fire()
	hearts.empty()
	# I tried to make this next bit shorter but it crashed pretty much everything so I didn't try it again
	check_if_hit()
	screen.fill((BACKGROUND_COLOUR))
	bullets.draw(screen)
	StaticObjects.Screen.draw()
	StaticObjects.Status.draw_hearts()
	blocks.draw(screen)
	hearts.draw(screen)
	players.draw(screen)
	bombs.draw(screen)
	bomb_explosions.draw(screen)
	explosions.draw(screen)
	# And now to activate it all...
	pygame.display.flip()
	# Boom.
	clock.tick(60)
pygame.quit()
# Have fun!