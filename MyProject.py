import pygame
import os
import sys
import random
from os import path

# некоторые константы
maps = ['pr1.txt', 'pr2.txt', 'pr3.txt']
my_map = maps[0]
pygame.init()
total_score = 0
level_num = 0
player = None
GRAVITY = 1
# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
t_box_group = pygame.sprite.Group()
door_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
coins_group = pygame.sprite.Group()
fire_group = pygame.sprite.Group()

size = width, height = 450, 350
# инициализация звуков
pygame.mixer.music.load('data\on_music.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play()
snd_dir = path.join(path.dirname(__file__), 'data')
coin_sound = pygame.mixer.Sound(path.join(snd_dir, 'coin_sound.wav'))
tardis_sound = pygame.mixer.Sound(path.join(snd_dir, 'next_level.wav'))
game_over = pygame.mixer.Sound(path.join(snd_dir, 'go_sound.wav'))

screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
screen.fill(pygame.Color('black'))
running = True
FPS = 10


def terminate(): # выход из временного окна
    pygame.quit()
    sys.exit()


def start_screen(): #  начальное окно
    intro_text = ["Движение по клеточкам",
                  "происходит за счет",
                  "нажатия стрелочек."]

    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def new_level_screen(score, messege): # промежуточное окно между уровнями
    global level_num, maps, total_score, my_map, player, level_x, level_y
    total_score += score
    level_num += 1
    if level_num < len(maps):
        intro_text = [messege,
                      "Ваш счёт:",
                      str(score),
                      "Нажмите <Q>, чтoбы начать игру заново"]
        my_map = maps[level_num]
        player = None
        player, level_x, level_y = generate_level(load_level(my_map))
    else: # если конец
        intro_text = [messege,
                      "Ваш  финальный счёт:",
                      str(total_score),
                      "Нажмите <Q>, чтoбы начать игру заново",
                      "Нажмите <Z>, (и во время игры) чтoбы",
                      "начать уровень заново"]
    fon = pygame.transform.scale(load_image('fon.png'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN: # перезапуск игры
                if event.key == pygame.K_q:
                    for elem in all_sprites:
                        all_sprites.remove(elem)
                    for elem in enemy_group:
                        enemy_group.remove(elem)
                    for elem in player_group:
                        player_group.remove(elem)
                    for elem in star_group:
                        star_group.remove(elem)
                    for elem in door_group:
                        door_group.remove(elem)
                    for elem in t_box_group:
                        t_box_group.remove(elem)
                    for elem in tiles_group:
                        tiles_group.remove(elem)
                    my_map = maps[0]
                    level_num = 0
                    total_score = 0
                    player = None
                    player, level_x, level_y = generate_level(load_level(my_map))
                    create_particles((player.rect.x, player.rect.y))
                    return
                elif event.key == pygame.K_z: # перезапускуровня
                    for elem in all_sprites:
                        all_sprites.remove(elem)
                    for elem in enemy_group:
                        enemy_group.remove(elem)
                    for elem in player_group:
                        player_group.remove(elem)
                    for elem in star_group:
                        star_group.remove(elem)
                    for elem in door_group:
                        door_group.remove(elem)
                    for elem in t_box_group:
                        t_box_group.remove(elem)
                    for elem in tiles_group:
                        tiles_group.remove(elem)
                    level_num -= 1
                    my_map = maps[level_num]
                    total_score -= score
                    player = None
                    player, level_x, level_y = generate_level(load_level(my_map))
                    create_particles((player.rect.x, player.rect.y))
                    return
                else:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def create_particles(position): # создание звезд
    particle_count = 15
    numbers = range(-15, 20)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


def generate_level(level): # генерация уровня из текста
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '$':
                Tile('empty', x, y)
                Coin(x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '/':
                Tile('door', x, y)
            elif level[y][x] == '+':
                Tile('top', x, y)
            elif level[y][x] == '-':
                Tile('border', x, y)
            elif level[y][x] == 'E':
                Tile('empty', x, y)
                Enemy(x, y)
            elif level[y][x] == '%':
                Tile('empty', x, y)
                Fire(x, y)
    return new_player, x, y


def load_image(name, colorkey=None): # загрузка изображения
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

# изображения
tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png'), 'border':  load_image('grass.png'),
               'coin': load_image('coin.png'), 'door': load_image('door.png'), 'top': load_image('top.png')}
player_image = load_image('dino1.png', -1)
enemy_image = load_image('enemy.jpg', -1)
screen_rect = (0, 0, width, height)
tile_width = tile_height = 50


def load_level(filename): # загрузка уровня из карты
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


class Particle(pygame.sprite.Sprite): # класс звездочек
    fire = [load_image("star.png", -1)]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites, star_group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 1

    def update(self): # падение звезд
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Tile(pygame.sprite.Sprite): # создание спрайтов фона
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        if tile_type == 'wall' or tile_type == 'top':
            t_box_group.add(self)
        if tile_type == 'door':
            door_group.add(self)
        if tile_type == 'coin':
            coins_group.add(self)
        if tile_type == 'border':
            t_box_group.add(self)
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Enemy(pygame.sprite.Sprite): # злодей
    def __init__(self, pos_x, pos_y):
        super().__init__(enemy_group, all_sprites)
        self.image = player_image
        self.step = tile_width
        self.score = 0
        self.frames = []
        self.cut_sheet(load_image("enemy.jpg", -1), 6, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 1, tile_height * pos_y + 1)
        self.flag = 1

    def cut_sheet(self, sheet, columns, rows): # создание анимации
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self): # движение злодея
        y = self.rect.y
        self.rect.y += 10
        if pygame.sprite.spritecollideany(self, t_box_group):
            self.rect.y = y
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if pygame.sprite.spritecollideany(self, t_box_group): # если злодей столкнулся с со стенкой, то он бежит обратно
            self.flag = 1 if self.flag == -1 else -1
        self.rect.x += 10 * self.flag
        if pygame.sprite.spritecollideany(self, player_group): # если злодей столкнулся с героем
            game_over.play()
            q = pygame.sprite.spritecollideany(self, player_group)
            q.score = 0
            self.step = 0
            self.score = 0
            screen.fill(pygame.Color('black'))
            for elem in all_sprites:
                all_sprites.remove(elem)
            for elem in enemy_group:
                enemy_group.remove(elem)
            for elem in player_group:
                player_group.remove(elem)
            for elem in star_group:
                star_group.remove(elem)
            for elem in door_group:
                door_group.remove(elem)
            for elem in t_box_group:
                t_box_group.remove(elem)
            for elem in tiles_group:
                tiles_group.remove(elem)
            for elem in coins_group:
                coins_group.remove(elem)
            for elem in fire_group:
                fire_group.remove(elem)
            new_level_screen(self.score, "Вы проиграли!")


class Coin(pygame.sprite.Sprite): # класс монетки
    def __init__(self, pos_x, pos_y):
        super().__init__(coins_group, all_sprites)
        self.image = player_image
        self.step = tile_width
        self.score = 0
        self.frames = []
        self.cut_sheet(load_image("coins.png", -1), 6, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 1, tile_height * pos_y + 1)

    def cut_sheet(self, sheet, columns, rows): # анимация монетки
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if pygame.sprite.spritecollideany(self, player_group): # десйтсвия, если монетку взял герой
            q = pygame.sprite.spritecollideany(self, player_group)
            coins_group.remove(self)
            coin_sound.play()
            self.image = tile_images['empty']
            q.score += 1


class Fire(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(fire_group, all_sprites)
        self.image = player_image
        self.step = tile_width
        self.score = 0
        self.frames = []
        self.cut_sheet(load_image("fire.png", -1), 4, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 2, tile_height * pos_y + 5)

    def cut_sheet(self, sheet, columns, rows): # анимация огня
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if pygame.sprite.spritecollideany(self, player_group): # если герой попадает в огонь, то он умирает
            q = pygame.sprite.spritecollideany(self, player_group)
            game_over.play()
            self.step = 0
            q.score = 0
            screen.fill(pygame.Color('black'))
            for elem in all_sprites:
                all_sprites.remove(elem)
            for elem in enemy_group:
                enemy_group.remove(elem)
            for elem in player_group:
                player_group.remove(elem)
            for elem in star_group:
                star_group.remove(elem)
            for elem in door_group:
                door_group.remove(elem)
            for elem in t_box_group:
                t_box_group.remove(elem)
            for elem in tiles_group:
                tiles_group.remove(elem)
            for elem in coins_group:
                coins_group.remove(elem)
            for elem in fire_group:
                fire_group.remove(elem)
            new_level_screen(self.score, "Вы проиграли!")


class Player(pygame.sprite.Sprite): # герой
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.step = tile_width
        self.score = 0
        self.frames = []
        self.cut_sheet(load_image("dino1.png", -1), 8, 2)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect().move(tile_width * pos_x + 5, tile_height * pos_y + 1)

    def cut_sheet(self, sheet, columns, rows): # анимация героя
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self): # ограничений движений героя
        y = self.rect.y
        self.rect.y += 10
        if pygame.sprite.spritecollideany(self, t_box_group):
            self.rect.y = y
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

    def move(self, arg): # движение героя от стрелок
        x, y = self.rect.x, self.rect.y
        if arg == 1:
            self.rect.x += self.step
        elif arg == 2:
            self.rect.x -= self.step
        elif arg == 3:
            self.rect.y -= self.step
        elif arg == 4:
            self.rect.y += self.step
        if pygame.sprite.spritecollideany(self, t_box_group):
            self.rect.x, self.rect.y = x, y
        if pygame.sprite.spritecollideany(self, coins_group): # сбор монетки
            q = pygame.sprite.spritecollideany(self, coins_group)
            coins_group.remove(q)
            q.image = tile_images['empty']
            coin_sound.play()
            self.score += 1
        if pygame.sprite.spritecollideany(self, enemy_group) or pygame.sprite.spritecollideany(self, enemy_group):
            # столеновение с монеткой и огнем
            self.step = 0
            self.score = 0
            game_over.play()
            screen.fill(pygame.Color('black'))
            for elem in all_sprites:
                all_sprites.remove(elem)
            for elem in enemy_group:
                enemy_group.remove(elem)
            for elem in player_group:
                player_group.remove(elem)
            for elem in star_group:
                star_group.remove(elem)
            for elem in door_group:
                door_group.remove(elem)
            for elem in t_box_group:
                t_box_group.remove(elem)
            for elem in tiles_group:
                tiles_group.remove(elem)
            for elem in coins_group:
                coins_group.remove(elem)
            for elem in fire_group:
                fire_group.remove(elem)
            new_level_screen(self.score, "Вы проиграли!")
        if pygame.sprite.spritecollideany(self, door_group): # столкновение с Тардис
            self.step = 0
            tardis_sound.play()
            screen.fill(pygame.Color('black'))
            for elem in enemy_group:
                enemy_group.remove(elem)
            for elem in all_sprites:
                all_sprites.remove(elem)
            for elem in player_group:
                player_group.remove(elem)
            for elem in star_group:
                star_group.remove(elem)
            for elem in door_group:
                door_group.remove(elem)
            for elem in t_box_group:
                t_box_group.remove(elem)
            for elem in tiles_group:
                tiles_group.remove(elem)
            for elem in coins_group:
                coins_group.remove(elem)
            for elem in fire_group:
                fire_group.remove(elem)
            create_particles((self.rect.x, self.rect.y))
            for elem in player_group:
                player_group.remove(elem)
            new_level_screen(self.score, "Вы прошли уровень!")


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj): #переориентировка
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target): # обновление по предмету
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


