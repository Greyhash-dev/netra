import pygame
import events
import time
import numpy as np
import json

pygame.init()
clock = pygame.time.Clock()

# CONF
title = "NETRA"
set_fps = 120  # FPS
div = 1  # DIV
H = 1920/div  # PIXELS
V = 1080/div  # PIXELS
hor_travel_time = 3  # Travel Time in seconds
ver_travel_time = 6  # Travel Time in seconds
shoot_cooldown = 0.25  # Shoot cooldown in seconds
bullet_travel_time = 0.75  # Vertical Travel time in seconds
speed_attack = 2  # Speed Attack (fps coupled)
vertical_movement_area = [0.5, 0.95]  # Allowed movement area
max_rotation = 20  # Maximum Rotation
ship_size = 0.07  # Width of ship
bkg_scroll_speed = 2
animation_speed = 0.1
num_stars = 400
min_time_word_distance = 0.5
max_word_num = 5
noclip = 0
idle_movement_area = [0.3, 0.7]
title_rel_pos = [0.5, 0.1]
points_rel_pos = [0.95, 0.05]
timer_rel_pos = [0.05, 0.05]
title_animation_speed = 1
title_animation_amp = V*0.03
scoreboard_pos = [0.1, 0.2, 0.9]  # [H, V, H]
goal_pos = [0.5, 0.05]
# SPEC:
# IDs:
#   0 - Ship
#   1 - Bullet
#   2 - Word
# Actions:
# 0 > Not implemented / should not happen
# 1 > Nothing
# 2 > Destroy both colission partners
# 3 > End game

#   0 1 2
# 0 0
# 1 0 0
# 2 3 2 0
run_into_word_punish = -10
hit_correct_word_p = 5
hit_wrong_word_p = -5
playtime_secs = 60
win_blink_delay = 0.25
time_til_new_wortart = 10
goal_blink_begin = 3
goal_blink_speed = 0.1 # [s]
goal_scale_time = 1
banner_pos = [0.5, 0.8]

scr = pygame.display.set_mode((H,V))
pygame.display.set_caption(title)

def load_res(names, scale_factor, mod=1):
    objs = []
    objs_dims = []
    for name in names:
        obj = pygame.image.load("res/"+name)
        obj_dimensions = obj.get_size()
        objs.append(pygame.transform.scale(obj, (H * scale_factor, (obj_dimensions[1] / obj_dimensions[0]) * H * scale_factor * mod)))
        objs_dims.append(objs[-1].get_size())
    if len(objs) == 1:
        return objs[0], objs_dims[0]
    else:
        return objs, objs_dims

def rot_center(image, angle):
    loc = image.get_rect().center  #rot_image is not defined 
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite

