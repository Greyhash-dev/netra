import pygame
import time
import numpy as np
import random
random.seed()

class eventchecker:
    def __init__(self):
        self.keys = [0, 0, 0, 0, 0, 0, 0, 0] #  [LEFT, RIGHT, SPACE, UP, DOWN, D, BACKSPACE, ENTER] -> 0 UP | 1 -> DOWN
        self.running = True

    def check(self, events):
        text_value = ""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.keys[0] = time.time()
                elif event.key == pygame.K_RIGHT:
                    self.keys[1] = time.time()
                elif event.key == pygame.K_SPACE:
                    self.keys[2] = time.time()
                elif event.key == pygame.K_UP:
                    self.keys[3] = time.time()
                elif event.key == pygame.K_DOWN:   
                    self.keys[4] = time.time()
                elif event.key == pygame.K_d:
                    self.keys[5] = time.time()
                elif event.key == pygame.K_BACKSPACE:
                    self.keys[6] = time.time()
                elif event.key == pygame.K_RETURN:
                    self.keys[7] = time.time()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.keys[0] = 0
                elif event.key == pygame.K_RIGHT:
                    self.keys[1] = 0
                elif event.key == pygame.K_SPACE:                                                
                    self.keys[2] = 0
                elif event.key == pygame.K_UP: 
                    self.keys[3] = 0
                elif event.key == pygame.K_DOWN:
                    self.keys[4] = 0
                elif event.key == pygame.K_d: 
                    self.keys[5] = 0
                elif event.key == pygame.K_BACKSPACE:
                    self.keys[6] = 0
                elif event.key == pygame.K_RETURN:
                    self.keys[7] = 0
            if event.type == pygame.TEXTINPUT:
                text_value += event.text
        return self.running, self.keys, text_value

def deg2rad(deg):
    return (deg / 360)*2*np.pi

class bulletmanager:
    def __init__(self, velocity, V):
        self.velocity = velocity
        self.V = V
        self.bullets = []

    def spawn(self, position, angle, start_distance=0):
        self.bullets.append([list(position), deg2rad(angle), start_distance])
        if start_distance != 0:
            self.bullets[-1][0][1] -= np.cos(deg2rad(angle)) * start_distance
            self.bullets[-1][0][0] -= np.sin(deg2rad(angle)) * start_distance

    def update(self, fps):
        step = self.V/(fps*self.velocity+0.1)
        for bullet in self.bullets:
            bullet[0][1] -= np.cos(bullet[1]) * step
            bullet[0][0] -= np.sin(bullet[1]) * step
            if bullet[0][1] < 0:
                self.bullets.remove(bullet)
        return self.bullets


class hitbox:
    def __init__(self, pos, size, h_type, obj_ref=None):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]
        self.h_type = h_type
        self.ref = obj_ref

    def draw(self, scr):
        pygame.draw.rect(scr, (255, 0, 0), [self.x, self.y, self.w, self.h], 3)


class bkg:
    def __init__(self, num, res, speed):
        self.x = []
        self.y = []
        self.size = []
        self.speed = res[0] / speed
        self.res = res
        for i in range(0, num):
            self.y.append(random.randint(0, res[0]))
            self.x.append(random.randint(0, res[1]))
            self.size.append(5 if random.randint(0, 5) == 5 else 3)

    def draw(self, scr):
        for i in range(0, len(self.x)):
            pygame.draw.rect(scr, (150, 150, 150), [self.x[i], self.y[i], self.size[i], self.size[i]])

    def step(self, fps):
        for i in range(0, len(self.y)):
            self.y[i] += self.speed / (fps+0.1)
            if self.y[i] > self.res[0]:
                self.y[i] = self.y[i] - self.res[0]
                self.x[i] = random.randint(0, self.res[1])


class word:
    def __init__(self, spawn_pos, img, font, wortart):
        self.spawn_pos = spawn_pos
        self.pos = list(spawn_pos)
        self.img = img
        self.size = self.img.get_size()
        self.wortart = wortart

    def blit(self, scr):
        scr.blit(self.img, self.pos)

