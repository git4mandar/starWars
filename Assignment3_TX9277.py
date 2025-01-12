###########################################################################
# # CS 4849 : Game Programming - Spring 2009
# # Assignment 3: Star Wars - Mandar Shivrekar (TX9277)
# # Submission Date - 06/10/2009
# #
# # Game Motive:
# # Kill the opponent ship by firing at it. Save your ship by missing fired bullets.
# # Opponent ship will flee when its health falls below a certain limit
# # Tip to win: The opponent ship will make a seeking move just before 
# #             firing at you. Identify it and save yourself! :)
# #
# # Please Note:
# # The Ship fires when "SpaceBar" key is pressed
# #    If kept pressed the bullets are fired with a certain interval
# # The "left arrow" key steers the ship left
# # The "right arrow" key steers the ship right
# # The "up arrow" key steers the ship up
# # The "down arrow" key steers the ship down
# # One bullet hit will reduce the ship health by one
# # The current health of space ships is depicted by the health indicators besides them
# # F1 key press brings up the help onscreen. Press F1 again to remove help
# # ESC key press pauses the game. Press ESC again to continue
# # Q key increases the manually controlled ship speed
# # W key decreases the manually controlled ship speed
###########################################################################
# Credits:
# # Background song theme: "Star Wars" movie title song, TM & (c) Lucasfilm Ltd. 2009
# # Ship1 Image: (c) Thomas Models, 2000
# # Ship2 Image: Image from "ChrisAtWar" user at Sodahead.com
# # Bullet Images obtained from www.free-animations.co.uk
# # Background space image courtesy NASA (Hubble Space Telescope Imagery)
# # Explosion image from blog.sfweekly.com
# # Some code and code pattern used from kinematic_steering.py
# # Firing/Explosion/Destruction sounds obtained from shockwave-sound.com
###########################################################################
# Vote of Thanks:
# # Prof. Dr. William Thibault for an excellant course on Game Programming!
# # Sushant and Rama for their constructive feedback and help!
# # All classmates for designing and building amazing games, thereby elavating the class standard! :)
###########################################################################

SCREEN_SIZE = (800, 600)
BULLET_FIRING_RATE = 10 # Increase this to decrease the rate
DEFAULT_HEALTH = 100    # All Ship healths
FONT_NAME = "arial"
DEFAULT_FONT_SIZE = 16
WHITE = (255,255,255)   # Macro for WHITE color

import pygame, numpy, math
from pygame.locals import *
from gameobjects.vector2 import Vector2
from random import randint

