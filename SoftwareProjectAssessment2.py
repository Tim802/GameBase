#importing required modules
import pygame
from random import randint
from pygame.locals import (
    QUIT,
    K_ESCAPE,
    KEYDOWN,
    K_w,
    K_a,
    K_s,
    K_d,
    K_SPACE
)

'''A base model of a game to be expanded upon if wished, useful for accelerating the production process of a video game by reducing the amount of set up'''


class Game():

    '''
    A class containing all necessary objects for running the game.
    '''

    #colours commonly used in the game
    blue = (0,0,255)
    red = (255,0,0)
    green = (0,255,0)
    black = (0,0,0)
    white = (255,255,255)

    #dimensions of the screen
    WinDim = (800,600)

    #lists for containing the bullets and enemies in the game
    projectiles = []
    enemies = []

    #default directional arguments for the player
    playerdir = 'x'
    playerfacing = 1

    def __init__(self) -> None:

        '''Running the initial definitions and activating the clock to start the game'''

        #creating screen
        self.win = pygame.display.set_mode(Game.WinDim)
        #Setting top caption
        pygame.display.set_caption('The Best Game You Ever Did Lay Eyes Upon')
        #Setting framrate max
        self.FramePerSec = pygame.time.Clock()
        self.FPS = 60

        #creating clock for enemy spawning and adding an initial delay
        self.enclock = pygame.time.Clock()
        self.enclock.tick()
        self.endelay = 1000

        #checking if the game is running
        self.running = True

    def run(self):

        '''Accessing child classes and pygame functions to run and render the game'''

        #instantiating the player and making it accessable to all classes
        global p1
        p1 = Player()

        #main loop
        while self.running:
            #checking to see if a key is pressed, then activating the corresponding function if true
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif event.key == K_SPACE:
                        #adds bullet to projecctile list
                        Game.projectiles.append(Bullet())
                elif event.type == QUIT:
                    self.running = False
            
            #moving the player if required
            p1.update()

            #updating the enemies
            for entity in Game.enemies:
                entity.update()
                entity.x = entity.rect.left
                entity.y = entity.rect.top

            #updating the bullets
            for bullet in Game.projectiles:
                bullet.update()

            #adding individual components to the screen
            self.win.fill(Game.black)
            
            #rendering player
            p1.draw(self.win)

            #rendering enemies
            for entity in Game.enemies:
                entity.draw(self.win)

            #rendering bullets
            for bullet in Game.projectiles:
                bullet.draw(self.win)

            #check to see if max enemies is reached, then spawning enemy after delay
            if len(Game.enemies) < 10:

                self.endelay = self.endelay - self.enclock.tick()

                if self.endelay <= 0:
                    Game.enemies.append(Enemy(randint(0,3)))
                    self.endelay = randint(500, 1500)
                    self.enclock.tick()

            #updating the screen
            pygame.display.update()
            self.FramePerSec.tick(self.FPS)

class Entity(Game, pygame.sprite.Sprite):

    '''A parent class of the entities in the game. Provides basic rendering and movement capabilities'''

    def __init__(self,dim,colour, maxspeed, speed) -> None:
        super().__init__()
        pygame.sprite.Sprite.__init__(self)
        #basic data on the player
        self.dim = dim
        self.colour = colour
        self.maxspeed = maxspeed
        self.speed = speed
       
        #creating surface and rect components of player
        self.image = pygame.Surface((self.dim,self.dim))
        self.image.fill(self.colour)
        self.rect = self.image.get_rect()
        
        #setting init velocity to 0
        self.velx = 0
        self.vely = 0

        #setting init prevel to 0
        self.preVelx = 0
        self.preVely = 0

    def update(self):

        '''Updates the position of the entity based on input data, moves the rect object of the entity into new position'''

        #checking to see if any velocity is being added, then +/- vel to reach 0
        if self.velx == 0:
            if self.preVelx > 0:
                self.velx = -1
            elif self.preVelx < 0:
                self.velx = 1
        if self.vely == 0:
            if self.preVely > 0:
                self.vely = -1
            elif self.preVely < 0:
                self.vely = 1

        #adding prev frame vel to current
        self.velx = self.velx + self.preVelx
        self.vely = self.vely + self.preVely

        #checking against max speed, then setting to max speed if reached
        if self.velx > self.maxspeed:
            self.velx = self.maxspeed
        elif self.velx < -self.maxspeed:
            self.velx = -self.maxspeed

        if self.vely > self.maxspeed:
            self.vely = self.maxspeed
        elif self.vely < -self.maxspeed:
            self.vely = -self.maxspeed

        #moving player within screen bounds
        self.rect.move_ip(self.velx, self.vely)
        self.rect.clamp_ip((0,0), Game.WinDim)

        #setting current vel to prev vel for next calculation
        self.preVelx = self.velx
        self.preVely = self.vely

    def draw(self, surface):

        '''Renders the surface object of the entity onto the screen'''

        surface.blit(self.image, self.rect)

