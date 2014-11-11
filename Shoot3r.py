"""
Welcome to Shoot3r, a remake of... I have no idea.
Controls:
    Player 1 (Blue):
        Left:   Left
        Right:  Right
        Fire:   Up
        Bomb:   Down
    Player 2 (Red):
        Left:   A
        Right:  D
        Fire:   S
        Bomb:   W
    Fullscreen: F11
    Exit:       Escape
You have three lives and three bombs.
For every two bullets that hit you you lose a heart.
Bombs and the splash damage from the explosion makes you lose two hearts.
To all the people I sent this to:
	If you are going to try to read my code, good luck.
	If you do read my code and want to take something out of it, that's fine, but
		please cite me :D
The spritesheet functions are not mine, but everything else is!
The files 'Singleplayer_RandomAI' and 'Singleplayer_TrackingAI' are my first attempts at
 an AI for this game.
Graphics and music are both my design, but the soundtrack (bleep bloop) is from a
 remake of the original Space Invaders.
Have fun :D

Variable changing is in constants.py.
"""
import pygame, random, math, os
from spritesheet import * # The only thing in this project not mine, I couldn't be bothered to make my own spritesheet grabbing file
from pygame.locals import *
from constants import *
os.chdir('Resources') # Change the working directory to the place where all the sounds, pictures etc are
pygame.init() # Off we go
fullscreen_size = pygame.display.list_modes()[0] # Gets the most applicable fullscreen size
SCREEN_WIDTH = G_SCREEN_WIDTH # G_SCREEN_WIDTH and G_SCREEN_HEIGHT are the not-fullscreen window size
SCREEN_HEIGHT = G_SCREEN_HEIGHT
# SCREEN_HEIGHT and SCREEN_WIDTH are variables used in game generation
fullscreen = False
font = pygame.font.SysFont('courier', 30) # Fooooont
font.set_bold(True)
clock = pygame.time.Clock() # Frame limiter blah blah
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Make the screen
p1score = 0
p2score = 0
class Game(): # Game functions
    def end(player):
        """ End and restart the game """
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
        """ Make a block """
        self.image = pygame.Surface((BLOCK_WIDTH,BLOCK_HEIGHT))
        self.image.fill(BLOCK_COLOUR) # Grey
        self.rect = self.image.get_rect()
        self.rect.y = screen.get_rect().centery
        self.rect.x = x
        pygame.sprite.Sprite.__init__(self)
        blocks.add(self)
    def update(self):
        """ Move a block """
        self.rect.x -= BLOCK_SPEED # Move left
        if self.rect.x <= 0-self.rect.width: # Loop
            self.rect.x = SCREEN_WIDTH
class StaticObjects(): 
    """ All the static things that aren't part of the gameplay """
    class Screen():
        """ Things to do with drawing the screen """
        def draw():
            """ Make the screen things """
            pygame.draw.rect(screen,STATUS_BAR_COLOUR,(0,SCREEN_HEIGHT-50,SCREEN_WIDTH,SCREEN_HEIGHT)) # Draw the status bar
    class Heart(pygame.sprite.Sprite):
        def __init__(self,player,n):
            """ Init a heart """
            self.image = pygame.image.load('heart.png') # Aw <3
            self.image.set_colorkey((195,195,195)) # Colourkeys make a certain colour within a Surface transparent
            # I should have probably stuck to a consistent colourkey
            self.rect = self.image.get_rect()
            self.rect.y = SCREEN_HEIGHT-45 # Move the hearts
            if player == 1:
                self.rect.x = 10 + n*50
            else:
                self.rect.x = SCREEN_WIDTH-(n+1)*50
            pygame.sprite.Sprite.__init__(self)
            hearts.add(self)
    class Status(): # Stuff on the grey status bar
        def draw_hearts(): # The magical heart-placeing algorithm
            """ Organise hearts """
            for i in range(math.ceil(player1.life)):
                heart = StaticObjects.Heart(1,i)
            for i in range(math.ceil(player2.life)):
                heart = StaticObjects.Heart(2,i)
            # Score text
            p1scoretext = font.render(str(p1score),0,(0,0,255))
            screen.blit(p1scoretext,(screen.get_rect().centerx - p1scoretext.get_rect().width - 10,SCREEN_HEIGHT-45))
            p2scoretext = font.render(str(p2score),0,(255,0,0))
            screen.blit(p2scoretext,(screen.get_rect().centerx+p1scoretext.get_rect().width + 10,SCREEN_HEIGHT-45)) # EVERYTHING is relative, that's why it was so easy to make fullscreen toggling work