if __name__ == "__main__":
    running = True
    evchk = events.eventchecker()
    h_cursor_pos = H/2
    shoot_time = 0
    bmgr = events.bulletmanager(bullet_travel_time, V)

    h_lastdir = 0
    v_cursor_pos = vertical_movement_area[1] * V
    debug = 0
    debug_set = 0
    last_word_spawn = 0
    hitboxen = []
    bkg = events.bkg(num_stars, (int(V), int(H)), bkg_scroll_speed)
    
    ships, ships_dimensions = load_res(["ship_1.png", "ship_2.png", "ship_3.png", "ship_4.png", "ship_5.png"], ship_size)
    ship = ships[0]
    ship_dimensions = ships_dimensions[0]
    background, background_dimensions = load_res(["background.png"], 1, 2)
    bkg_scroll_cur = V - background_dimensions[1]
    animation_counter = 0
    animation_idx = 0
    startup_lag = 1
    debug_font = pygame.font.Font("./fonts/hack.ttf", 30)
    point_font = pygame.font.Font("./fonts/hack.ttf", 40)
    point_font_ani = pygame.font.Font("./fonts/hack.ttf", 20)
    font = pygame.font.Font("./fonts/hack.ttf", 40)
    timer_font = pygame.font.Font("./fonts/hack.ttf", 40)
    goalmanager_font = pygame.font.Font("./fonts/hack.ttf", 40)
    banner_font = pygame.font.Font("./fonts/hack.ttf", 40)
    timer = events.timemgr(playtime_secs, (timer_rel_pos[0]*H, timer_rel_pos[1]*V), timer_font)
    debug_fps = []
    debug_time = []

    
    # TITLE SCREEN VALUES INITIALIZATION
    with open('player_stat.json') as f:
        player_stats = sorted(json.load(f), key=lambda i: i['points'], reverse=True)
    spawn_words = 0
    allow_movement = 0
    auto_move = 0
    auto_move_switched = 0
    title_font = pygame.font.Font("./fonts/title.ttf", 80)
    scoreboard_font = pygame.font.Font("./fonts/menu.ttf", 50)
    tmp = title_font.render(title, True, (255, 255, 255))
    ts = events.TitleScreenText(title_font, title, (H*title_rel_pos[0]-(tmp.get_size()[0]/2), V*title_rel_pos[1]-(tmp.get_size()[1])/2), title_animation_speed, title_animation_amp)

    sb = events.Scoreboard(scoreboard_font, player_stats, scoreboard_pos, (H, V))
    speed_attack_alt = speed_attack


    with open('wortarten.json') as user_file:
        wortarten = json.load(user_file)
    wm = events.word_manager(5, font, (H, V), wortarten)
    gm = events.goalmanager([goal_pos[0] * H, goal_pos[1] * V], time_til_new_wortart, wortarten, goalmanager_font, goal_blink_begin, goal_blink_speed, goal_scale_time)

    pmgr = events.pointmgr(point_font, point_font_ani, (points_rel_pos[0]*H, points_rel_pos[1]*V))

    name_eintragen = 0
    cur_name = ""
    win_blink_cnt = 0
    win_blink_state = 1

    banner = events.banner(banner_font, (banner_pos[0]*H, banner_pos[1]*V), "Drücke Leertaste zum Starten", (150, 150, 150), 10)

    while running:
        now = time.time()
        fps = clock.get_fps()
        if fps == 0 and startup_lag == 1:
            fps = set_fps
        else:
            startup_lag = 0

        running, keys, txtin = evchk.check(pygame.event.get())

        # SHIP ANIMATION
        if animation_counter > animation_speed * fps:
            animation_idx += 1
            if animation_idx == len(ships):
                animation_idx = 0
            animation_counter = 0
        animation_counter += 1
        ship = ships[animation_idx]
        ship_dimensions = ships_dimensions[animation_idx]

        
        # DEBUG SWITCH

        if keys[5]:
            if not debug_set:
                debug = not debug
            debug_set = 1
        else:
            debug_set = 0


        # HORIZONTAL

        if (keys[0] or keys[1]) and allow_movement:
            if keys[0] and keys[1]:
                h_direction = 0
            elif keys[1]:
                h_direction = 1
            elif keys[0]:
                h_direction = -1
        else:
            h_direction = 0

        if not allow_movement:
            speed_attack = 0.75
            if h_cursor_pos > H*idle_movement_area[1]:
                auto_move = 0
            elif h_cursor_pos < H*idle_movement_area[0]:
                auto_move = 1
            if auto_move:
                h_direction = 1
            else:
                h_direction = -1
        else:
            speed_attack = speed_attack_alt

        h_direction = h_lastdir * (1-(speed_attack/(fps+0.1))) + h_direction * (speed_attack/(fps+0.1))
        h_lastdir = h_direction
        h_cursor_pos += (H/(fps*hor_travel_time+0.1)) * h_direction
        if h_cursor_pos < 0:
            h_cursor_pos = 0
        elif h_cursor_pos > H:
            h_cursor_pos = H


        # VERTICAL

        if (keys[3] or keys[4]) and allow_movement:
            if keys[3] and keys[4]:
                v_direction = 0
            elif keys[3]:
                v_direction = -1
            elif keys[4]:
                v_direction = 1
        else:
            v_direction = 0

        v_cursor_pos += (V/(fps*ver_travel_time+0.1)) * v_direction                                                           
        if v_cursor_pos < V * vertical_movement_area[0]:
            v_cursor_pos = V * vertical_movement_area[0]
        elif v_cursor_pos > V * vertical_movement_area[1]:
            v_cursor_pos = V * vertical_movement_area[1]


        # BULLETS

        if keys[2] and (shoot_time - now + shoot_cooldown) < 0 and not name_eintragen:
            if not allow_movement:
                allow_movement = 1
                spawn_words = 1
                pmgr = events.pointmgr(point_font, point_font_ani, (points_rel_pos[0]*H, points_rel_pos[1]*V))
                cur_name = ""

                timer.start()
                shoot_time = now
            else:
                shoot_time = now
                bmgr.spawn((h_cursor_pos, v_cursor_pos), - h_direction*max_rotation, ship_dimensions[1]/2*0.75)
        bullets = bmgr.update(fps)


        # WORDS

        if len(wm.words) != max_word_num and now - last_word_spawn > min_time_word_distance and spawn_words:
            wm.spawn()
            last_word_spawn = now


        # DRAW SCREEN

        scr.fill((0, 0, 0))
        bkg.step(fps)
        bkg.draw(scr)
        wm.step(fps)
        wm.blit(scr)
        wm.add_hitboxes(hitboxen)

        
        ship = pygame.transform.scale(ship, (H * ship_size * (1-np.abs(h_direction**2/5)), (ship_dimensions[1] / ship_dimensions[0]) * H * ship_size))
        rotated = pygame.transform.rotate(ship, - h_direction*max_rotation)
        ship_dimensions = rotated.get_size()
        position = (h_cursor_pos - ship_dimensions[0]/2, int(v_cursor_pos - ship_dimensions[1]/2))
        scr.blit(rotated, position)
        hitboxen.append(events.hitbox(position, ship_dimensions, 0))

        for bullet in bullets:
            r = min([V/150, H/150])
            pygame.draw.circle(scr, (255, 100, 100), bullet[0], r)
            hitboxen.append(events.hitbox((bullet[0][0]-r, bullet[0][1]-r), (r*2, r*2), 1, bullet))

        if not allow_movement:
            ts.blit(scr, fps)
            sb.blit(scr)
            banner.update(scr)
        else:
            cur_wortart = gm.update(scr)
            pmgr.blit(scr, fps)
            time_flag = timer.update(scr)
            if not time_flag:
                allow_movement = 0
                spawn_words = 0
                if sb.won(pmgr.points):
                    name_eintragen = 1
                pmgr.points = 0

        if name_eintragen:
            if len(cur_name) < 10:
                cur_name += txtin
            if txtin:
                sb.text_enter(cur_name)
            if keys[6]:
                cur_name = cur_name[:-1]
                sb.text_enter(cur_name)
                keys[6] = 0
            if keys[7] and cur_name != "":
                name_eintragen = 0
                sb.text_enter(cur_name)
                j = json.dumps(sb.players, indent=2)
                with open("player_stat.json", "w") as f:
                    f.write(j)
            if win_blink_cnt + win_blink_delay < time.time():
                win_blink_cnt = time.time()
                win_blink_state = not win_blink_state
                sb.text_enter(cur_name+"_"*win_blink_state)
        else:
            if win_blink_state == 0:
                win_blink_state = 1
                sb.text_enter(cur_name)



        # CHECK COLLISSION
        for hitbox_a in hitboxen:
            for hitbox_b in hitboxen:
                if 0 < hitbox_b.x - hitbox_a.x < hitbox_a.w:
                    if 0 < hitbox_b.y - hitbox_a.y < hitbox_a.h:
                        bullet_hit_word = 0
                        if hitbox_a.h_type == 0 or hitbox_b.h_type == 0:
                            if hitbox_a.h_type + hitbox_b.h_type != 1:
                                if not noclip:
                                    pmgr.apply(run_into_word_punish)
                                    if hitbox_a.h_type == 2:
                                        wm.words.remove(hitbox_a.ref)
                                        hitboxen.remove(hitbox_a)
                                    elif hitbox_b.h_type == 2:
                                        wm.words.remove(hitbox_b.ref)
                                        hitboxen.remove(hitbox_b)

                        elif hitbox_a.h_type == 2 and hitbox_b.h_type == 1:
                            bullets.remove(hitbox_b.ref)
                            wm.words.remove(hitbox_a.ref)
                            bullet_hit_word = 1
                            if hitbox_a.ref.wortart == cur_wortart:
                                pmgr.apply(hit_correct_word_p)
                            else:
                                pmgr.apply(hit_wrong_word_p)
                        elif hitbox_b.h_type == 2 and hitbox_a.h_type == 1:
                            bullets.remove(hitbox_a.ref)
                            wm.words.remove(hitbox_b.ref)
                            if hitbox_b.ref.wortart == cur_wortart:
                                pmgr.apply(hit_correct_word_p)
                            else:
                                pmgr.apply(hit_wrong_word_p)
                            bullet_hit_word = 1
                        if bullet_hit_word:
                            hitboxen.remove(hitbox_b)
                            hitboxen.remove(hitbox_a)
                            # TODO: Boom animation

        if debug:
            for hitbox in hitboxen:
                hitbox.draw(scr)
                img = debug_font.render(f"FPS: {str(round(fps))} ({set_fps}) {(clock.get_rawtime()/((1/set_fps)*1000))*100}%", True, (255, 0, 0))
            scr.blit(img, (10, 10))
            debug_fps.append(fps)
            debug_time.append(clock.get_rawtime())
            if len(debug_fps) > 200:
                debug_fps.pop(0)
            if len(debug_time) > 200:                                               
                debug_time.pop(0)

            l = [[10, 50], [230, 50], [230, 170], [10, 170]]
            pygame.draw.lines(scr, (255, 0, 0), 1, l)

            
            l = [[20, 100+60]]
            cnt = 0
            for f in debug_fps:
                l.append([20+cnt, 100-(f/set_fps)*100+60])
                cnt += 1
            pygame.draw.lines(scr, (0, 0, 255), 0, l)

            l = [[20, 100+60]]
            cnt = 0
            for f in debug_time:
                l.append([20+cnt, 100-f/((1/set_fps)*1000)*100+60])
                cnt += 1
            pygame.draw.lines(scr, (0, 255, 255), 0, l)
        hitboxen = []

        pygame.display.flip()
        clock.tick(set_fps)
    pygame.quit()