# Base Singleton World Class
class World(object):
    def __init__(self, screen):
        self.screen = screen
        self.entities = {}
        self.entity_id = 0
        self.background = pygame.surface.Surface(SCREEN_SIZE).convert()
        image = pygame.image.load("space.jpg").convert_alpha()
        self.background.blit(image, (0,0))
        self.pauseFlag = False
        self.show_Help = True
        
        message = "Press F1 for more help"
        font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE)
        text_surface = font.render(message, True, WHITE)
        self.background.blit(text_surface, (2,2))
    
    def showHelp(self):
        self.show_Help = True

    def hideHelp(self):
        self.show_Help = False
    
    def showHelp_status(self):
        return self.show_Help
        
    def add_entity(self, entity):
        self.entities[self.entity_id] = entity
        entity.id = self.entity_id
        self.entity_id += 1
        
    def remove_entity(self, entity):
        del self.entities[entity.id]
                
    def get(self, entity_id):
        if entity_id in self.entities:
            return self.entities[entity_id]
        else:
            return None
        
    def process(self, time_passed):
        if self.pauseFlag == True:
            return
        time_passed_seconds = time_passed / 1000.0        
        for entity in self.entities.values():
            entity.process(time_passed_seconds)
            
    def render(self, surface):
        surface.fill((0,0,0))
        surface.blit(self.background, (0, 0))
        if self.pauseFlag == True:
            message = "GAME PAUSED"
            font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE*3)
            text_surface = font.render(message, True, WHITE)
            surface.blit(text_surface, (SCREEN_SIZE[0]/2-text_surface.get_width()/2,SCREEN_SIZE[1]/2-text_surface.get_height()/2))
            return
        if self.show_Help == True:
            message = "SPACE = Fire Bullet,   ARROW KEYS = Steer Ship"
            font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE)
            text_surface = font.render(message, True, WHITE)
            surface.blit(text_surface, (2,text_surface.get_height()))
            message = "q = Increase Ship Speed,   w = Decrease Ship Speed"
            font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE)
            text_surface = font.render(message, True, WHITE)
            surface.blit(text_surface, (2,text_surface.get_height()*2))
            message = "ESC = Pause Game"
            font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE)
            text_surface = font.render(message, True, WHITE)
            surface.blit(text_surface, (2,text_surface.get_height()*3))
            message = "Press F1 again to remove this message"
            font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE)
            text_surface = font.render(message, True, WHITE)
            surface.blit(text_surface, (2,text_surface.get_height()*4))
            
        for entity in self.entities.itervalues():
            entity.render(surface)
            
    def get_close_entity(self, name, location, range=10.):
        for entity in self.entities.values():            
            if entity.name == name:            
                distance_v = location - entity.position
                distance = math.sqrt(distance_v[0]**2+distance_v[1]**2)
                if distance < range:
                    return entity        
        return None

    def pause(self):
        self.pauseFlag = True
    
    def unPause(self):
        self.pauseFlag = False
        
    def pause_status(self):
        return self.pauseFlag
###############################################################

class SteeringOutput:
    def __init__ (self, lin=(0,0), ang=0. ):
        self.linear = numpy.array([float(lin[0]), float(lin[1])])
        self.angular = ang

###############################################################


def normalize ( vec2 ):
    len = math.sqrt(vec2[0]**2 + vec2[1]**2)
    return vec2 / len

def length ( vec2 ):
    len = math.sqrt(vec2[0]**2 + vec2[1]**2)
    return len
    

def getOrientationFromVelocity ( currentOrientation, velocity ):
# move into Kinematic
    if velocity[0]**2 + velocity[1]**2 > 0:
        return math.atan2(-velocity[1],velocity[0])
    else:
        return currentOrientation

def getVelocityFromOrientation ( orientationAngle ):
    vel = numpy.array([0.,0.])
    vel[0] = math.cos(orientationAngle)
    vel[1] = -math.sin(orientationAngle)
    return vel
    

###############################################################

