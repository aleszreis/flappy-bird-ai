from operator import add
import pygame as pg
import os
import random

######## IMAGENS/TELA DO JOGO ########

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800

PIPE_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'pipe.png')))
FLOOR_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'base.png')))
BG_IMG = pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bg.png')))
BIRD_IMGS = [
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird1.png'))),
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird2.png'))),
    pg.transform.scale2x(pg.image.load(os.path.join('imgs', 'bird3.png'))),
]

pg.font.init()
POINTS_FONT = pg.font.SysFont('arial', 50)

######## CLASSES ########

class Bird:
    IMGS = BIRD_IMGS
        # Animações de rotação
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIM_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.height = self.y
        self.time = 0 # Tempo que ele demora para subir e descer
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.velocity = -10.5 # No grid do pygame, o eixo Y sobe pra baixo
        self.time = 0
        self.height = self.y

    def move(self):
    # Calcular o deslocamento
        self.time += 1
        deslocamento = self.velocity * self.time + 1.5 * (self.time**2) # S = S0 + V0t + at²/2


    # Restringir o deslocamento
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0: 
            deslocamento -= 2 # Dá um "boost" pra cima ao pressionar tecla de pular

        self.y += deslocamento

    # Ângulo do pássaro
        if deslocamento < 0 or self.y < (self.height + 50):
            if self.angle < self.MAX_ROTATION:
                self.angle = self.MAX_ROTATION
        else:
            if self.angle > -90:
                self.angle -= self.ROTATION_VELOCITY


    def draw(self, screen):
    # Definir imagem do pássaro a ser usada
        self.img_count += 1

        if self.img_count < self.ANIM_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIM_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIM_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIM_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < (self.ANIM_TIME * 4) + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

    # Se o pássaro tiver caindo, não bater asa
        if self.angle <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIM_TIME * 2

    # Desenhar a imagem
        rotated_img = pg.transform.rotate(self.img, self.angle)
        img_center_position = self.img.get_rect(topleft=(self.x, self.y)).center
        rectangle = rotated_img.get_rect(center=img_center_position)
        screen.blit(rotated_img, rectangle.topleft)

    def get_mask(self):
        return pg.mask.from_surface(self.img) # Mascara o retangulo do pássaro para aprimorar o cálculo da colisão


class Pipe:
    OPENING = 200
    VELOCITY = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top_position = 0
        self.bot_position = 0
        self.TOP_PIPE = pg.transform.flip(PIPE_IMG, False, True)
        self.BOT_PIPE = PIPE_IMG
        self.passed_through = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top_position = self.height - self.TOP_PIPE.get_height()
        self.bot_position = self.height + self.OPENING

    def move(self):
        self.x -= self.VELOCITY

    def draw(self, screen):
        screen.blit(self.TOP_PIPE, (self.x, self.top_position))
        screen.blit(self.BOT_PIPE, (self.x, self.bot_position))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_pipe_mask = pg.mask.from_surface(self.TOP_PIPE)
        bot_pipe_mask = pg.mask.from_surface(self.BOT_PIPE)

        top_distance = (self.x - bird.x, self.top_position - round(bird.y))
        bot_distance = (self.x - bird.x, self.bot_position - round(bird.y))

        collided_top = bird_mask.overlap(top_pipe_mask, top_distance)
        collided_bot = bird_mask.overlap(bot_pipe_mask, bot_distance)

        if collided_top or collided_bot:
            return True
        else:
            return False

class Floor:
    VELOCITY = 5 # Mesma velocidade do cano
    WIDTH = FLOOR_IMG.get_width()
    IMG = FLOOR_IMG

    def __init__(self, y):
        self.y = y
        self.x0 = 0
        self.x1 = self.x0 + self.WIDTH

    def move(self):
        self.x0 -= self.VELOCITY
        self.x1 -= self.VELOCITY

        if self.x0 + self.WIDTH < 0:
            self.x0 = self.x1 + self.WIDTH

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x0 + self.WIDTH

    def draw(self, screen):
        screen.blit(self.IMG, (self.x0, self.y))
        screen.blit(self.IMG, (self.x1, self.y))

######## DESENHA A TELA ########
def draw_screen(screen, birds, pipes, floor, points):
    screen.blit(BG_IMG, (0, 0))
    for bird in birds:
        bird.draw(screen)
    for pipe in pipes:
        pipe.draw(screen)

    text = POINTS_FONT.render(f'Pontuação: {points}', 1, (255, 255, 255))
    screen.blit(text, (SCREEN_WIDTH - 10 - text.get_width(), 10))
    floor.draw(screen)

    pg.display.update()

def main():
    birds = [Bird(230, 350)]
    floor = Floor(730)
    pipes = [Pipe(700)]
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    points = 0
    clock = pg.time.Clock() # "Conta" o tempo dentro do jogo

    on = True
    while on:
        clock.tick(30)

        # Interação com o usuário
        for event in pg.event.get():
            if event.type == pg.QUIT:
                on = False
                pg.quit()
                quit()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    for bird in birds:
                        bird.jump()
        # Move as coisas
        for bird in birds:
            bird.move()
        floor.move()

        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for i, bird in enumerate(birds): # "i" é o index do pássaro dentro da lista
                if pipe.collide(bird):
                    birds.pop(i)
            
                if not pipe.passed_through and bird.x > pipe.x:
                    pipe.passed_through = True
                    add_pipe = True
            
            pipe.move()

            if pipe.x + pipe.TOP_PIPE.get_width() < 0:
                remove_pipes.append(pipe)
            
        if add_pipe:
            points += 1
            pipes.append(Pipe(600))

        for pipe in remove_pipes:
            pipes.remove(pipe)

        for i, bird in enumerate(birds):
            if (bird.y + bird.img.get_height() > floor.y) or bird.y < 0:
                birds.pop(i)

        draw_screen(screen, birds, pipes, floor, points)

if __name__ == '__main__':
    main()