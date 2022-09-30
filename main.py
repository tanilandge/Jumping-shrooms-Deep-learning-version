import math
from numpy import append
import pygame
import os
import random
import time
import sys
import neat

WIDTH = 550
HEIGHT = 643
FPS = 64
PLAYER_STARTING_COORDINATES = 595
FONTNAME = 'freesansbold.ttf'
COLOUR =  (225, 215, 191)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy birds ig')
clock = pygame.time.Clock()

# set up asset folders
gameFolder = os.path.dirname(__file__)
imgFolder = os.path.join(gameFolder, 'img')
bg = pygame.image.load(os.path.join(imgFolder, "bg_shroom.png")).convert()
playerImg = pygame.image.load(os.path.join(imgFolder, 'p3_front.png')).convert() 
playerImg2 = pygame.image.load(os.path.join(imgFolder, 'p3_jump.png')).convert()
pipesBottomImg = pygame.image.load(os.path.join(imgFolder, 'bottomShroom3.png')).convert()
pipesTopImg = pygame.image.load(os.path.join(imgFolder, 'topShroom3.png')).convert()
pygame.display.flip()

# set up superclass sprite
class Sprite:
    def __init__(self, x, y, spriteImg1, spriteImg2):
        pygame.sprite.Sprite.__init__(self)
        self.image = spriteImg1
        self.image2 = spriteImg2
        self.image.set_colorkey((0, 0, 0))
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Pipes(Sprite, pygame.sprite.Sprite):
    def __init__(self, x, y, spriteImg1, spriteImg2):
        Sprite.__init__(self, x, y, spriteImg1, spriteImg2)
        self.x = x
        self.y = y
        self.listOfPipes = []
        self.namesOfPipes = [["bottomShroom1.png", "topShroom1.png"], ["bottomShroom2.png", "topShroom2.png"], ["bottomShroom3.png", "topShroom3.png"],  ["bottomShroom4.png", "topShroom4.png"]]
        self.pipesCoords = [[105, 531], [125, 551], [62, 487], [160, 585]]

    def getPipesImage(self, item):  
        pipesBottomImg = pygame.image.load(os.path.join(imgFolder, item[0])).convert()
        pipesTopImg = pygame.image.load(os.path.join(imgFolder, item[1])).convert()
        return pipesBottomImg, pipesTopImg

    def checkIfThereWerePreviousPipes(self):
        if len(self.listOfPipes) > 0:
            return True
        else:
            return False
        
    def createPipes(self, numberOfPipes, allSprites):
        prevPipes = self.checkIfThereWerePreviousPipes()
        if prevPipes:
            pipeX, pipeY = self.listOfPipes[-1].getPipesCoordinates()
            self.x = pipeX + 400
        
        for count in range(0, numberOfPipes):
            item = random.randint(0, len(self.namesOfPipes) - 1)
            pipesBottomImg, pipesTopImg = self.getPipesImage(self.namesOfPipes[item])
            bottomPipes = BottomPipe(self.x, self.pipesCoords[item][1], pipesTopImg, pipesBottomImg)
            topPipes = TopPipe(self.x, self.pipesCoords[item][0], pipesTopImg, pipesBottomImg)
            allSprites.add(bottomPipes)
            allSprites.add(topPipes)
            self.listOfPipes.append(bottomPipes)
            self.listOfPipes.append(topPipes)
            self.x += 400 
    
    def movePipesForward(self):
        for item in self.listOfPipes:
            pipeX, pipeY = item.getPipesCoordinates()
            pipeX -= 1
            item.setPipesCoordinates(pipeX, pipeY)

    def checkIfPipeIsNoLongerOnScreen(self, pipes, allSprites):
        PipeX, PipeY = self.listOfPipes[0].getPipesCoordinates()
        if PipeX <= -100:
            pipes.createPipes(1, allSprites)
            allSprites.remove(self.listOfPipes[0])
            self.listOfPipes.remove(self.listOfPipes[0])

    def getCurrentPipe(self):
        return self.listOfPipes[0], self.listOfPipes[1]

# set up pipes subclass 
class BottomPipe(Pipes, pygame.sprite.Sprite):
    def __init__(self, x, y, topPipeImg, bottomPipeImg):
        Pipes.__init__(self, x, y, topPipeImg, bottomPipeImg)
        self.image = bottomPipeImg
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def getPipesCoordinates(self):
        return self.x, self.y

    def setPipesCoordinates(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)

