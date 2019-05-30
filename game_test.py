import pygame
import random
import cv2
import numpy as np
import time
from pynput.keyboard import Key, Controller

keyboard = Controller()

cap = cv2.VideoCapture(0)
time.sleep(5)
left = False
right = False
center = True

pygame.init()

win = pygame.display.set_mode((800, 690))
pygame.display.set_caption("Smart Game")
ss = pygame.image.load('spaceship.png')
bg = pygame.image.load('bg.png')
gm = pygame.image.load('game_over.jpg')

clock = pygame.time.Clock()

score = 0


class space_ship(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel = 20  # hit-box remaining
        self.health = 10

    def draw(self, win):
        win.blit(ss, (self.x, self.y))
        pygame.draw.rect(win, (255, 0, 0), (695, 45, 80, 10))
        pygame.draw.rect(win, (0, 128, 0), (695, 45, 80 - (8 * (10 - self.health)), 10))


class projectile(object):
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel = 20

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)


class obstacle(object):
    def __init__(self, level):
        self.x = random.randint(40, 760)
        self.y = 40
        self.level = level
        self.radius = round(30 * level ** 0.45)
        self.color = (255, 255 * level // 2, 0)
        self.vel = round(9 / level ** 0.2)

    def update(self, level):
        self.radius = round(30 * level ** 0.45)
        self.color = (255, 255 * level // 2, 0)
        self.vel = round(11 / level ** 0.64)

    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
        pygame.display.update()


def redrawGameWindow():
    win.blit(bg, (0, 0))
    Player_ship.draw(win)
    #text = font.render('Score: ' + str(score), 1, (204, 239, 240))
    #win.blit(text, (690, 10))
    for bullet in bullets:
        bullet.draw(win)

    for rock in rocks:
        rock.draw(win)

    pygame.display.update()


# main_loop
font = pygame.font.SysFont('comicsans', 30, True)
Player_ship = space_ship(0, 607, 100, 63)
bullets = []
shoot_loop = 0
rocks = []
rock_loop = 1

run = True

while run:
    clock.tick(27)

    if shoot_loop > 0:
        shoot_loop += 1
    if shoot_loop > 3:
        shoot_loop = 0

    if rock_loop > 0:
        rock_loop += 1
    if rock_loop > 60:
        rock_loop = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    for bullet in bullets:

        for rock in rocks:
            if bullet.x + bullet.radius > rock.x - rock.radius and bullet.x - bullet.radius < rock.x + rock.radius:
                if bullet.y + bullet.radius < rock.y + rock.radius:
                    rock.level -= 1
                    score += 1
                    bullets.pop(bullets.index(bullet))
                    if rock.level:
                        rock.update(1)
                    else:
                        rocks.pop(rocks.index(rock))

        if bullet.y + bullet.radius > 0:
            bullet.y -= bullet.vel
        else:
            bullets.pop(bullets.index(bullet))

    for rock in rocks:
        if rock.y + rock.radius < 607:
            rock.y += rock.vel
        else:
            rocks.pop(rocks.index(rock))
            if Player_ship.health > 0:
                Player_ship.health -= 1
            else:
                run = False

    if rock_loop == 60:
        r_level = random.choice([1, 2])
        rocks.append(obstacle(r_level))
        rock_loop = 1

    ret, img = cap.read()
    img = cv2.flip(img, 1)
    height, width, _ = img.shape
    blur = cv2.blur(img, (3, 3))
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    lower = np.array([100, 100, 50])
    upper = np.array([119, 255, 200])
    mask = cv2.inRange(hsv, lower, upper)

    kernel_square = np.ones((11, 11), np.uint8)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    # Perform morphological transformations to filter out the background noise
    # Dilation increase skin color area
    # Erosion increase skin color area
    dilation = cv2.dilate(mask, kernel_ellipse, iterations=1)
    erosion = cv2.erode(dilation, kernel_square, iterations=1)
    dilation2 = cv2.dilate(erosion, kernel_ellipse, iterations=1)
    filtered = cv2.medianBlur(dilation2, 5)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (8, 8))
    dilation2 = cv2.dilate(filtered, kernel_ellipse, iterations=1)
    kernel_ellipse = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    dilation3 = cv2.dilate(filtered, kernel_ellipse, iterations=1)
    median = cv2.medianBlur(dilation2, 5)
    ret, thresh = cv2.threshold(median, 127, 255, 0)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img, contours, -1, (122, 122, 0), 3)
    new = contours
    max_area = 100
    ci = 0
    if (len(contours) > 0):
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if (area > max_area):
                max_area = area
                ci = i
                # Largest area contour
        cnts = new[ci]
        moments = cv2.moments(cnts)

        # Central mass of first order moments
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])  # cx = M10/M00
            cy = int(moments['m01'] / moments['m00'])  # cy = M01/M00
        centerMass = (cx, cy)
        print(cx, cy)
        cv2.circle(img, centerMass, 7, [100, 0, 255], 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, 'Center', tuple(centerMass), font, 2, (0, 0, 0), 2)
        if (cx < (width / 2) + 60 and center == True):
            if Player_ship.x >= Player_ship.vel:
                left = True
                print('up')
                Player_ship.x -= Player_ship.vel
        if (cx > (width / 2) +60 and cx < (width / 2) + 100 and (left == True or right == True)):
            center = True
            left = False
            right = False

        if (cx > (width / 2) + 100 and center == True):
            if Player_ship.x <= 800 - Player_ship.width - Player_ship.vel:
                #center = False
                right = True
                print("down")
                Player_ship.x += Player_ship.vel

        if cv2.contourArea(cnts) < 2000 and shoot_loop == 0:
            if len(bullets) < 15:
                bullets.append(
                    projectile(round(Player_ship.x + Player_ship.width // 2), round(Player_ship.y), 9, (255, 0, 0)))
                shoot_loop = 1

    cv2.line(img, (int(width / 2) + 60, 0), (int(width / 2) + 60, height), (255, 255, 255), 5)
    cv2.line(img, (int(width / 2) + 100, 0), (int(width / 2) + 100, height), (255, 255, 255), 5)
    cv2.imshow('frame', img)




    redrawGameWindow()

run_1 = True
while run_1 and Player_ship.health == 0:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_1 = False

    win.blit(gm, (0, 0))
    pygame.display.update()

pygame.quit()