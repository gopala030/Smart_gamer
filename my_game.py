import pygame
import random
from pynput.keyboard import Key, Controller
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
        self.vel = 20#hit-box remaining
        self.health = 10

    def draw(self, win):
        win.blit(ss, (self.x, self.y))
        pygame.draw.rect(win, (255,0,0), (695, 45, 80, 10))
        pygame.draw.rect(win, (0,128,0), (695, 45, 80 - (8 * (10 - self.health)), 10))                    

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
        self.radius = round(30*level ** 0.45)
        self.color = (255, 255*level // 2, 0)
        self.vel = round(9/ level**0.25)

    def update(self, level):
        self.radius = round(30*level ** 0.45)
        self.color = (255, 255*level // 2, 0)
        self.vel = round(11/ level**0.8)


    def draw(self, win):
        pygame.draw.circle(win, self.color, (self.x, self.y), self.radius)
        pygame.display.update()


def redrawGameWindow():
    win.blit(bg, (0, 0))
    Player_ship.draw(win)
    text = font.render('Score: ' + str(score), 1, (204, 239, 240) )
    win.blit(text, (690, 10))
    for bullet in bullets:
        bullet.draw(win)

    for rock in rocks:
        rock.draw(win)

    pygame.display.update()

   

#main_loop
font = pygame.font.SysFont('comicsans', 30, True)
Player_ship = space_ship(0, 607, 100, 63)
bullets =[]
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

    if rock_loop > 0 :
        rock_loop += 1
    if rock_loop > 40:
        rock_loop = 0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    

    for bullet in bullets:

        for rock in rocks:
            if bullet.x + bullet.radius  > rock.x - rock.radius and bullet.x - bullet.radius < rock.x + rock.radius:
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
            if Player_ship.health > 0 :
                Player_ship.health -= 1
            else :
                run = False

    if rock_loop == 40:
        r_level = random.choice([1,2])
        rocks.append(obstacle(r_level))
        rock_loop = 1

    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_SPACE] and shoot_loop == 0:
        if len(bullets) < 7:
            bullets.append(projectile(round(Player_ship.x + Player_ship.width //2), round(Player_ship.y), 9, (255, 0, 0)))
            shoot_loop = 1

    if keys[pygame.K_LEFT] and Player_ship.x >= Player_ship.vel:
        Player_ship.x -= Player_ship.vel

    if keys[pygame.K_RIGHT] and Player_ship.x <= 800 - Player_ship.width - Player_ship.vel:
        Player_ship.x += Player_ship.vel
    
    redrawGameWindow()

run_1 = True
while run_1 and Player_ship.health == 0 :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run_1 = False

    win.blit(gm, (0, 0))
    pygame.display.update()

pygame.quit()