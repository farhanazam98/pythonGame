import sys
import pygame
import math
import random
import time
import numpy as np
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
        self.offset = math.pi / 32

    def intersectLines(self, pt1, pt2, ptA, ptB):
        DET_TOLERANCE = 0.00000001
        x1, y1 = pt1
        x2, y2 = pt2
        dx1 = x2 - x1
        dy1 = y2 - y1
        x, y = ptA
        xB, yB = ptB
        dx = xB - x
        dy = yB - y
        DET = (-dx1 * dy + dy1 * dx)
        if math.fabs(DET) < DET_TOLERANCE:
            return False
        DETinv = 1.0/DET
        r = DETinv * (-dy * (x-x1) + dx * (y-y1))
        s = DETinv * (-dy1 * (x-x1) + dx1 * (y-y1))
        xi = (x1 + r*dx1 + x + s*dx)/2.0
        yi = (y1 + r*dy1 + y + s*dy)/2.0
        return True

    def generatePoly(self):
        verts = []
        self.offset += math.pi / 64
        for i in range(0, self.numSides):
            angle = (2.0 * math.pi / self.numSides * i) + self.offset
            x = self.size * cos(angle) + self.position[0]
            y = self.size * sin(angle) + self.position[1]
            verts.append([x, y])
        self.verts = verts
        edges = []
        for vert1 in self.verts:
            for vert2 in self.verts:
                if vert1 != vert2:
                    tup = (vert1, vert2)
                    edges.append(tup)
        self.edges = edges

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
        if dist < self.size + otherPolygonActor.size:
            for edge1 in self.edges:
                for edge2 in otherPolygonActor.edges:
                    return self.intersectLines(edge1[0], edge1[1], edge2[0], edge2[1])


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
        degree = random.randint(3, 8)
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

bg = pygame.image.load("space.bmp")

score = 0

scoreFont = pygame.font.SysFont("arialroundedmtbold", 25)

gameOverFont = pygame.font.SysFont("arialroundedmtbold", 60)

quitFont = pygame.font.SysFont("arialroundedmtbold", 30)

song = AudioSegment.from_wav("chomp.wav")

size = width, height = 512, 512

screen = pygame.display.set_mode(size)

player = PlayerActor([0, 0], [width/2, height/2], 0.9, 4, 8)

enemies = []

isDone = False
gameOver = False
startTime = time.time()
# the lower the spawn rate, the more enemies appear
spawnRate = 50
while isDone == False:
    screen.blit(bg, (0, 0))
    currTime = time.time()
    if currTime > startTime + 2.0:
        spawnRate -= 1
        if spawnRate < 20:
            spawnRate = 20
        startTime = time.time()

    keys = pygame.key.get_pressed()
    for key in keys:
        if keys[pygame.K_q]:
            sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    if random.randint(1, spawnRate) == 1:
        enemies.append(EnemyActor())

#    screen.fill([0, 0, 0])
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
        game_over_text = gameOverFont.render("GAME OVER", True, (255, 0, 0))
        t_width = game_over_text.get_width()
        t_height = game_over_text.get_height()
        screen.blit(game_over_text, (width/2 -
                                     t_width // 2, height/2 - t_height // 2))
        quit_text = quitFont.render("press Q to quit", True, (255, 0, 0))
        q_width = quit_text.get_width()
        q_height = quit_text.get_height()
        screen.blit(quit_text, (width/2 -
                                q_width // 2, height/2 - q_height // 2 + t_height))

    score_text = scoreFont.render("SCORE: " + str(score), True, (255, 255, 0))
    screen.blit(score_text, (0, 0))
    pygame.display.flip()
while 1:

    # wait for a few seconds while displaying game over
    sys.exit()
    continue