class word_manager:
    def __init__(self, speed, font, res, wortarten):
        self.words = []
        self.speed = res[1] / speed
        self.font = font
        self.res = res
        self.wortarten = wortarten
        self.types = [a for a in wortarten.keys()]
        self.last_type = 0

    def blit(self, scr):
        for word in self.words:
            word.blit(scr)

    def spawn(self):
        try:
            words = self.wortarten[self.types[self.last_type + 1]]
            wortart = self.types[self.last_type + 1]
        except IndexError:
            self.last_type = 0
            wortart = self.types[0]
            words = self.wortarten[self.types[0]]
        word_now = words[random.randint(0, len(words)-1)]
        img = self.font.render(word_now.upper(), True, (255, 255, 255))
        self.words.append(word((random.randint(0, int(self.res[0])-img.get_size()[0]), -img.get_size()[1]), img, self.font, wortart))
        self.last_type += 1

    def step(self, fps):
        for word in self.words:
            word.pos[1] += self.speed / (fps+0.1)
            if word.pos[1] > self.res[1]:
                self.words.remove(word)

    def add_hitboxes(self, hb):
        for word in self.words:
            hb.append(hitbox(word.pos, word.size, 2, word))


class TitleScreenText:
    def __init__(self, font, text, pos, animation_speed, amp):
        self.font = font
        self.text = text
        self.pos = pos
        self.animation_speed = animation_speed
        self.cnt = 0
        self.amp = amp
        self.interpol = [[255, 0, 128], [163, 73, 164], [0, 0, 255]]

    def blit(self, scr, fps):
        width = self.pos[0]
        cnt = 0
        total = len(self.text)
        for char in self.text:
            off = np.sin(((cnt+self.cnt)/total)*np.pi*2)
            rn_f = (off+1) / (2 / (len(self.interpol)-1))
            per = 1-np.abs(rn_f - round(rn_f))*2
            rgb = tuple(np.array(self.interpol[round(rn_f)])*per + 
                        np.array(self.interpol[round(rn_f+0.5)])*(1-per))
            char = self.font.render(char, True, rgb)
            scr.blit(char, (width, self.pos[1] + off*self.amp))
            width += char.get_size()[0]
            cnt += 1
        self.cnt += self.animation_speed / (fps+0.1)


class Scoreboard:
    def __init__(self, font, players, positioning, scr_size):
        self.font = font
        self.players = players
        self.scr_size = scr_size
        self.dummy_players = []
        self.rendered = []
        self.i = 0
        self.p = [scr_size[0] * positioning[0], scr_size[1] * positioning[1], scr_size[0] * positioning[2]]
        if len(players) != 9:
            for _ in range(0, 9-len(players)):
                self.dummy_players.append({"name":".........", "points":0})
        self.render()
    
    def render(self):
        cnt = 0
        self.rendered = []
        for player in self.players+self.dummy_players:
            cnt += 1
            name = self.font.render(str(cnt)+ ". " + player["name"], True, (255, 50, 50))
            points = self.font.render(str(player["points"]), True, (255, 50, 50))
            self.rendered.append([name, points])
            if cnt == 9:
                break

    def blit(self, scr):
        height = self.rendered[0][0].get_size()[1]
        cnt = 0
        for obj in self.rendered:
            scr.blit(obj[0], (self.p[0], self.p[1]+height*cnt))
            scr.blit(obj[1], (self.p[2] - obj[1].get_size()[0], self.p[1]+height*cnt))
            cnt += 1

    def won(self, number):
        i = 0
        for player in self.players:
            if number >= player["points"]:
                break
            i += 1
        if i < 10:
            self.players = self.players[0:i] + [{"name":"Neu", "points":number}] + self.players[i:]
            self.render()
            self.i = i
            return 1
        else:
            return 0

    def text_enter(self, cur_txt):
        self.players[self.i]["name"] = cur_txt
        self.render()


class pointmgr:
    def __init__(self, point_font, ani_font, pos):
        self.points = 0
        self.font = point_font
        self.ani_font = ani_font
        self.pos = pos
        self.ani = []

    def apply(self, amount):
        if amount > 0:
            self.ani.append([0, self.ani_font.render("+ "+str(amount), True, (0, 255, 0)), amount])
        else:
            self.ani.append([0, self.ani_font.render("- "+str(np.abs(amount)), True, (255, 0, 0)), amount])


    def blit(self, scr, fps):
        point_img = self.font.render(str(int(self.points)), True, (255, 255, 0))
        scr.blit(point_img, (self.pos[0] - (point_img.get_size()[0]/2), self.pos[1] - (point_img.get_size()[1]/2)))
        for a in self.ani:
            scr.blit(a[1], (self.pos[0] - (a[1].get_size()[0]/2), a[0]))
            a[0] += 0.4 * (60/(fps+0.1))
            if a[0] > self.pos[1] - point_img.get_size()[1]:
                self.ani.remove(a)
                self.points += a[2]