class Player(Entity):

    '''Child class of entity. contains checks for movement conditions, as well as init info'''

    def __init__(self):

        '''creates and centres the player object, also calls Entity.__init__()'''

        super().__init__(10, Game.white, 20, 4)
        #centres character in middle of screen
        self.x = self.rect.centerx
        self.y = self.rect.centery
        self.rect.center = (400,300)
        
    def update(self):

        '''Checks to see if a movement key has been pressed, adds velocity, then calls Entity.update() for movement'''

        kpress = pygame.key.get_pressed()

        #checking for a key press, adding velocity for corresponding key press, and updating directional info
        if kpress[K_w]:
            self.vely = -self.speed
            Game.playerdir = 'y'
            Game.playerfacing = 1
        elif kpress[K_s]:
            self.vely = self.speed
            Game.playerdir = 'y'
            Game.playerfacing = -1
        else:
            self.vely = 0
        if kpress[K_d]:
            self.velx = self.speed
            Game.playerdir = 'x'
            Game.playerfacing = 1
        elif kpress[K_a]:
            self.velx = -self.speed
            Game.playerdir = 'x'
            Game.playerfacing = -1
        else:
            self.velx = 0

        #setting positional data
        self.x = self.rect.centerx
        self.y = self.rect.centery

        super().update()

class Bullet(Entity):

    '''A child of Entity() class, contains all information on the creation and translation of bullet objects'''

    def __init__(self):

        '''finds default information from player character for creation of entity'''

        super().__init__(3, Game.white, 30, 30)
        #finding player data for spawning
        self.direction = Game.playerdir
        self.facing = Game.playerfacing
        self.playerx = p1.rect.centerx
        self.playery = p1.rect.centery

        #centring the bullet on player location
        self.rect.centerx = self.playerx
        self.rect.centery = self.playery

        #making the bullet object independant of player object. New updates to player won't affect bullet
        self.x = self.playerx
        self.y = self.playery

    def update(self):

        '''takes information from initialisation and uses this to move the bullet at max speed, also destroys bullet if reached the end of screen'''

        #finding the direction player is facing, moving bullet by speed unless outside bounds. If outside bounds object is deleted from list
        if self.direction == 'x':
            if self.x > 1 and self.x < (Game.WinDim[0] - 2):
                self.velx = self.facing * self.maxspeed
            else:
                Game.projectiles.pop(Game.projectiles.index(self))
        if self.direction == 'y':
            if self.y > 1 and self.y < (Game.WinDim[1] - 2):
                self.vely = -self.facing * self.maxspeed
            else:
                Game.projectiles.pop(Game.projectiles.index(self))

        super().update()

        self.x = self.rect.centerx
        self.y = self.rect.centery

    def draw(self, win):

        '''renders the bullet object onto the screen as a circle'''

        pygame.draw.circle(win, Game.white, (self.x,self.y), self.dim)

class Enemy(Entity):

    '''A child of the Entity() class. contains the tracking of the player and randomised creation of the entity'''

    def __init__(self,start):

        '''randomises the spawn conditions of the entity and sets the objects for its position'''

        super().__init__(randint(5,10), Game.red, randint(1,15), randint(1,5))
        #centring enemy on spawn location data
        self.start = start
        self.x = self.rect.centerx
        self.y = self.rect.centery

        #finding which side to spawn enemy on from randint, then spawning enemy at random point on that side
        if self.start == 0:
            self.x = 0
            self.y = randint(0, (Game.WinDim[1] - self.dim))
        elif self.start == 1:
            self.x = Game.WinDim[0] - self.dim
            self.y = randint(0, (Game.WinDim[1] - self.dim))
        elif self.start == 2:
            self.x = randint(0, (Game.WinDim[0] - self.dim))
            self.y = 0
        elif self.start == 3:
            self.x = randint(0, Game.WinDim[0] - self.dim)
            self.y = Game.WinDim[1] - self.dim
        else:
            pass

    def update(self):

        '''Finds the position of the player, compares to current position and adds velocity in the direction of the player'''
        
        #compares position of player to current pos. adds vel to reach player
        if p1.rect.centerx > self.x:
            self.velx = self.speed
        elif p1.rect.centerx < self.x:
            self.velx = -self.speed
        else:
            self.velx = 0

        if p1.rect.centery > self.y:
            self.vely = self.speed
        elif p1.rect.centery < self.y:
            self.vely = -self.speed
        else:
            self.vely = 0

        super().update()

#instantiating the game and running it
game = Game()
game.run()

#quitting the game at end of program
pygame.quit