class Sounds(): # Sounds made in Sfxr, a retro synth
    lazer1 = pygame.mixer.Sound('Lazer1.ogg') # Pew
    lazer2 = pygame.mixer.Sound('Lazer2.ogg') # Pew pew
    explosion = pygame.mixer.Sound('Explosion.ogg') # Boom
    hit = pygame.mixer.Sound('Hit.ogg')
    bomb = pygame.mixer.Sound('Bomb.ogg')
    whistle = pygame.mixer.Sound('Whistle.ogg')
    theme = pygame.mixer.Sound('Theme.wav') # <-- This one was made in Musagi, retro sequencer and synth. Remake of the Space Invaders Advanced theme
class Explosion(pygame.sprite.Sprite): # Magical spawn-anywhere explosion object
    def __init__(self,x,y,type):
        """ Generate an explosion """
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
        self.sprite_change_cooldown = 0 # This part may or may not actually do anything
        self.image = self.sprites[0]
        self.image.set_colorkey((255,255,255)) # See? Inconsistent transparencies :(
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        pygame.sprite.Sprite.__init__(self)
        explosions.add(self)
    def update(self):
        """ Change explosion sprites """
        if pygame.time.get_ticks() - self.sprite_change_cooldown > EXPLOSION_COOLDOWN:
            self.xpos = self.rect.x # THESE TWO LINES ARE IMPORTANT
            self.ypos = self.rect.y # When a sprite changes images it resets its coordinates, so I had to store them and then re-move them
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
        """ Make a spaceship! Wooooooo """
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
        # Old deprecated velocity stuff - this never worked well
        #self.vx *= 0.8
        #if self.vx <= -0.1 and self.vx >= -0.2:
        #   self.vx = 0
        #self.rect.x += round(self.vx,1)
        """ Change sprites around """
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
        if self.firing: # These two IFs control which sprite set is active, the firing one or the basic flight one
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
        """ Send up or down a bomb """
        if pygame.time.get_ticks() - self.bomb_cooldown > BOMB_COOLDOWN and self.bombs > 0:
            Sounds.whistle.play()
            self.bombs -= 1
            if self.pn == 1:
                bomb = Bomb(self.rect.centerx - 12,self.rect.y, True)
            else:   
                bomb = Bomb(self.rect.centerx - 12,self.rect.y + SPRITE_SIZE, False)
            self.bomb_cooldown = pygame.time.get_ticks()
    def fire(self): # Pew pew
        """ Fire a bullet pair """
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
    """ Check collisions """
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
		""" Init a single bullet """
        if d: # If it's a bullet that goes up
            self.image = pygame.image.load('bullet_blue.png')
        else: # If not
            self.image = pygame.image.load('bullet_red.png')
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.x = px
        self.rect.y = py
        self.going_up = d
        pygame.sprite.Sprite.__init__(self)
        bullets.add(self)
    def update(self):
		""" Move a bullet """
        if self.going_up: # Goin' up
            self.rect.y -= BULLET_SPEED
        else: # Goin' down
            self.rect.y += BULLET_SPEED
class Bomb(pygame.sprite.Sprite):
    def __init__(self,px,py,d):
		""" Create a bomb. """
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
		""" Move a bullet """
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
    block = Block(random.randrange(0,SCREEN_WIDTH)) # Random block placement
explosions = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bombs = pygame.sprite.Group()
hearts = pygame.sprite.Group()
update_groups = [bombs,bullets,explosions,bomb_explosions,blocks,players]
player1 = Player(1)
player2 = Player(2)

done = False
Sounds.theme.play(-1) # Bleeeep blooooop
while not done: # Main
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                # Fullscreen flag imported from pygame.locals
				# This bit toggles fullscreen mode and sets different variables according to screen size
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
    if pressed[pygame.K_RIGHT] and player1.rect.x < SCREEN_WIDTH - player1.rect.width:        player1.rect.x += P1_MOVE
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
    hearts.empty()
    check_if_hit()
    # I tried to make this next bit shorter but it crashed pretty much everything so I didn't try it again. It draws all the sprites
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