class KinematicGameEntity(object):
    
    def __init__(self, world, name, image, think=0):
        
        # kinematic properties
        self.position = numpy.array([0.,0.])  
        self.velocity = numpy.array([0.,0.])
        self.target_position = numpy.array([float(randint(0, SCREEN_SIZE[0])), float(randint(0, SCREEN_SIZE[1]))])
        self.orientationAngle = 0
        self.angularVelocity = 0
        self.health = DEFAULT_HEALTH
        self.world = world
        self.name = name
        self.image = image
        self.move_resolution = 25
        self.steeringBehavior = None
        self.maxSpeed = 0
        self.id = 0
        self.fireSound = pygame.mixer.Sound("fire.wav")
        self.fireSound.set_volume(0.6)
        self.fire_clock = BULLET_FIRING_RATE
        self.set_think = think
        
    def render(self, surface):
        x, y = self.position
        rotSurf = pygame.transform.rotate ( self.image, self.orientationAngle/math.pi*180. )
        w, h = rotSurf.get_size()
        surface.blit(rotSurf, (x-w/2, y-h/2))   
        bar_x = x - 12
        bar_y = y + h/2
        surface.fill( (0, 255, 0), (bar_x, bar_y, 25, 4))
        surface.fill( (255, 0, 0), (bar_x, bar_y, 25-(self.health*25/DEFAULT_HEALTH), 4))
        
    def process(self, time_passed):
        if ( self.steeringBehavior != None ):
            steering = self.steeringBehavior.getSteering()
            if steering != None:
                self.velocity = steering.linear
                self.angularVelocity = steering.angular
            else:
                self.velocity = numpy.array([0.,0.])
                self.angularVelocity = 0.

        self.orientationAngle += self.angularVelocity * time_passed
        self.position += self.velocity * time_passed
        if self.health > 5:
            for i in (0,1):
                if self.position[i] > SCREEN_SIZE[i]:
                    self.position[i] -= SCREEN_SIZE[i]
                if self.position[i] < 0:
                    self.position[i] += SCREEN_SIZE[i]
        else:
            for i in (0,1):
                if self.position[i] > SCREEN_SIZE[i]:
                    self.position[i] -= (SCREEN_SIZE[i]+5)
                if self.position[i] < 0:
                    self.position[i] += (SCREEN_SIZE[i]-5)
                    
        if self.set_think == 1:
            self.think()
        
        if self.health == 0:
            explosion = Explosion(self.world, "Ship1Explosion1", (self.position[0]+self.image.get_width(),self.position[1]))
            self.world.add_entity(explosion)
            explosion = Explosion(self.world, "Ship1Explosion2", (self.position[0]-self.image.get_width(),self.position[1]))
            self.world.add_entity(explosion)
            explosion = Explosion(self.world, "Ship1Explosion3", (self.position[0],self.position[1]+self.image.get_height()))
            self.world.add_entity(explosion)
            explosion = Explosion(self.world, "Ship1Explosion4", (self.position[0],self.position[1]-self.image.get_height()))
            self.world.add_entity(explosion)

            ship1part0 = pygame.image.load("ship1part0.png").convert_alpha()
            explosion = Explosion(self.world, "ship1part0", (self.position[0]+self.image.get_width(),self.position[1]), 0.04, ship1part0)
            self.world.add_entity(explosion)
            ship1part1 = pygame.image.load("ship1part1.png").convert_alpha()
            explosion = Explosion(self.world, "ship1part1", (self.position[0]-self.image.get_width(),self.position[1]), 0.05, ship1part1)
            self.world.add_entity(explosion)
            ship1part2 = pygame.image.load("ship1part2.png").convert_alpha()
            explosion = Explosion(self.world, "ship1part2", (self.position[0],self.position[1]+self.image.get_height()), 0.06, ship1part2)
            self.world.add_entity(explosion)
            ship1part3 = pygame.image.load("ship1part3.png").convert_alpha()
            explosion = Explosion(self.world, "ship1part3", (self.position[0],self.position[1]-self.image.get_height()), 0.07, ship1part3)
            self.world.add_entity(explosion)
            
            explosionSound = pygame.mixer.Sound("destroyed.wav")
            explosionSound.set_volume(0.6)
            explosionSound.play()
            
            if self.name == "ship1":
                message = "Opponent Ship Defeated!! You WON!!"
                font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE*3)
                text_surface = font.render(message, True, WHITE)
                self.world.background.blit(text_surface, (SCREEN_SIZE[0]/2-text_surface.get_width()/2,SCREEN_SIZE[1]/2-text_surface.get_height()/2))
            else:
                message = "Your Ship Defeated!! You LOOSE!!"
                font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE*3)
                text_surface = font.render(message, True, WHITE)
                self.world.background.blit(text_surface, (SCREEN_SIZE[0]/2-text_surface.get_width()/2,SCREEN_SIZE[1]/2-text_surface.get_height()/2))
            
            message = "Game Programming by Mandar Shivrekar, CSU East Bay, 2009. Thanks to Prof. Thibault for such a wonderful course!"
            font = pygame.font.SysFont(FONT_NAME, DEFAULT_FONT_SIZE)
            text_surface = font.render(message, True, WHITE)
            self.world.background.blit(text_surface, (SCREEN_SIZE[0]/2-text_surface.get_width()/2,SCREEN_SIZE[1]/2+150))
            
            self.world.remove_entity(self)
        
    def hit(self):
        if self.health > 0:
            self.health -= 1
    
    def move_left(self):
        if(self.target_position[0] > 0):
            self.target_position += (-self.move_resolution,0)

    def move_right(self):
        if(self.target_position[0] < SCREEN_SIZE[0]):
            self.target_position += (self.move_resolution,0)
    
    def move_up(self):
        if(self.target_position[1] > 0):
            self.target_position += (0,-self.move_resolution)
                        
    def move_down(self):
        if(self.target_position[1] < SCREEN_SIZE[1]):
            self.target_position += (0,self.move_resolution)
    
    def increaseSpeed(self):
        if self.maxSpeed < 500:
            self.maxSpeed += 5

    def decreaseSpeed(self):
        if self.maxSpeed > 0:
            self.maxSpeed -= 5
        
    def think(self):
        alien = self.world.get_close_entity("ship2", self.position, range=math.sqrt(SCREEN_SIZE[0]**2+SCREEN_SIZE[1]**2))
        if self.health <= 0:
            self.steeringBehavior = KinematicFlee ( self, alien, 0 )
            return
        
        if self.health < 5:
            self.steeringBehavior = KinematicFlee ( self, alien, 75 )
            return
            
        alien = self.world.get_close_entity("ship2", self.position, range=float(self.image.get_width()*3))
        if alien != None:
            if alien.health <= 0:
                return
            self.steeringBehavior = KinematicArrive ( self, alien, 10, 1 )
            return
            
        alien = self.world.get_close_entity("ship2", self.position, range=float(self.image.get_width()*4))
        if alien != None:
            if alien.health <= 0:
                return
            self.steeringBehavior = KinematicSeek ( self, alien )
            return
        
        alien = self.world.get_close_entity("ship2", self.position, range=float(self.image.get_width()*5))
        if alien != None:
            if alien.health <= 0:
                return
            self.steeringBehavior = KinematicArrive ( self, alien, 40, 0 )
            return
        
        self.steeringBehavior = KinematicWander ( self, alien, 100, 8 )
        
    def fire(self):
        if self.health > 0:
            self.fire_clock -= 1
            if self.fire_clock > 0:
                return
            bullet = pygame.image.load("bullet.gif").convert_alpha()
            bullet = Bullet ( self.world, self.name+"_bullet", self.position, \
                            math.degrees(self.orientationAngle), bullet )
            self.world.add_entity(bullet)
            self.fireSound.set_volume(0.6)
            self.fireSound.play()
            self.fire_clock = BULLET_FIRING_RATE
            