class TopPipe(Pipes, pygame.sprite.Sprite):
    def __init__(self, x, y, topPipeImg, bottomPipeImg):
        Pipes.__init__(self, x, y, topPipeImg, bottomPipeImg)
        self.image = topPipeImg
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def getPipesCoordinates(self):
        return self.x, self.y

    def setPipesCoordinates(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        
# set up subclass Player to inherit from the superclass 'sprite'
class Player(Sprite, pygame.sprite.Sprite):
    def __init__(self, x, y, spriteImg1, spriteImg2):
        Sprite.__init__(self, x, y, spriteImg1, spriteImg2)
        spriteImg1 = playerImg
        spriteImg2 = playerImg2
        self.score = 0
        self.heightJumped = 0
        self.playerCurrentlyMovingUp = False
        self.playerInitialPos = [self.y]
        self.xValueOfSin = 0
        self.xValueOfCos = 0

    def changeSpriteImg(self, jumpImg):
        if jumpImg:
            self.image = playerImg2
        else:
            self.image = playerImg
        self.image.set_colorkey((0, 0, 0))

    def moveUp(self, xValueOfSin, playerInitialPos):  # move player sprite upwards
        self.y = playerInitialPos[-1] - (90 * math.sin(math.radians(xValueOfSin)))
        self.heightJumped = self.y
        self.rect.center = (self.x, self.y)

    def moveDown(self, xValueOfCos):  # move player sprite downwards
        self.y = HEIGHT - ((HEIGHT-self.heightJumped) * math.cos(math.radians(xValueOfCos)))
        self.rect.center = (self.x, self.y)

    def getCoordinates(self):
        return self.x, self.y

    def isDead(self, pipes, gameStarted):
        playerXValue, playerYValue = self.getCoordinates()
        bottomPipe, topPipe = pipes.getCurrentPipe()
        if gameStarted:
            if self.rect.colliderect(bottomPipe.rect) or self.rect.colliderect(topPipe.rect) or self.y >= 595:
               # print("dead")
                return True
        return False
    
    def increaseScore(self, pipes):
        playerX, playerY = self.getCoordinates()
        bottomPipe, topPipe = pipes.getCurrentPipe()
        bottomPipeX, bottomPipeY = bottomPipe.getPipesCoordinates()
        topPipeX, topPipeY = topPipe.getPipesCoordinates()
        if (playerX + 34) == (bottomPipeX - 103) or (playerX + 34) == (topPipeX - 103):
            return True
        return False

def main(genomes, config):
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(50, 300, playerImg, playerImg2))
        g.fitness = 0
        ge.append(g)

    #set up sprites
    #player = Player(50, 300, playerImg, playerImg2)
    
    pipes = Pipes(500, 488, pipesTopImg, pipesBottomImg)

    allSprites = pygame.sprite.Group()
    allSprites.add(players)
    pipes.createPipes(3, allSprites)

    #xValueOfCos = 0
    #xValueOfSin = 0
    #
    # playerInitialPos = [300] #[player.y]

    done = False
    #
    # playerCurrentlyMovingUp = False
    gameStarted = True
    timeDelay = 0

    while not done:
        dt = clock.tick(FPS) / 1000
        timeDelay += + dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(players) > 0:
            pipe0, pipe1 = pipes.getCurrentPipe()
        else:
            done = True
            break

        pygame.init()
        keys = pygame.key.get_pressed()

        for x, player in enumerate(players):
            output = nets[x].activate((player.y, abs(player.y - pipe0.rect.y),  abs(player.y -  pipe1.rect.y)))
            
            if output[0] > 0.5:
                #gameStarted = True
                #print("bye")
                ge[x].fitness += 0.0001
                player.playerCurrentlyMovingUp = True
                player.playerInitialPos.append(player.y)
                
            
            if player.playerCurrentlyMovingUp == True: # and timeDelay > 0.001
                #print("bye")
                player.changeSpriteImg(True)
                player.moveUp(player.xValueOfSin, player.playerInitialPos)
                #print(player.playerInitialPos[-1], player.y)

                if (player.playerInitialPos[-1] - player.y) >= 90:
                    player.playerCurrentlyMovingUp = False
                    player.playerInitialPos.pop()
                    player.xValueOfSin = 0       #player has finished moving up so reset x
                else:
                    player.xValueOfSin += 2.5
                player.xValueOfCos = 0

            if player.y < PLAYER_STARTING_COORDINATES and player.playerCurrentlyMovingUp == False: #and timeDelay > 0.01
                player.changeSpriteImg(False)
                player.moveDown(player.xValueOfCos)
                player.xValueOfCos += 1

            if player.y >= PLAYER_STARTING_COORDINATES: #keeeps player on the floor
                player.y = PLAYER_STARTING_COORDINATES

            if player.y < 45: #keeps player for going up out ofthe screen
                player.y = 45
                player.playerCurrentlyMovingUp = False

            
            increaseScore = player.increaseScore(pipes)
            dead = player.isDead(pipes, gameStarted)

            if dead:
                ge[x].fitness -= 1
                players.pop(x)
                nets.pop(x)
                ge.pop(x)
                allSprites.remove(player)

            elif dead == False and increaseScore == True:
                player.score += 1
                for g in ge:
                    g.fitness += 3

        pipes.movePipesForward()
        pipes.checkIfPipeIsNoLongerOnScreen(pipes, allSprites) 
        allSprites.update()
        screen.blit(bg, (0, 0))
        font = pygame.font.Font(FONTNAME, 40)
        text = 'Score:' + str(player.score)
        textSurface = font.render(text, True, BLACK)
        textRect = textSurface.get_rect()
        textRect.center = (450, 60)
        screen.blit(textSurface, textRect)
        allSprites.draw(screen)
        pygame.display.flip()

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)

if __name__ == "__main__":
    config_path = os.path.join(gameFolder, "config-feedforward.txt")
    run(config_path)
        