class timemgr:
    def __init__(self, playtime_sec, pos, font):
        self.start_time = 0
        self.playtime_sec = playtime_sec
        self.pos = pos
        self.font = font

    def start(self):
        self.start_time = time.time()

    def update(self, scr):
        cur = time.time() - self.start_time
        if cur < self.playtime_sec:
            left = self.playtime_sec - cur
            left_per = left / self.playtime_sec
            m = int(left/60)
            s = int(left-(m*60))
            img = self.font.render(str(m)+":"+str(s), True, (255 * (1-left_per), 255 * left_per, 0))
            scr.blit(img, (self.pos[0]-(img.get_size()[0]/2), self.pos[1]-(img.get_size()[1]/2)))
            return 1
        else:
            return 0


class goalmanager:
    def __init__(self, pos, t, wortarten, font, goal_blink_begin, goal_blink_speed, scaletime):
        self.possible = [a for a in wortarten.keys()]
        self.pos = pos
        self.start_time = 0
        self.t = t
        self.now = self.possible[0]
        self.font = font
        self.goal_blink_speed = goal_blink_speed
        self.goal_blink_begin = goal_blink_begin
        self.goal_last_blink = 0
        self.goal_blink_state = 1
        self.last = 0
        self.scaletime = scaletime

    def update(self, scr):
        time_left = self.t - (time.time() - self.start_time)
        if time_left < 0:
            while True:
                self.now = self.possible[random.randint(0, len(self.possible)-1)]
                if self.now != self.last:
                    self.last = self.now
                    break
            self.start_time = time.time()
            time_left = self.t - (time.time() - self.start_time)
        left_per = time_left / self.t
        img = self.font.render(self.now, True, (255 * (1-left_per), 0, 255 * left_per))

        if time_left < self.goal_blink_begin:
            if self.goal_last_blink - time.time() + self.goal_blink_speed < 0:
                self.goal_blink_state = not self.goal_blink_state
                self.goal_last_blink = time.time()
        else:
            self.goal_blink_state = 1
            
        if self.goal_blink_state:
            pos = self.pos.copy()
            if time_left < self.scaletime or self.t - time_left < self.scaletime:
                if time_left < self.scaletime:
                    scale = time_left / self.scaletime
                else:
                    scale = 1/((self.t - time_left) / self.scaletime+0.001)
                    if scale > 10:
                        scale = 0
                    pos[1] = - pos[1] * ((self.t - time_left) / self.scaletime) + pos[1] * (1-(self.t - time_left) / self.scaletime)
                size = [img.get_size()[0] * scale, img.get_size()[1]*scale]
                img = pygame.transform.scale(img, size)
            scr.blit(img, (self.pos[0]-(img.get_size()[0]/2), self.pos[1]-(img.get_size()[1]/2)))
        return self.now


class banner:
    def __init__(self, font, pos, text, color, animation_speed = 0):
        self.font = font
        self.pos = pos
        self.text = text
        self.color = color
        self.last_blink = 0
        self.state = 1
        self.buchstabe = 1
        self.tick_speed = animation_speed / len(text)
        self.animation_speed = animation_speed
        self.img = self.font.render(text, True, color)

    def update(self, scr):
        if self.animation_speed > 0:
            if time.time() - self.last_blink > self.tick_speed:
                self.last_blink = time.time()
                if self.state == 1:
                    self.img = self.font.render(self.text[:self.buchstabe], True, self.color)
                    self.buchstabe += 1
                    if self.buchstabe > len(self.text)+1:
                        self.state = 0
                        self.buchstabe = 0
                else:
                    self.img = self.font.render(self.text*(self.buchstabe%2), True, self.color)
                    self.buchstabe += 1
                    if self.buchstabe == 20:
                        self.state = 1
                        self.buchstabe = 1

        scr.blit(self.img, (self.pos[0]-(self.img.get_size()[0]/2), self.pos[1]-(self.img.get_size()[1]/2)))