##########################################################

class SteeringBehavior:
    def __init__(self):
        pass
    def getSteering(self):
        pass

class KinematicStationary ( SteeringBehavior ):
    def __init__(self, character ):
        self.character = character
        self.target = character
        self.maxSpeed = 0

    def getSteering (self):
        velocity = 0
        velocity *= self.maxSpeed
        return SteeringOutput ( velocity, 0. )
        

class KinematicSeek ( SteeringBehavior ):
# Seek moves always at full speed, will overshoot and oscillate if it reaches target
    def __init__(self, character, target, maxSpeed=100., huntMode=0 ):
        self.character = character
        self.target = target
        self.maxSpeed = maxSpeed
        self.hunt = huntMode

    def getSteering (self):
        velocity = self.target.position - self.character.position
        velocity = normalize(velocity)
        velocity *= self.maxSpeed
        # face in the direction the character is going
        self.character.orientationAngle = getOrientationFromVelocity ( \
            self.character.orientationAngle, velocity)
        if(self.hunt == 1):
            self.character.fire()
        return SteeringOutput ( velocity, 0. )

class KinematicFlee ( SteeringBehavior ):
    def __init__(self, character, target, maxSpeed=100. ):
        self.character = character
        self.target = target
        self.maxSpeed = maxSpeed

    def getSteering (self):
        velocity =  self.character.position - self.target.position
        velocity = normalize(velocity)
        velocity *= self.maxSpeed
        # face in the direction the character is going
        self.character.orientationAngle = getOrientationFromVelocity ( \
            self.character.orientationAngle, velocity)
        return SteeringOutput ( velocity, 0. )