player, level_x, level_y = generate_level(load_level(my_map))
camera = Camera()
start_screen()
create_particles((player.rect.x, player.rect.y))
pygame.mouse.set_visible(0)
while running:
    screen.fill(pygame.Color('black'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                player.move(1)
            elif event.key == pygame.K_LEFT:
                player.move(2)
            elif event.key == pygame.K_UP:
                player.move(3)
            elif event.key == pygame.K_DOWN:
                player.move(4)
            elif event.key == pygame.K_z:
                screen.fill(pygame.Color('black'))
                for elem in all_sprites:
                    all_sprites.remove(elem)
                for elem in enemy_group:
                    enemy_group.remove(elem)
                for elem in player_group:
                    player_group.remove(elem)
                for elem in star_group:
                    star_group.remove(elem)
                for elem in door_group:
                    door_group.remove(elem)
                for elem in t_box_group:
                    t_box_group.remove(elem)
                for elem in tiles_group:
                    tiles_group.remove(elem)
                for elem in coins_group:
                    coins_group.remove(elem)
                for elem in fire_group:
                    fire_group.remove(elem)
                player, level_x, level_y = generate_level(load_level(my_map))
    camera.update(player)
    for i, sprite in enumerate(all_sprites):
        camera.apply(sprite)
    all_sprites.draw(screen)
    player_group.update()
    player_group.draw(screen)
    coins_group.update()
    coins_group.draw(screen)
    enemy_group.update()
    enemy_group.draw(screen)
    star_group.update()
    star_group.draw(screen)
    fire_group.update()
    fire_group.draw(screen)
    pygame.display.flip()
    clock.tick(20)
pygame.quit()
