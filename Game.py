import sys
import pygame
import math
import random
from pydub import AudioSegment
from pydub.playback import play
from math import *


def length(vec):
    return sqrt(vec[0] * vec[0] + vec[1] * vec[1])


class Actor:
    def __init__(self, speed, position, friction):

        self.speed = speed
        self.position = position
        self.friction = friction
        self.acceleration = [0, 0]

    def accelerate(self):
        return

    def modifySpeed(self):
        self.speed[0] *= self.friction
        self.speed[1] *= self.friction
        return

    def move(self):
        self.accelerate()

        self.speed[0] += self.acceleration[0]
        self.speed[1] += self.acceleration[1]

        self.modifySpeed()

        self.position[0] = self.position[0] + self.speed[0]
        self.position[1] = self.position[1] + self.speed[1]

    def draw(self):
        return


class PolygonActor(Actor):
    def __init__(self, speed, position, friction, size, numSides):
        super().__init__(speed, position, friction)
        self.size = size
        self.numSides = numSides
        red = random.randint(20, 255)
        green = random.randint(20, 255)
        blue = random.randint(20, 255)
        self.color = [red, green, blue]

    def generatePoly(self):
        verts = []
        for i in range(0, self.numSides):
            angle = 2.0 * math.pi / self.numSides * i
            x = self.size * cos(angle) + self.position[0]
            y = self.size * sin(angle) + self.position[1]
            verts.append([x, y])
        self.verts = verts

    def draw(self):
        self.generatePoly()
        pygame.draw.aalines(
            screen, [self.color[0], self.color[1], self.color[2]], True, self.verts)
        pygame.draw.polygon(
            screen, [self.color[0], self.color[1], self.color[2]], self.verts)

    def collidesWith(self, otherPolygonActor):
        dx = self.position[0]-otherPolygonActor.position[0]
        dy = self.position[1]-otherPolygonActor.position[1]
        dist = sqrt(dx*dx + dy*dy)
        return dist < self.size + otherPolygonActor.size


class PlayerActor(PolygonActor):

    def accelerate(self):
        keys = pygame.key.get_pressed()
        accLimit = 0.4
        self.acceleration = [0, 0]
        if keys[pygame.K_LEFT]:
            self.acceleration[0] -= accLimit
        if keys[pygame.K_RIGHT]:
            self.acceleration[0] += accLimit
        if keys[pygame.K_UP]:
            self.acceleration[1] -= accLimit
        if keys[pygame.K_DOWN]:
            self.acceleration[1] += accLimit

        accMag = length(self.acceleration)
        if (accMag > accLimit):
            self.acceleration[0] = self.acceleration[0] / accMag * accLimit
            self.acceleration[1] = self.acceleration[1] / accMag * accLimit

    def modifySpeed(self):
        speedLimit = 8
        speedMag = length(self.speed)
        if (speedMag > speedLimit):
            self.speed[0] = self.speed[0] / speedMag * speedLimit
            self.speed[1] = self.speed[1] / speedMag * speedLimit

        super().modifySpeed()

    def move(self):
        super().move()
        if self.position[0] < self.size:
            self.position[0] = self.size
        if self.position[0] > width - self.size:
            self.position[0] = width - self.size
        if self.position[1] < self.size:
            self.position[1] = self.size
        if self.position[1] > height - self.size:
            self.position[1] = height - self.size


class EnemyActor(PolygonActor):

    def __init__(self):

        pos = [0, 0]
        spd = [0, 0]
        size = random.randint(1, 40)
        edge = random.randint(0, 3)
        degree = random.randint(4, 6)
        if (edge == 0):  # Left Edge
            pos = [-size, random.randint(0, height)]
            spd = [1, 0]
        elif (edge == 1):  # Right Edge
            pos = [width+size, random.randint(0, height)]
            spd = [-1, 0]
        elif (edge == 2):  # Top Edge
            pos = [random.randint(0, width), -size]
            spd = [0, 1]
        elif (edge == 3):  # Bottom Edge
            pos = [random.randint(0, width), height+size]
            spd = [0, -1]

        randSpeed = random.randint(20, 100)/60
        spd[0] *= randSpeed
        spd[1] *= randSpeed
        super().__init__(spd, pos, 1, size, degree)


pygame.init()

score = 0

font = pygame.font.SysFont("arialroundedmtbold", 20)

song = AudioSegment.from_wav("chomp.wav")

size = width, height = 512, 512

screen = pygame.display.set_mode(size)

player = PlayerActor([0, 0], [width/2, height/2], 0.9, 4, 8)

enemies = []


isDone = False
gameOver = False
while isDone == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    if random.randint(1, 50) == 1:
        enemies.append(EnemyActor())

    screen.fill([0, 0, 0])
    if gameOver == False:
        player.move()
    player.draw()

    for enemy in enemies:
        if gameOver == False:
            enemy.move()
        enemy.draw()

    nonCollidingEnemies = []
    for enemy in enemies:
        if player.collidesWith(enemy):
            if player.size > enemy.size:
                player.size += 1
                score += 1
                play(song)
            else:
                isDone = False
                gameOver = True
        else:
            nonCollidingEnemies.append(enemy)

    enemies = nonCollidingEnemies
    if gameOver:
        text = font.render("Game Over", True, (255, 0, 0))
        print(type(width/2))
        screen.blit(text, (width/2, height/2))
    else:
        text = font.render("Score: " + str(score), True, (0, 128, 0))
        screen.blit(text, (0, 0))

    pygame.display.flip()
while 1:

    # wait for a few seconds while displaying game over
    sys.exit()
    continue