class KinematicArrive ( SteeringBehavior ):
# Arrive slows down as it reaches target, stops if within radius of target
    def __init__(self, character, target, maxSpeed=40., huntMode=0, radius=32, ttt=0.25 ):
        self.character = character
        self.target = target
        self.maxSpeed = maxSpeed
        self.radius = radius
        self.timeToTarget = ttt
        self.hunt = huntMode

    def getSteering (self):
        velocity = self.target.position - self.character.position
        distsq = velocity[0]**2 + velocity[1]**2
        if distsq < self.radius**2:
            if(self.hunt == 1):
                self.character.fire()
            return None
        velocity /= self.timeToTarget
        distsq = velocity[0]**2 + velocity[1]**2
        if distsq > self.maxSpeed * self.maxSpeed:
            velocity = normalize(velocity)
            velocity *= self.maxSpeed
        # face in the direction the character is going
        self.character.orientationAngle = getOrientationFromVelocity ( \
            self.character.orientationAngle, velocity)
        if(self.hunt == 1):
            self.character.fire()
        return SteeringOutput ( velocity, 0. )

class KinematicWander ( SteeringBehavior ):
    def __init__(self, character, target=None, maxSpeed=40., maxAngularVel=10. ):
        self.character = character
        self.target = target
        self.maxSpeed = maxSpeed
        self.maxAngularVel = maxAngularVel

    def getSteering (self):
        velocity = getVelocityFromOrientation(self.character.orientationAngle)
        velocity *= self.maxSpeed
        # change our orientation randomly
        angle = numpy.random.uniform() - numpy.random.uniform()
        angle *= self.maxAngularVel
        return SteeringOutput ( velocity, angle )

class KinematicManual ( SteeringBehavior ):
    def __init__(self, character, target=None, maxSpeed=300., radius=32, ttt=0.25 ):
        self.character = character
        self.target_position = self.character.target_position
        self.character.maxSpeed = maxSpeed
        self.maxSpeed = self.character.maxSpeed
        self.radius = radius
        self.timeToTarget = ttt

    def getSteering (self):
        velocity = self.target_position - self.character.position
        distsq = velocity[0]**2 + velocity[1]**2
        if distsq < self.radius**2:
            return None
        velocity /= self.timeToTarget
        distsq = velocity[0]**2 + velocity[1]**2
        if distsq > self.character.maxSpeed * self.character.maxSpeed:
            velocity = normalize(velocity)
            velocity *= self.character.maxSpeed
            
        # face in the direction the character is going
        self.character.orientationAngle = getOrientationFromVelocity ( \
            self.character.orientationAngle, velocity)
        return SteeringOutput ( velocity, 0. )
        
##########################################################

class Bullet(object):
    # Initialize the bullet object
    def __init__(self, world, name, pos, orientationAngle, image):
        x,y = pos
        self.position = numpy.array([float(x),float(y)])  
        self.velocity = numpy.array([10.,10.])
        self.orientationAngle = orientationAngle
        self.angularVelocity = 0
        self.health = 1
        self.world = world
        self.name = name
        self.image = image
        self.hit = 0
        self.steeringBehavior = None
        
        self.id = 0
        
    # Draw the bullet
    def render(self, surface):
        x, y = self.position
        w, h = self.image.get_size()
        surface.blit(self.image, (x-w/2, y-h/2))   
    
    # update the bullet position
    def process(self, time_passed=0):
        if(self.name == "ship1_bullet"):
            ship = self.world.get_close_entity("ship2", self.position, 50)
        if(self.name == "ship2_bullet"):
            ship = self.world.get_close_entity("ship1", self.position, 50)
        if ship is not None:
            distance_v = self.position - ship.position
            distance = math.sqrt(distance_v[0]**2+distance_v[1]**2)
            if distance < ship.image.get_width()-10:
                ship.hit()
                fireSound = pygame.mixer.Sound("explarr.wav")
                fireSound.set_volume(0.6)
                fireSound.play()
                self.image = pygame.image.load("explosion.png").convert_alpha()
                if self.hit == 1:
                    explosion = Explosion(self.world, self.name+"_explosion", self.position, 0.15)
                    self.world.add_entity(explosion)
                    self.world.remove_entity(self)
                    return
                self.hit = 1
                return
        
        destination = numpy.array([(self.velocity[0]*math.cos(math.radians(self.orientationAngle))),(-self.velocity[1]*math.sin(math.radians(self.orientationAngle)))])
        self.position += destination

##########################################################

class Explosion(object):
    # Initialize the explosion object
    def __init__(self, world, name, pos=(0,0), rate=0.03, image=None):
        self.world = world
        self.name = name
        self.position = pos
        self.rate = rate
        self.distance = 0
        self.alpha = 1  # lerp factor for color
        self.isexpired = False
        if image == None:
            self.image = pygame.image.load("bullet.gif").convert_alpha()
        else:
            self.image = image
    
    # Update the explosion particle positions and color using lerp
    def process(self, time_passed=0):
        self.distance += 2
        self.alpha -= self.rate
        if(self.alpha < 0):
            self.world.remove_entity(self)
    
    # Draw the explosion particles
    def render(self, surface):
        x,y = self.position
        for angle in range(0, 360, 20):
            surface.blit(self.image, ( int(x+(self.distance*(-1)*math.cos(math.radians(angle)))), int(y+(self.distance*math.sin(math.radians(angle)))) ))
      
##########################################################
     

def run():
    
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
    
    # set window title
    pygame.display.set_caption("Program #3 Star Wars - Mandar Shivrekar (TX9277)") # Set window title
    pygame.key.set_repeat(20,20)
    
    # Start background music
    pygame.mixer.music.load("StarTrekTheme.ogg")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)
    
    world = World(screen)

    w, h = SCREEN_SIZE
    clock = pygame.time.Clock()
        
    ship1 = pygame.image.load("ship1.png").convert_alpha()
    ship1 = KinematicGameEntity ( world, "ship1", ship1, 1 )
    
    ship2 = pygame.image.load("ship2.png").convert_alpha()
    ship2 = KinematicGameEntity ( world, "ship2", ship2 )
    
    for ship in (ship1, ship2):
        ship.position = numpy.array([float(randint(0, w)), float(randint(0, h))])
        world.add_entity(ship)
    
    ship1.steeringBehavior = KinematicWander ( ship1, ship2, 100, 8 )
    ship2.steeringBehavior = KinematicManual ( ship2, ship1 )
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            if event.type == KEYDOWN:
                if world.pause_status() == False:
                    if event.key == K_SPACE:
                        ship2.fire()
                        pygame.event.clear()
                        
                    if event.key == K_LEFT:
                        ship2.move_left()
                        pygame.event.clear()
                   
                    if event.key == K_RIGHT:
                        ship2.move_right()
                        pygame.event.clear()
                    
                    if event.key == K_UP:
                        ship2.move_up()
                        pygame.event.clear()
                    
                    if event.key == K_DOWN:
                        ship2.move_down()
                        pygame.event.clear()
                        
                    if event.key == K_q:
                        ship2.increaseSpeed()
                        pygame.event.clear()
            
                    if event.key == K_w:
                        ship2.decreaseSpeed()
                        pygame.event.clear()

                    if event.key == K_F1:
                        clock.tick(100)
                        if world.showHelp_status() == False:
                            world.showHelp()
                        else:
                            world.hideHelp()
                        pygame.event.clear()

                if event.key == K_ESCAPE:
                    clock.tick(100)
                    if world.pause_status() == False:
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                        world.pause()
                    else:
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()
                        world.unPause()
                    pygame.event.clear()
        
        time_passed = clock.tick(30)
        
        world.process(time_passed)
        world.render(screen)
        
        pygame.display.update()
    
if __name__ == "__main__":    
    run()
    pygame.quit()
    
