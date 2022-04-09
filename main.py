# Wizardy

import os.path
import time

import pygame
import pygame.freetype
import csv
import random
import os
import json


#global variables needed
Move_screen = [0,0]
mousey = False
hero_x = 0
hero_y = 0
move_back_map = False

# Map Tile is used for all the background sprites including monsters and moves rather than the hero
class Map_Tile(pygame.sprite.Sprite):
    def __init__(self, xypos, type, subtype):
        pygame.sprite.Sprite.__init__(self)
        global hero_x
        global hero_y
        global sound_setting

        #shared attributes (might get changed by Type or sub-type)
        self.interactive = False
        self.obstacle = False
        self.visible = False
        self.secret = False
        self.on_screen = False
        self.found = True
        self.found_counter = 20
        self.found_bounce = 10
        self.fade = 30
        self.subtype = subtype
        self._layer = 1
        self.home_in_on_hero = True
        self.direction = pygame.math.Vector2((1,1)).normalize()
        self.life = 1
        self.found_sound = None
        (self.x, self.y) = xypos

        #specific attributes
        if type == "wall":
            self.obstacle = True
            self.object_type = "wall"
            self.image = pygame.image.load("venv/graphics/stone_wall.png").convert_alpha()
            self.rect = self.image.get_rect()
        elif type == "door":
            self.obstacle = True
            self.object_type = "door"
            self.image = pygame.image.load("venv/graphics/stone_wall1.png").convert_alpha()
            self.rect = self.image.get_rect()
            if subtype == "red":
                self.key_needed = "Red Key"
            elif subtype == "blue":
                # This is the level exit
                self.key_needed = "Blue Key"
                self.images = []
                self.images.append(pygame.image.load("venv/graphics/Closed.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/Open.png").convert_alpha())
                self.image = pygame.image.load("venv/graphics/Closed.png").convert_alpha()
            elif subtype == "green":
                self.key_needed = "Green Key"
            self.locked = True
            self.interactive = True
            self._layer = 2
            self.found_sound = pygame.mixer.Sound("venv/sounds/smash_pot.ogg")
            self.fade = 0
        elif type == "floor":
            self.obstacle = False
            self.object_type = "floor"
            self._layer = 1
            self.image = pygame.image.load("venv/graphics/sand.png").convert_alpha()
            self.rect = self.image.get_rect()
        elif type == "target":
            self.obstacle = False
            self.object_type = "target"
            self.fade = 2
            self.life = 1
            self._layer = 4
            self.interactive = True
            self.visible = True
            self.image = pygame.image.load("venv/graphics/target.png").convert_alpha()
            self.rect = self.image.get_rect()
        elif type == "spell":
            self.object_type = "spell"
            self.life = 1
            self.fade = 30

            scale = (64,64)
            if subtype == "dragon_boss":
                scale = (250, 250)
            self.images = []
            original_image = pygame.image.load("venv/graphics/spell1.png").convert_alpha()
            scaled_image = pygame.transform.scale(original_image, scale)
            self.images.append(scaled_image)
            original_image = pygame.image.load("venv/graphics/spell2.png").convert_alpha()
            scaled_image = pygame.transform.scale(original_image, scale)
            self.images.append(scaled_image)
            original_image = pygame.image.load("venv/graphics/spell3.png").convert_alpha()
            scaled_image = pygame.transform.scale(original_image, scale)
            self.images.append(scaled_image)
            original_image = pygame.image.load("venv/graphics/spell4.png").convert_alpha()
            scaled_image = pygame.transform.scale(original_image, scale)
            self.images.append(scaled_image)
            # add smoke graphics here??


            self.animation_wait = 0
            self._layer = 3
            self.spell_sound = pygame.mixer.Sound("venv/sounds/spell.ogg")
            self.visible = True
            self.image = scaled_image
            self.rect = scaled_image.get_rect()

        elif type == "key":
            if subtype == "red":
                self.image = pygame.image.load("venv/graphics/red_key.png").convert_alpha()
                self.rect = self.image.get_rect()
                self.object_type = "redkey"
            elif subtype == "blue":
                self.image = pygame.image.load("venv/graphics/blue_key.png").convert_alpha()
                self.rect = self.image.get_rect()
                self.object_type = "bluekey"
            elif subtype == "green":
                self.image = pygame.image.load("venv/graphics/green_key.png").convert_alpha()
                self.rect = self.image.get_rect()
                self.object_type = "greenkey"
            self.obstacle = False
            self.interactive = True
            self._layer = 2
            self.found_sound = pygame.mixer.Sound("venv/sounds/find_key.ogg")
            self.fade = 0
        elif type == "pot":
            self.object_type = "pot"
            self.obstacle = False
            self.interactive = True
            self._layer = 2
            self.found_sound = pygame.mixer.Sound("venv/sounds/smash_pot.ogg")
            self.fade = 0
            self.image = pygame.image.load("venv/graphics/pot.png").convert_alpha()
            scale = (random.randint(30,50), random.randint(40,65))
            self.image = pygame.transform.scale(self.image, scale)
            self.rect = self.image.get_rect()

        elif type == "item":
            self.object_type = "item"
            self.obstacle = False
            self.interactive = True
            self.found = False
            self.fade = 5
            self._layer = 2
            if subtype == "gold":
                self.image = pygame.image.load("venv/graphics/gold.png").convert_alpha()
            if subtype == "health":
                self.image = pygame.image.load("venv/graphics/health.png").convert_alpha()
            if subtype == "potion":
                self.image = pygame.image.load("venv/graphics/spell.png").convert_alpha()
            self.found_sound = pygame.mixer.Sound("venv/sounds/pickup_object.ogg")
            self.rect = self.image.get_rect()
        else:

            self.obstacle = False
            self.object_type = "monster"
            self.found_sound= pygame.mixer.Sound("venv/sounds/monster_fall.ogg")
            self.frozen = 0
            # add animation details
            self.fade = 0
            self.images = []
            # death image needed for all monsters
            self.image_death = pygame.image.load("venv/graphics/smoke3.png").convert_alpha()
            scale = (64, 64)
            if subtype == "dragon_boss":
                scale = (250, 250)
            self.image_death = pygame.transform.scale(self.image_death, scale)

            self.animation_wait = 0
            self.current_direction = "right"
            self.can_move = True
            self._layer = 4

            if subtype == "skeleton":
                # set various values, can change to make harder
                self.speed = 2
                self.life = 10
                self.fade = 30
                self.animation_speed = 12
                self.attack = 1
                self.attack_strength = self.attack
                self.full_life = self.life
                self.images.append(pygame.image.load("venv/graphics/skeleton_move_1.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/skeleton_move_2.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/skeleton.png").convert_alpha())
                self.images_right = self.images
                self.images_left = [pygame.transform.flip(image, True, False) for image in
                                    self.images]  # Flipping every image.


                self.image = pygame.image.load("venv/graphics/skeleton.png").convert_alpha()

                self.rect = self.image.get_rect()

            if subtype == "slime":
                # set various values, can change to make harder
                self.speed = 0.25
                self.life = 10
                self.fade = 30
                self.animation_speed = 24
                self.attack = 2
                self.attack_strength = self.attack
                self.full_life = self.life
                self.images.append(pygame.image.load("venv/graphics/SlimeMonster1.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/SlimeMonster2.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/SlimeMonster1.png").convert_alpha())
                self.images_right = self.images
                self.images_left = [pygame.transform.flip(image, True, False) for image in
                                    self.images]  # Flipping every image.
                self.image = pygame.image.load("venv/graphics/SlimeMonster1.png").convert_alpha()
                self.rect = self.image.get_rect()


            if subtype == "zombie":
                # set various values, can change to make harder
                self.speed = 1
                self.life = 5
                self.fade = 30
                self.animation_speed = 6
                self.attack = 1
                self.attack_strength = self.attack
                self.full_life = self.life
                self.images.append(pygame.image.load("venv/graphics/zombie_1.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/zombie_2.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/zombie_1.png").convert_alpha())
                self.images_right = self.images
                self.images_left = [pygame.transform.flip(image, True, False) for image in
                                    self.images]  # Flipping every image.
                self.image = pygame.image.load("venv/graphics/zombie_1.png").convert_alpha()
                self.rect = self.image.get_rect()

            if subtype == "dragon_boss":
                # set various values, can change to make harder
                self.speed = 0
                self.life = 20
                self.fade = 30
                self.animation_speed = 6
                self.attack = 5
                self.attack_strength = self.attack
                self.full_life = self.life
                self._layer = 4
                self.images.append(pygame.image.load("venv/graphics/Dragon_boss.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/Dragon_boss_2.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/Dragon_boss.png").convert_alpha())
                self.images_right = self.images
                self.images_left = [pygame.transform.flip(image, True, False) for image in
                                    self.images]  # Flipping every image.
                self.image = pygame.image.load("venv/graphics/Dragon_boss.png").convert_alpha()
                self.rect = self.image.get_rect()


            if subtype == "fireball":
                # set various values, can change to make harder
                self.speed = 8
                self.life = 5
                self.fade = 1
                self.animation_speed = 5
                self.attack = 5
                self.attack_strength = self.attack
                self.full_life = self.life
                self.images.append(pygame.image.load("venv/graphics/fire_1.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/fire_2.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/fire_1.png").convert_alpha())
                self.images_right = self.images
                self.images_left = [pygame.transform.flip(image, True, False) for image in
                                    self.images]  # Flipping every image.
                self.image = pygame.image.load("venv/graphics/fire_1.png").convert_alpha()
                self.rect = self.image.get_rect()
                # Will not change as fired from level boss
                self.home_in_on_hero = False
                # target is where the hero is now and does not change
                # needed to add a random factor otherwise too easy
                self.prey_vector = (hero_x - self.x + (random.randint(-100, 100)), hero_y - self.y + random.randint(-100, 100))
                self.visible = True

            if subtype == "blob":
                # set various values, can change to make harder
                self.speed = 5
                self.life = 5
                self.fade = 1
                self.animation_speed = 5
                self.attack = 5
                self.attack_strength = self.attack
                self.full_life = self.life
                self.images.append(pygame.image.load("venv/graphics/blob.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/blob.png").convert_alpha())
                self.images.append(pygame.image.load("venv/graphics/blob.png").convert_alpha())
                self.images_right = self.images
                self.images_left = [pygame.transform.flip(image, True, False) for image in
                                    self.images]  # Flipping every image.
                self.image = pygame.image.load("venv/graphics/blob.png").convert_alpha()
                self.rect = self.image.get_rect()
                # Will not change as fired from level boss
                self.home_in_on_hero = False
                # target is where the hero is now and does not change
                # needed to add a random factor otherwise too easy
                self.prey_vector = (hero_x - self.x + (random.randint(-100, 100)), hero_y - self.y + random.randint(-100, 100))
                self.visible = True



        self.pos_last_x = self.x
        self.pos_last_y = self.y
        self.pos_before_last_x = self.pos_last_y
        self.pos_before_last_y = self.pos_last_y
        self.contact_obstacle = False
        self.monster_movement = [[0, 0], [0, 0]]


    def checkEvents(self):
        # General update for all object types to ensure all move together on the background
        global Move_screen
        global move_back_map

        #keep a note of where you were last time
        self.pos_before_last_x = self.pos_last_x
        self.pos_before_last_y = self.pos_last_y
        self.pos_last_x = self.x
        self.pos_last_y = self.y
        if move_back_map == False:
            # Move everything based on hero details
            self.x = self.x - Move_screen[0]
            self.y = self.y - Move_screen[1]
        #otherwise move it back to where it was
        else:
            self.x = self.pos_before_last_x
            self.y = self.pos_before_last_y

    def monster_move(self):
        # This is only called if the monster is not touching an obstacle and can move
        # bounce back means it will get called to start moving when able
        global hero_x
        global hero_y
        global Move_screen

        #Work out where the hero is and move towards him
        # Work out target vector based on current hero location
        # for homing in monsters
        if self.home_in_on_hero == True:
            self.prey_vector = (hero_x - self.x, hero_y - self.y)
        if self.prey_vector != (0,0) and self.on_screen == True:
            self.direction = pygame.math.Vector2(self.prey_vector).normalize()

        self.monster_movement = self.direction * self.speed
        self.x = self.x + self.monster_movement[0]
        self.y = self.y + self.monster_movement[1]

        # Work out animation based on direction
        if self.prey_vector[0] >= 0 and self.animation_wait == 0:
            self.image = self.images_right[0]
            self.current_direction = "right"
        elif self.prey_vector[0]< 0 and self.animation_wait == 0:
            self.image = self.images_left[0]
            self.current_direction = "left"

        #counter for animation
        self.animation_wait = self.animation_wait + 1

        if self.current_direction == "right":
            if self.animation_wait == self.animation_speed:
                self.image = self.images_right[1]
            if self.animation_wait == self.animation_speed * 2:
                self.image = self.images_right[2]
            if self.animation_wait == self.animation_speed * 3:
                self.animation_wait = 0
        else:
            if self.animation_wait == self.animation_speed:
                self.image = self.images_left[1]
            if self.animation_wait == self.animation_speed * 2:
                self.image = self.images_left[2]
            if self.animation_wait == self.animation_speed * 3:
                self.animation_wait = 0



    def fade_countdown(self):
        global sound_setting
        self.fade = self.fade - 1
        if self.fade <= 0:
                if sound_setting == "on" and self.found_sound is not None:
                    self.found_sound.play()
                self.kill()

    def found_item(self):
        self.found_counter = self.found_counter - 1
        if self.found_bounce <= self.found_counter:
            self.y = self.y - 10
        elif self.found_bounce > self.found_counter and self.found_counter >= 0:
            self.y= self.y + 10
        if self.found_counter <= 0:
            self.fade_countdown()



    def update(self):
        #only need to include object types that interact or move in this def
        global screen
        global sound_setting
        global music_setting
        #only move a monster if it is not hitting an obstacle or been attacked and is visible
        if self.object_type == "monster" and self.contact_obstacle == False and self.on_screen == True:
            if self.can_move == True:
                self.monster_move()
        elif self.object_type == "monster" and self.contact_obstacle == True:
            # This is bounce back to move monster back
            self.x = self.x - self.monster_movement[0]
            self.y = self.y - self.monster_movement[1]
            self.contact_obstacle = False
            #destroy fireball if it hits something
            if self.subtype == "fireball" or self.subtype == "blob":
                self.life = 0
        #spell have stay on the screen for a while so fade does this
        #duplication if there life = 0 this will happen anyway?
        if self.object_type == "spell" or self.object_type == "target":
            self.fade_countdown()

        #If a monster has been frozen also using fade countdown
        #freeze all monsters for the same amount of time
        if self.object_type == "monster" and self.can_move == False:
            self.frozen = self.frozen + 1
            self.attack_strength = 0
            if self.frozen >= 30:
                self.can_move = True
                self.attack_strength = self.attack
                self.frozen = 0
            if self.life <= 0:
                self.image = self.image_death

        #animation of spell
        if self.object_type == "spell":
            self.animation_wait = self.animation_wait + 1
            change = 8
            if self.animation_wait == change:
                self.image = self.images[0]
            if self.animation_wait == change * 2:
                self.image = self.images[1]
            if self.animation_wait == change * 3:
                self.image = self.images[2]
            if self.animation_wait == change * 4:
                self.image = self.images[3]
            if self.animation_wait == change * 5:
                self.animation_wait = 0


        if self.object_type == "item" and self.found == True:
            self.found_item()

        if self.life <= 0:
            self.fade_countdown()

        self.checkEvents()
        self.rect.centerx = self.x
        self.rect.centery = self.y



# Hero is wizardy in this game
class Hero(pygame.sprite.Sprite):

    def __init__(self, xypos):
        """ Creates in xypos position
        """
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("venv/graphics/wizard.png").convert_alpha()
        self.rect = self.image.get_rect()
        (self.x, self.y) = xypos
        self.target_location = (self.x, self.y)
        self.target_location_list = list(self.target_location)
        self.run_speed = 10
        self.direction_travel = [0, 0]
        self.hero_vector = (0.0, 0.0)
        self.last_x = self.x
        self.last_y = self.y
        self.contact_obstacle = False
        self.potion = 100
        self.life = 100
        self.gold = 0
        self.potion_cost = 20
        self.carrying = []
        self.carry_gold = 0
        self.carry_health = 0
        self.carry_potion = 0
        # add animation details
        self.images = []
        self.images.append(pygame.image.load("venv/graphics/wizard_step1.png").convert_alpha())
        self.images.append(pygame.image.load("venv/graphics/wizard_step2.png").convert_alpha())
        self.images.append(pygame.image.load("venv/graphics/wizard.png").convert_alpha())
        self.images_right = self.images
        self.images_left = [pygame.transform.flip(image, True, False) for image in self.images]  # Flipping every image.
        self.animation_wait = 0
        self.current_direction = "right"



    def checkEvents(self):
        global Move_screen
        global mousey
        global background

        # check to ensure that hero is always centre screen regardless
        centre_of_screen = background[0] - (background[0] / 2), background[1] - (background[1] / 2)
        (self.x, self.y) = centre_of_screen

        #If obstacle then stop
        if self.contact_obstacle == True:
            self.stop()


        # change to list as it needs to be mutable (we'll need to change it)
        self.target_location_list = list(self.target_location)
        # Work out target vector based on current hero location
        self.hero_vector = (self.target_location[0] - self.x, self.target_location[1] - self.y)

        # work out direction of travel using Vector2 (2 is for 2D) and normalise takes out any scale
        # scale will be added later using the hero's 'run_speed'
        if self.hero_vector != (0,0):
            self.direction_travel = pygame.math.Vector2(self.hero_vector).normalize()
            #print("direction of travel is", self.direction_travel)
            Move_screen = self.direction_travel * self.run_speed
            # change animation depending of direction
            if self.hero_vector[0] >= 0:
                self.image = self.images_right[0]
                self.animation_wait = self.animation_wait + 1
                self.current_direction = "right"
                if self.animation_wait >= 4:
                    self.image = self.images_right[1]
                    self.animation_wait = 0
            if self.hero_vector[0] < 0:
                self.image = self.images_left[0]
                self.animation_wait = self.animation_wait + 1
                self.current_direction = "left"
                if self.animation_wait >= 4:
                    self.image = self.images_left[1]
                    self.animation_wait = 0
        # Otherwise wizard is standing still
        else:
            if self.current_direction == "right":
                self.image = self.images_right[2]
            else:
                self.image = self.images_left[2]


    def stop(self):
        self.contact_obstacle = False
        Move_screen[0] = 0
        Move_screen[1] = 0
        self.target_location_list[0] = self.x
        self.target_location_list[1] = self.y
        self.direction_travel = [0, 0]
        self.hero_vector = (0.0, 0.0)
        self.target_location = (self.x, self.y)



    def update(self,):
        global hero_x, hero_y
        self.checkEvents()

        self.rect.centerx = self.x
        self.rect.centery = self.y
        hero_x = self.x
        hero_y = self.y

class Button:
    def __init__(self, screen, position_x, position_y, text, size, colour, level, button_width, button_height):
        self.position_x = position_x
        self.position_y = position_y
        self.text = text
        self.size = size
        self.colour = colour
        self.button_width = button_width
        self.button_height = button_height
        self.active = False
        self.next_screen = 0
        self.level = level
        my_ft_font = pygame.freetype.SysFont('Courier', size)
        text_position_x = position_x + (self.button_width / 2) - (my_ft_font.get_rect(text, size=size)[2]) / 2
        text_position_y = position_y + (self.button_height / 2) - (my_ft_font.get_rect(text, size=size)[3]) / 2
        print(position_x, (self.button_width / 2), (len(text) * size) / 2)

        text_length = my_ft_font.get_rect(text, size=size)
        #print("Test_Length", text_length)
        pygame.draw.rect(screen, self.colour, (position_x, position_y, self.button_width, self.button_height))
        my_ft_font.render_to(screen, (text_position_x, text_position_y), text, (0,0,0))

        if self.text == "More":
            self.next_screen = level
        if self.text == "Reset":
            self.next_screen = 1

    def button_activated(self, screen):
        print("HIT", self.text)
        print(self.position_x, self.position_y, self.button_width, self.button_height)
        if self.active == False:
            # Returns to original colour
            button_colour = self.colour
        else:
            #Red when activated
            button_colour = (255,0,0)
        pygame.draw.rect(screen, button_colour, (self.position_x, self.position_y, self.button_width, self.button_height))
        my_ft_font = pygame.freetype.SysFont('Courier', self.size)
        text_position_x = self.position_x + (self.button_width / 2) - (
            my_ft_font.get_rect(self.text, size=self.size)[2]) / 2
        text_position_y = self.position_y + (self.button_height / 2) - (
            my_ft_font.get_rect(self.text, size=self.size)[3]) / 2
        text_length = my_ft_font.get_rect(self.text, size=self.size)
        # print("Test_Length", text_length)
        my_ft_font.render_to(screen, (text_position_x, text_position_y), self.text, (0, 0, 0))
    #def checkEvents(self):
    #    if self.active == True:

class Game():
    def __init__(self):
        # Set up player details
        self.account_playing = os.environ.get('USERNAME')
        print(self.account_playing)
        self.game_file = "venv/players/" + self.account_playing + ".json"

        # If there is no file for a person they get Level 1 and no gold
        player_data_start = '{ "level":1, "gold":0, "screen":"resize", "screen_height":640, "screen_width":1024, "sound":"on", "music":"on"}'

        self.no_potion = pygame.mixer.Sound("venv/sounds/empty.ogg")
        self.you_died_sound = pygame.mixer.Sound("venv/sounds/Hero_died.ogg")

        #Check to see if they have a game file
        if not os.path.isfile(self.game_file):
            self.player_data = json.loads(player_data_start)
            with open(self.game_file, 'w') as file:
                json.dump(self.player_data, file,  indent=4)
        #Load this if there is one
        else:
            self.player_data = json.load(open(self.game_file, 'r'))

        self.screen_setting = (self.player_data["screen_width"] ,self.player_data["screen_height"])

        if self.player_data["screen"] == "full":
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:            
            self.screen = pygame.display.set_mode(self.screen_setting, pygame.RESIZABLE)

        global sound_setting
        sound_setting = str(self.player_data["sound"])
        global music_setting
        music_setting = str(self.player_data["music"])
        if music_setting == "on":
            pygame.mixer.music.load("venv/music/Mining Town (Loop).wav")
            pygame.mixer.music.set_volume(0.50)
            pygame.mixer.music.play(-1, 0.0)

    def level(self, name):
        #Level is the main game
        global mousey
        global hero_x, hero_y
        global background
        global Move_screen
        global move_back_map
        global sound_setting
        global music_setting
        my_ft_font = pygame.freetype.SysFont('Courier', 12)
        shift_pressed = False
        screen_changed = True
        show_map =  False
        z_wait = False
        x_wait = False
        self.gold = 0
        self.select_sound = pygame.mixer.Sound("venv/sounds/replenish.ogg")
        self.name = name


        #screen = pygame.display.set_mode(self.screen_setting, pygame.RESIZABLE)
        background = self.screen.get_size()
        print("background", background, "screen", self.screen)



        # Add background tiles
        #self.map_tile_Sprite = pygame.sprite.LayeredUpdates()
        self.map_tile_Sprite = pygame.sprite.Group()

        # loop through the csv files provided as the map template
        level_being_played = 'venv/maps/'+ name + '.csv'
        print("level being played", level_being_played)
        with open(level_being_played, 'r') as map_info:
            map_data = csv.reader(map_info, delimiter=',')
            y1 = 0
            for row in map_data:
                #print(row)
                x1 = 0
                for field in row:
                    # add the height of the tile spri
                    coords = (x1, y1)
                    if field == '1':
                        tile_image = "wall"
                        subtype_local = ""
                    elif field == '0':
                        tile_image = "floor"
                        subtype_local = ""
                    elif field == '2':
                        tile_image = "monster"
                        subtype_local = "skeleton"
                    elif field == 'z':
                        tile_image = "monster"
                        subtype_local = "zombie"
                    elif field == 'd':
                        tile_image = "monster"
                        subtype_local = "dragon_boss"
                    elif field == 's':
                        tile_image = "monster"
                        subtype_local = "slime"
                    elif field == 'r':
                        tile_image = "door"
                        subtype_local = "red"
                    elif field == 'R':
                        tile_image = "key"
                        subtype_local = "red"
                    elif field == 'g':
                        tile_image = "door"
                        subtype_local = "green"
                    elif field == 'G':
                        tile_image = "key"
                        subtype_local = "green"
                    elif field == 'b':
                        tile_image = "door"
                        subtype_local = "blue"
                    elif field == 'B':
                        tile_image = "key"
                        subtype_local = "blue"
                    elif field == 'P':
                        tile_image = "pot"
                        subtype_local = "up"
                    elif field == 'p':
                        tile_image = "pot"
                        subtype_local = ""
                    elif field == 'W':
                        #This is the hero
                        start_x = x1
                        start_y = y1
                        tile_image = "skip"
                    else:
                        tile_image = "skip"
                        subtype_local = ""
                    # as long as not skip create a sprite
                    if tile_image != "skip":
                        block = Map_Tile(coords, tile_image, subtype_local)
                        self.map_tile_Sprite.add(block)
                        # If it is a pot add 2 more near
                        if tile_image == "pot":
                            #spread either left to right or up and down
                            if subtype_local == "up":
                                r1 = -5
                                r2 = 5
                                r3 = -100
                                r4 = 100
                            else:
                                r1 = -100
                                r2 = 100
                                r3 = -5
                                r4 = 5
                            coord_off = [x1 + random.randint(r1,r2), y1 + random.randint(r3,r4)]
                            block = Map_Tile(coord_off, tile_image, subtype_local)
                            self.map_tile_Sprite.add(block)
                            coord_off = [x1 + random.randint(r1,r2), y1 + random.randint(r3,r4)]
                            block = Map_Tile(coord_off, tile_image, subtype_local)
                            self.map_tile_Sprite.add(block)
                    # Need floor behind any item (may need to change when more than one floor type)
                    if tile_image != "floor" and tile_image != "wall" and tile_image != "skip" or field == "W":
                        #This is an object so need a floor tile as well
                        block = Map_Tile(coords, "floor", "")
                        self.map_tile_Sprite.add(block)


                    x1 = x1 + 64
                # add the width of the tiles sprite
                y1 = y1 + 64


        obstacles_on_screen = pygame.sprite.Group()
        on_screen = pygame.sprite.LayeredUpdates()
        monsters = pygame.sprite.Group()
        interactive_monsters = pygame.sprite.Group()
        target = pygame.sprite.Group()
        spell = pygame.sprite.Group()
        interactive_tiles = pygame.sprite.Group()
        self.visible = pygame.sprite.Group()

        xdiff = background[0] / 2
        ydiff = background[1] / 2
        # Add hero, seems easier to add as group (might need to change that later)
        self.hero_Sprite = pygame.sprite.Group()
        hero = Hero([xdiff, ydiff])
        self.hero_Sprite = pygame.sprite.Group(hero)
        print("Hero Sprite ", xdiff, ydiff)

        #need to move all tiles relative to where the wizard starts on the map
        #background = self.screen.get_size()
        for t in self.map_tile_Sprite:
            t.x = t.x - start_x + xdiff
            t.y = t.y - start_y + ydiff
        self.map_tile_Sprite.update()

        # Run until the user asks to quit
        running = True

        clock = pygame.time.Clock()

        #update sprites before first loop
        self.hero_Sprite.update()
        self.map_tile_Sprite.update()

        #Main loop
        while running:
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # when mousey is true the wizard vector is set to the mouse pointer
                    # check if a monster is being attacked
                    mousey = True
                    position = pygame.mouse.get_pos()
                    # create a target sprite at that location
                    block = Map_Tile(position, "target", "")
                    self.map_tile_Sprite.add(block)
                    # if a target it should be visible and in the group target
                    target.add(block)
                    target.update()

                if event.type == pygame.MOUSEBUTTONUP:
                    # when mousey is false then effectly player has clicked on a location
                    mousey = False
                    # Stop the wizard
                    self.hero_Sprite.sprites()[0].contact_obstacle = True
                    self.hero_Sprite.update()


                # key press or holding down
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                        print("Key down")
                        shift_pressed = True
                        self.hero_Sprite.sprites()[0].hero_vector = (0, 0)
                        Move_screen[0] = 0
                        Move_screen[1] = 0
                    if event.key == pygame.K_z:
                        if z_wait == False:
                            if self.hero_Sprite.sprites()[0].carry_health > 0 and self.hero_Sprite.sprites()[0].life <= 95:
                                self.hero_Sprite.sprites()[0].carry_health = self.hero_Sprite.sprites()[0].carry_health - 1
                                self.hero_Sprite.sprites()[0].life = 100
                                self.selected()
                        z_wait = True
                    if event.key == pygame.K_x:
                        if x_wait == False:
                            if self.hero_Sprite.sprites()[0].carry_potion > 0 and self.hero_Sprite.sprites()[0].potion <= 95:
                                self.hero_Sprite.sprites()[0].carry_potion = self.hero_Sprite.sprites()[0].carry_potion - 1
                                self.hero_Sprite.sprites()[0].potion = 100
                                self.selected()
                        x_wait = True

                    if event.key == pygame.K_m:
                        show_map = True

                    if event.key == pygame.K_s:
                        if str(self.player_data["sound"]) == "on":
                            self.player_data["sound"] = "off"
                            sound_setting = str(self.player_data["sound"])
                        else:
                            self.player_data["sound"] = "on"
                            sound_setting = str(self.player_data["sound"])
                        with open(self.game_file, 'w') as file:
                            json.dump(self.player_data, file, indent=4)

                    if event.key == pygame.K_d:
                        if str(self.player_data["music"]) == "on":
                            self.player_data["music"] = "off"
                            music_setting = str(self.player_data["music"])
                            pygame.mixer.music.fadeout(10)
                        else:
                            self.player_data["music"] = "on"
                            music_setting = str(self.player_data["music"])
                            pygame.mixer.music.load("venv/music/Mining Town (Loop).wav")
                            pygame.mixer.music.set_volume(0.50)
                            pygame.mixer.music.play(-1, 0.0)

                        with open(self.game_file, 'w') as file:
                            json.dump(self.player_data, file, indent=4)

                # need player to press let go and press again to not use potions up, wait variables used for this
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                        shift_pressed = False
                    if event.key == pygame.K_x:
                        x_wait = False
                    if event.key == pygame.K_z:
                        z_wait = False
                    if event.key == pygame.K_m:
                        show_map = False
                if shift_pressed == True:
                    mousey = False


            # re-draw and move hero if the screen size changes
            if background != self.screen.get_size():
                print('Resized', background, self.screen)
                newbackground = self.screen.get_size()
                xdiff = (newbackground[0] - background[0])/2
                ydiff = (newbackground[1] - background[1])/2

                background = newbackground
                self.change_screen_size(0)


                screen_changed = True
                # updates all the map tiles to be in the right place
                for _ in self.map_tile_Sprite:
                    _.x = _.x + xdiff
                    _.y = _.y + ydiff
                # ensure target of hero resets to its new location
                self.hero_Sprite.sprites()[0].contact_obstacle = True
                self.hero_Sprite.update()




            move_back_map = False

            # Loop through all the tiles to decide what to do
            # Create sprite groups for visible and collision detection (for efficiency hopefully)
            # large levels slow it down and looping through all
            for _ in self.map_tile_Sprite:
                # Adding a test to decide what the wizard can see
                # Once a tile is made visible it will remain visible
                # (hero_x - 360, hero_y - 240, 720, 480)
                # need to look at sides of sprites to decide whether visible
                if _.rect.right  >= hero_x - 360 and _.rect.left <= hero_x + 360 \
                        and _.rect.bottom >= hero_y - 240 and _.rect.top <= hero_y + 240\
                        and _.visible == False:
                    _.visible = True
                    self.visible.add(_)



                #take all sprites out of the the on_screen group
                on_screen.remove(_)
                _.on_screen = False

                # change sprite to be in the on_screen sprite group (assuming this will help performance)
                if _.rect.right  >= 0 and _.rect.left <=  background[0] \
                        and _.rect.bottom >= 0 and _.rect.top <= background[1]\
                        and _.visible == True:
                    on_screen.add(_)
                    # Update sprite status
                    _.on_screen = True

                # some sprites should be deleted if they go off screen in case the keep going forever
                if _.on_screen == False:
                    if _.subtype == "blob" or _.subtype == "fire":
                        _.life = 0



                # monsters group
                if _.object_type == "monster" and _.on_screen == True and _.visible == True:
                    monsters.add(_)

                    #adding group for monsters that may trigger other events
                    # e.g. dragon boss creates fireballs
                    if  _.subtype == "dragon_boss":
                        interactive_monsters.add(_)
                    if _.subtype == "slime":
                        interactive_monsters.add(_)
                else:
                    monsters.remove(_)

                # Remove fireballs if they are not on screen
                if _.subtype == "fireball" and _.on_screen == False:
                    _.life = 0
                    _.attack = 0
                # Remove slime if they are not on screen
                if _.subtype == "slimeball" and _.on_screen == False:
                    _.life = 0
                    _.attack = 0

                # obstacles
                if _.obstacle == True and _.on_screen == True and _.visible == True:
                   obstacles_on_screen.add(_)
                else:
                   obstacles_on_screen.remove(_)

                # interactive
                if _.interactive == True and _.on_screen == True and _.visible == True:
                   interactive_tiles.add(_)
                else:
                   interactive_tiles.remove(_)

                # If the end of level exit is visible and you have the key need to change graphic
                if _.object_type == "door" and _.subtype == "blue" and _.on_screen == True:
                    if "Blue Key" in self.hero_Sprite.sprites()[0].carrying:
                        _.image = _.images[1]

            # checking collision with any background tiles that are obstacles
            # by definition an obstacle will stop our hero
            halted = pygame.sprite.groupcollide(self.hero_Sprite, obstacles_on_screen, False, False)
            if len(halted) >= 1:
                # don't want to loop through as only one wizard
                self.hero_Sprite.sprites()[0].contact_obstacle = True
                self.hero_Sprite.update()
                move_back_map = True
            else:
                self.hero_Sprite.sprites()[0].contact_obstacle = False
                move_back_map = False

            #checking collison of monster with hero
            monster_is_attacking = pygame.sprite.groupcollide(monsters, self.hero_Sprite,  False, False)
            if len(monster_is_attacking)>=1:
                for _ in monster_is_attacking:
                    self.hero_Sprite.sprites()[0].life = self.hero_Sprite.sprites()[0].life - _.attack_strength
                    #change colour and make a sound
                    # life circle
                    pygame.draw.circle(self.screen, (255, 255, 255), (hud_location[0] + 50, hud_location[1] + 50), 50)
                    #some monsters die when contacting hero
                    if _.subtype == "fireball" or _.subtype == "blob":
                        _.life = 0
                        _.attack = 0
                    # You die if life is gone
                    if self.hero_Sprite.sprites()[0].life <=0:
                        self.you_died()
                        return

            #checking collision with target (this triggers a spell)
            monster_is_attacked = pygame.sprite.groupcollide(monsters, target, False, False)
            # Is Monster already being attacked by a spell?
            already_hit_by_spell = pygame.sprite.groupcollide(monsters, spell, False, False)
            if len(monster_is_attacked)>=1:
                for _ in monster_is_attacked:

                    if _ in already_hit_by_spell:
                        shoot = False
                    else:
                        shoot = True
                    #Is the monster 'in range' of hero spell?
                    if _.rect.right >= hero_x - 360 and _.rect.left <= hero_x + 360 \
                            and _.rect.bottom >= hero_y - 240 and _.rect.top <= hero_y + 240:
                        monster_in_range = True
                    else:
                        monster_in_range = False

                    #Spell will only be created if hero has enough potion for a spell and less than 3
                    if self.hero_Sprite.sprites()[0].potion >= self.hero_Sprite.sprites()[0].potion_cost and len(spell) <= 3  \
                            and shoot == True and monster_in_range == True:
                        # Reduce the hero's potion
                        self.hero_Sprite.sprites()[0].potion = self.hero_Sprite.sprites()[0].potion - self.hero_Sprite.sprites()[
                            0].potion_cost
                        block = Map_Tile((_.rect.center), "spell", _.subtype)
                        self.map_tile_Sprite.add(block)
                        spell.add(block)
                        if str(self.player_data["sound"])=="on":
                            block.spell_sound.play()

                        # decrease life of the monster
                        _.life = _.life - 5
                        _.can_move = False

                        # Remove the target sprite it has done it's job
                        for s in target:
                            s.life = 0

                        # If a monster runs out of life they die and gold is spawned
                        if _.life <= 0:

                            # Different monsters will drop different amounts of gold
                            # how much gold?
                            range_from = 0
                            range_to = 0
                            if _.subtype == "skeleton":
                                range_from = 1
                                range_to = 10
                            if _.subtype == "zombie":
                                range_from = 1
                                range_to = 6
                            if _.subtype == "dragon_boss":
                                range_from = 30
                                range_to = 50

                            if _.subtype == "slime":
                                range_from = 1
                                range_to = 2

                            quantity_gold = random.randint(range_from, range_to)
                            if quantity_gold >= 0:
                                for n in range(1, quantity_gold):
                                    block = Map_Tile((_.rect.left + random.randint(0,_.rect.width), _.rect.top + \
                                                      random.randint(0, _.rect.height)), "item", "gold")
                                    self.map_tile_Sprite.add(block)
                        break
                    else:
                        #Tried to attack but are not able due to not enough potion
                        if str(self.player_data["sound"])=="on":
                            self.no_potion.play()

            halted_monsters = pygame.sprite.groupcollide(monsters, obstacles_on_screen, False, False)
            if len(halted_monsters)>=1:
                for _ in halted_monsters:
                    _.contact_obstacle = True
                    _.can_move = False

            #check for any interactive monsters (could be part of map_tile_Sprite loop moved here during troubleshooting)
            if len(interactive_monsters) >= 1:
                for m in interactive_monsters:
                    if m.subtype == "dragon_boss" and m.on_screen == True:
                        # make fireballs random
                        shall_i_fire = random.randint(1, 10)
                        if shall_i_fire == 1:
                            fire_from = [m.rect.centerx, m.rect.top + 20]
                            fire = Map_Tile(fire_from, "monster", "fireball")
                            self.map_tile_Sprite.add(fire)

                    if m.subtype == "slime" and m.on_screen == True:
                        # make blobs random
                        shall_i_fire = random.randint(1, 40)
                        if shall_i_fire == 1:
                            fire_from = [m.rect.centerx, m.rect.centery]
                            fire = Map_Tile(fire_from, "monster", "blob")
                            self.map_tile_Sprite.add(fire)

            # checking whether hero interacts with any objects
            interact = pygame.sprite.groupcollide(interactive_tiles, self.hero_Sprite, False, False)
            if len(interact) >= 1:
                for _ in interact:

                    # What happens to a door
                    if _.object_type == "door":
                        #Does hero have a key
                        if _.key_needed in self.hero_Sprite.sprites()[0].carrying:
                            print(_.key_needed)
                            _.life= 0
                            # If it is a door needing a blue key Level completed
                            if _.key_needed == "Blue Key":
                                self.gold = self.hero_Sprite.sprites()[0].carry_gold
                                self.end_of_level()
                                return

                    # Three types of Key (Red, Green and Blue)
                    # update the hero, then delete it
                    if _.object_type == "redkey":
                        self.hero_Sprite.sprites()[0].carrying.append("Red Key")
                        _.life = 0
                    if _.object_type == "bluekey":
                        self.hero_Sprite.sprites()[0].carrying.append("Blue Key")
                        _.life = 0
                    if _.object_type == "greenkey":
                        self.hero_Sprite.sprites()[0].carrying.append("Green Key")
                        _.life = 0
                    # if you walk into a pot
                    if _.object_type == "pot":
                        # random item or not
                        self.hero_Sprite.sprites()[0].contact_obstacle = False
                        type_of_object = random.randint(1,5)
                        if type_of_object == 2:
                            block = Map_Tile((_.x, _.y), "item", "health")
                            self.map_tile_Sprite.add(block)
                        if type_of_object == 3:
                            block = Map_Tile((_.x, _.y), "item", "potion")
                            self.map_tile_Sprite.add(block)
                        else:
                            # how much gold?
                            quantity_gold = random.randint(1,5)
                            for n in range(1,quantity_gold):
                                block = Map_Tile((_.x + (4 * n), _.y + random.randint(-10,10)), "item", "gold")
                                self.map_tile_Sprite.add(block)
                        # set life to 0 as pot needs to be destroyed
                        _.life = 0

                    if _.object_type == "item":
                        _.found = True
                        _.obstacle= False
                        _.interactive = False
                        self.hero_Sprite.sprites()[0].contact_obstacle = False
                        if _.subtype == "gold":
                            self.hero_Sprite.sprites()[0].carry_gold = self.hero_Sprite.sprites()[0].carry_gold  + 1
                        if _.subtype == "health":
                            self.hero_Sprite.sprites()[0].carry_health = self.hero_Sprite.sprites()[0].carry_health + 1
                        if _.subtype == "potion":
                            self.hero_Sprite.sprites()[0].carry_potion = self.hero_Sprite.sprites()[0].carry_potion + 1



            if mousey == True:
                position = pygame.mouse.get_pos()
                for _ in self.hero_Sprite:
                    _.target_location = position
             #    #for _ in target:
                #    _.x = position[0]
               #     _.y = position[1]



            #only updating screen if we are not moving back (otherwise you get screen judder)
            if move_back_map == False or screen_changed == True:
                # needed to clear out the sprites
                self.screen.fill((0,0,0))
                #not using circle - too vague
                #pygame.draw.circle(self.screen, (180,129,22), (hero_x ,hero_y ), 350, 2)
                #draw the sprites
                on_screen.draw(self.screen)
                pygame.draw.rect(self.screen, (0, 0, 255), (hero_x - 360, hero_y - 240, 720, 480), 1)
                self.hero_Sprite.draw(self.screen)
                screen_changed = False
                #Need a loop to add health details to all visible monsters
                for _ in monsters:
                    # Are the monster on the screen
                    if _ in on_screen:
                        # draw the life bar

                        # also excluding life on fireballs
                        if _.subtype != "fireball" and _.subtype != "blob":
                            # had to add this as rect went weird and crashes if off the screen
                            if _.rect.left >= 0 and _.rect.top >= 15:
                                bar_size = (_.life / _.full_life) * 50
                                x = _.rect.left + (_.rect.width / 4)
                                y = _.rect.top - 5

                                pygame.draw.rect(self.screen, (255, 0, 0), (x, y, bar_size, 3))
                                life = "Life:" + str(_.life)
                                my_ft_font.render_to(self.screen, (x , y - 10), life, (255, 0, 0))

            #regenerate Spell and health
            if self.hero_Sprite.sprites()[0].life <=100:
                self.hero_Sprite.sprites()[0].life = self.hero_Sprite.sprites()[0].life + 0.05
            if self.hero_Sprite.sprites()[0].potion <=100:
                self.hero_Sprite.sprites()[0].potion = self.hero_Sprite.sprites()[0].potion + 0.1

            # Update health and Potion HUD (this will change whether or not you are moving)
            hud_location = [0,background[1]-100]
            health = 100 - self.hero_Sprite.sprites()[0].life
            potion = 100 - self.hero_Sprite.sprites()[0].potion

            # add to hud for carrying text and possible title
            pygame.draw.rect((self.screen), (0, 0, 0), [hud_location[0], hud_location[1]-30, 300, 30])
            # hud
            pygame.draw.rect((self.screen), (0, 0, 0), [hud_location[0], hud_location[1], 300, 100])

            # life globe is red, turns pale if attacked
            if len(monster_is_attacking)>=1:
                 # life circle
                 pygame.draw.circle(self.screen, (255, 50, 0), (hud_location[0] + 50, hud_location[1] + 50), 50)
            else:
                # life circle
                pygame.draw.circle(self.screen, (255, 0, 0), (hud_location[0]+50,hud_location[1]+50 ), 50)
            # potion is pink, turns pale when spell cast
            if len(spell) >= 1:
                # Spell circle
                pygame.draw.circle(self.screen, (255, 100, 255), (hud_location[0] + 150, hud_location[1] + 50), 50)
            else:
                pygame.draw.circle(self.screen, (255, 0, 255), (hud_location[0] + 150, hud_location[1] + 50), 50)

            #adjust stats to current state
            pygame.draw.rect((self.screen), (0, 0, 0), [hud_location[0], hud_location[1], 100, health])
            pygame.draw.rect((self.screen), (0, 0, 0), [hud_location[0] + 100, hud_location[1] , 100, potion])

            #text of hud
            my_ft_font.render_to(self.screen, (hud_location[0], hud_location[1]), "LIFE", (255, 0, 0))
            my_ft_font.render_to(self.screen, (hud_location[0] + 100 - 10, hud_location[1]), "SPELL", (255, 0, 255))
            if self.hero_Sprite.sprites()[0].carry_health >= 1:
                my_ft_font.render_to(self.screen, (hud_location[0] + 50, hud_location[1] + 50), "Z", (255, 0, 0))
            if self.hero_Sprite.sprites()[0].carry_potion >= 1:
                my_ft_font.render_to(self.screen, (hud_location[0] + 150, hud_location[1] + 50), "X", (255, 0, 255))

            my_ft_font.render_to(self.screen, (hud_location[0] , hud_location[1] -20 ), "CARRYING:" +
                                 str(self.hero_Sprite.sprites()[0].carrying), (255, 255, 255))

            my_ft_font.render_to(self.screen, (hud_location[0] + 210 , hud_location[1] + 20), "GOLD   : " +
                                 str(self.hero_Sprite.sprites()[0].carry_gold), (255, 255, 255))
            my_ft_font.render_to(self.screen, (hud_location[0] + 210 , hud_location[1] + 40), "HEALTH : " +
                                 str(self.hero_Sprite.sprites()[0].carry_health), (255, 255, 255))
            my_ft_font.render_to(self.screen, (hud_location[0] + 210 , hud_location[1] + 60), "POTION : " +
                                 str(self.hero_Sprite.sprites()[0].carry_potion), (255, 255, 255))

            # Update the sprites
            self.hero_Sprite.update()
            self.map_tile_Sprite.update()

            #If a spell is cast you want to see the line (added at the end so it will be on top and visible)
            if len(spell)>=1:
                if self.hero_Sprite.sprites()[0].current_direction == "right":
                    adjust_spell_start = + 10
                else:
                    adjust_spell_start = - 10
                for _ in spell:
                    pygame.draw.line(self.screen, (0, 255, 0), (_.x, _.y),
                                     ( hero_x + adjust_spell_start, hero_y - 25), 2)

            if show_map == True:
                self.map()
            # Flip the display
            pygame.display.flip()

        return

    def map(self):
        #find minimum x and y
        x_list = []
        y_list = []

        for _ in self.visible:
            if _.obstacle == True:
                x_list.append(_.x)
                y_list.append(_.y)
        #needed incase no visible tiles are obstacle type
        if len(x_list) > 0 and len(y_list) > 0 :
            top =  min(x_list)
            left =  min(y_list)
        else:
            top = 0
            left = 0
        scale = 10

        for _ in self.visible:
            if _.obstacle == True:
                pygame.draw.rect(self.screen, (0,255,0),(10 + (_.x - top) /scale, 10 + (_.y - left) /scale,8,8))


    def draw_the_menu(self, screen, from_level):
        global my_buttons
        keepgoing = True
        screen.fill((0, 0, 0))

        my_ft_font_header_1 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 64)
        my_ft_font_header_2 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 32)
        my_ft_font_instruction = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 18)
        my_ft_font = pygame.freetype.SysFont('Courier', 16)
        one_third_of_screen = screen.get_width()/3
        if one_third_of_screen <=220:
            one_third_of_screen = 220
        screen_height = screen.get_height()

        # On screen items
        my_ft_font_header_1.render_to(screen, (5, 5), "Wizardy Menu", (255, 0, 255))
        my_ft_font_header_2.render_to(screen, (5, self.screen_setting[1] - 37), "Gold = " + str(self.player_data["gold"]), (255, 255, 0))
        my_ft_font_header_2.render_to(screen, (5, 74), "Select Level", (255, 255, 0))

        #find the number of levels files there are (they need to be in sequentual number)
        level = from_level
        start_of_button_x = one_third_of_screen - 220
        start_of_button_y = 125
        space_between_buttons = 75
        my_buttons = []
        while keepgoing:
            if start_of_button_y + space_between_buttons >= screen_height:
                my_buttons.append(
                    Button(screen, start_of_button_x, start_of_button_y, "More", 16, (0, 255, 0), level, 75, 50))
                keepgoing = False
            else:
                if level <= self.player_data["level"]:
                    colour = (0,255,0)
                else:
                    colour = (100,100,100)
                my_buttons.append(Button(screen, start_of_button_x, start_of_button_y, "Level " + str(level), 16, colour, level, 150, 50))
                start_of_button_y = start_of_button_y + space_between_buttons
                level = level + 1
                level_file = 'venv/maps/Level ' + str(level) + '.csv'
                keepgoing = os.path.exists(level_file)

        # Add the options screen button
        my_buttons.append(
            Button(screen, self.screen_setting[0] - 80, self.screen_setting[1] - 165, "Options", 16, (0, 255, 0), "", 75, 50))
        # Add the credits screen button
        my_buttons.append(
            Button(screen, self.screen_setting[0] - 80, self.screen_setting[1] - 110, "Credits", 16, (0, 255, 0), "", 75, 50))

        # Add the quit button
        my_buttons.append(
            Button(screen, self.screen_setting[0] - 80, self.screen_setting[1] - 55, "Quit", 16, (0, 255, 0), "", 75, 50))

        #if not the first screen of level, then need a button to reset to 1
        print("From Level is", from_level)
        if from_level > 1:
            #start_of_button_y = start_of_button_y + space_between_buttons
            print("Start of y button reset", start_of_button_y)
            my_buttons.append(
                Button(screen, start_of_button_x + 75, start_of_button_y, "Reset", 16, (0, 255, 0), 1, 75, 50))

        #Add the instructions:
        instructions = [
            "Nobody remembers why Wizardy entered the catacombs. Some",
            "say he was thrown out of his order because of his greed",
            "and avarice and sought wealth there.",
            "Others say he made a vow to a long dead ancient king",
            "to protect the world from evil.",
            "No matter.. Your job is to guide him..",
            "",
            "",
            "Direction - Mouse (hold down button)",
            "Attack - Click on Monster",
            "Hold your position - Shift",
            "Replenish Health - Z",
            "Replenish Magic - X",
            "Map - M",
            "",
            "Toggle Sound  - S",
            "Toggle Music - D",
            "",
            "Good Luck."]

        row = 100
        for line in instructions:
            my_ft_font_instruction.render_to(screen, (one_third_of_screen, row), line, (255, 255, 0))
            row = row + 25

    def draw_the_options(self):
        global my_buttons
        self.screen.fill((0, 0, 0))

        my_ft_font_header_1 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 64)
        my_ft_font_header_2 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 32)
        my_ft_font_instruction = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 18)
        my_ft_font = pygame.freetype.SysFont('Courier', 16)
        one_third_of_screen = self.screen.get_width() / 3
        if one_third_of_screen <=220:
            one_third_of_screen = 220

        # On screen items
        my_ft_font_header_1.render_to(self.screen, (one_third_of_screen - 220, 0), "Options" , (255, 255, 255))
        #my_ft_font_header_2.render_to(screen, (one_third_of_screen - 220, 70), "Select Level", (255, 255, 255))


        # find the number of levels files there are (they need to be in sequentual number)
        start_of_button_x = one_third_of_screen - 220
        start_of_button_y = 125
        space_between_buttons = 75
        my_buttons = []

        # Add the options  button
        my_ft_font_header_2.render_to(self.screen, (start_of_button_x, 110), "Sound: " + self.player_data["sound"], (255, 255, 255))
        my_buttons.append(
            Button(self.screen, one_third_of_screen * 2, 100, "Sound", 16, (0, 255, 0), "", 150, 50))
        #my_buttons.append(
        #    Button(screen, one_third_of_screen * 2 + 50, 100, "Off", 16, (0, 255, 0), "", 50, 50))

        my_ft_font_header_2.render_to(self.screen, (start_of_button_x, 160), "Music: " + self.player_data["music"], (255, 255, 255))
        my_buttons.append(
            Button(self.screen, one_third_of_screen * 2, 150, "Music", 16, (0, 255, 0), "", 150, 50))

        my_ft_font_header_2.render_to(self.screen, (start_of_button_x, 210), "Screen: " + self.player_data["screen"], (255, 255, 255))
        my_buttons.append(
            Button(self.screen, one_third_of_screen * 2, 200, "Screen", 16, (0, 255, 0), "", 150, 50))
        my_ft_font_instruction.render_to(self.screen, (start_of_button_x, 250), "Switching from FULL to RESIZE takes time..",
                                      (255, 255, 255))
        my_buttons.append(
            Button(self.screen, one_third_of_screen * 2, 300, "Return", 16, (0, 255, 0), "", 150, 50))

    def draw_the_credits(self):
        global my_buttons
        self.screen.fill((0, 0, 0))

        my_ft_font_header_1 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 64)
        my_ft_font_header_2 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 32)
        my_ft_font_credits = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", 18)
        my_ft_font = pygame.freetype.SysFont('Courier', 16)
        one_third_of_screen = self.screen.get_width() / 3
        if one_third_of_screen <=220:
            one_third_of_screen = 220

        # On screen items
        my_ft_font_header_1.render_to(self.screen, (one_third_of_screen - 220, 0), "Credits" , (255, 255, 255))

        start_of_button_x = one_third_of_screen - 220
        my_buttons = []

        # Add the instructions:
        credits = [
            "Graphics and game: Adam Thirlwell (thirlwella@gmail.com)",
            "Code license: GNU General Public License v3.0",
            "Assets license: http://creativecommons.org/licenses/by/4.0/ ",
            "",
            "Font: https://www.fontspace.com/edge-of-the-galaxy-font-f45748",
            "license: Public Domain",
            "",
            "Sounds various:",
            "sampled from https://mixkit.co/free-sound-effects/game/ royalty free files",
            "original recordings by Adam Thirlwell",
            "",
            "Music: https://chrislsound.itch.io/fantasy-towns-music-pack",
            "License: [Creative Commons Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/)",
            "",
            "Wizardy Release version 1.0"]

        row = 100
        for line in credits:
            my_ft_font_credits.render_to(self.screen, (one_third_of_screen, row), line, (255, 255, 0))
            row = row + 25


        my_buttons.append(
            Button(self.screen, self.screen_setting[0] - 155, self.screen_setting[1] - 55 , "Return", 16, (0, 255, 0), "", 150, 50))


    def menu(self, which_menu):
        global background
        global my_buttons
        keepgoing = True
        global sound_setting
        global music_setting
        self.level_playing =""

        background = pygame.Surface(self.screen.get_size())

        clock = pygame.time.Clock()

        # draws the main menu
        if which_menu == "options":
            self.draw_the_options()
        elif which_menu == "credits":
            self.draw_the_credits()
        else:
            self.draw_the_menu(self.screen, which_menu)

        while keepgoing:
            clock.tick(30)
            pygame.display.flip()
            background = pygame.Surface(self.screen.get_size())
            background.fill((0, 0, 0))
            halfway = background.get_width() / 2
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if which_menu != "options" and which_menu != "credits":
                        self.level_playing = "end game"
                    keepgoing = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    position = pygame.mouse.get_pos()

                    for _ in my_buttons:
                        if position[0] >= _.position_x and \
                            position[0] <= _.position_x + _.button_width and \
                            position[1] >= _.position_y and \
                            position[1] <= _.position_y + _.button_height:
                            if _.active == False:
                                _.active = True
                                _.button_activated(self.screen)
                                pygame.display.flip()
                                if _.text == "More":
                                    if _.next_screen == 0:
                                        _.next_screen = 1
                                    self.menu_start = _.next_screen
                                    keepgoing = False
                                elif _.text  == "Return" or _.text == "Reset":
                                    self.level_playing = ""
                                    self.menu_start = 1
                                    keepgoing = False
                                elif _.text == "Options" :
                                    self.level_playing = "options"
                                    keepgoing = False
                                    self.menu_start = 1
                                elif _.text == "Credits" :
                                    self.level_playing = "credits"
                                    keepgoing = False
                                    self.menu_start = 1
                                elif _.text == "Quit":
                                    self.level_playing = "end game"
                                    keepgoing = False

                                elif _.text == "Sound" or _.text == "Music" or _.text == "Screen":
                                    # save to file add here and toggle to be added
                                    print(_.text)
                                    if _.text == "Screen":
                                        if self.player_data["screen"] == "full":
                                            #https://github.com/pygame/pygame/issues/2360
                                            pygame.quit()  # ???
                                            os.environ['SDL_VIDEO_WINDOW_POS'] = str(100) + "," + str(100)
                                            #os.environ['SDL_VIDEO_CENTERED'] = '1'
                                            pygame.init()  # ???
                                            self.screen = pygame.display.set_mode(self.screen_setting, pygame.RESIZABLE)
                                            self.player_data["screen"] = "resize"
                                        else:
                                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                                            #pygame.display.set_mode(self.screen_setting, pygame.FULLSCREEN)
                                            self.player_data["screen"] = "full"

                                    if _.text == "Sound":
                                        if str(self.player_data["sound"]) == "on":
                                            self.player_data["sound"] = "off"
                                            sound_setting = str(self.player_data["sound"])
                                        else:
                                            self.player_data["sound"] = "on"
                                            sound_setting = str(self.player_data["sound"])

                                    if _.text == "Music":
                                        if str(self.player_data["music"]) == "on":
                                            self.player_data["music"] = "off"
                                            music_setting = str(self.player_data["music"])
                                            pygame.mixer.music.fadeout(10)
                                        else:
                                            self.player_data["music"] = "on"
                                            music_setting = str(self.player_data["music"])
                                            if music_setting == "on":
                                                pygame.mixer.music.load("venv/music/Mining Town (Loop).wav")
                                                pygame.mixer.music.set_volume(0.50)
                                                pygame.mixer.music.play(-1, 0.0)


                                    with open(self.game_file, 'w') as file:
                                        json.dump(self.player_data, file, indent=4)

                                    #need to redraw the screen to show the changes
                                    self.draw_the_options()

                                else:
                                    if "Level" not in _.text:
                                        print("Button ", _.text, " was pressed and has no action")
                                    else:
                                        print(_.level, self.player_data["level"])
                                        if _.level <= self.player_data["level"]:
                                            #self.level(_.text)
                                            self.level_playing = _.text
                                            return
                                        else:
                                            print("Level ", _.level, " still locked")
                                            _.active = False
                                            time.sleep(.25)
                                            _.button_activated(self.screen)
                                            pygame.display.flip()
                            else:
                                _.active = False
                                _.button_activated(self.screen)
                                pygame.display.flip()

                        #print("MISS", _.position_x, _.button_width, _.position_y, _.button_height)

                        #keepgoing = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        keepgoing = False

            if self.screen_setting[0] != background.get_width() or self.screen_setting[1] != background.get_height():
                self.change_screen_size(1)

        return(self.screen)

    def change_screen_size(self, level):
        self.screen_setting = self.screen.get_size()
        # write changes out of screen size to file
        self.player_data["screen_height"] = self.screen_setting[1]
        self.player_data["screen_width"] = self.screen_setting[0]
        self.save_player_data()
        self.draw_the_menu(self.screen, level)

    def save_player_data(self):
        # save screen changes out to file
        with open(self.game_file, 'w') as file:
            json.dump(self.player_data, file, indent=4)

    def selected(self):
        global sound_setting
        if sound_setting == "on":
            self.select_sound.play()

    def end_of_level(self):
        font_size = 64
        my_ft_font_header_1 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", font_size)

        for m in range(1, 20):
            my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m), "Level Completed!", (255, 255, 0))
            my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m + 100) ,
                                      "Gold found = " + str(self.gold),
                                      (255, 255, 0))
        my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m),
                                      "Level Completed!", (0, 255, 64))
        my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m + 100),
                                      "Gold found = " + str(self.gold),
                                      (0, 255, 0))
        self.player_data["gold"] = self.player_data["gold"] + self.gold
        level_number = int(self.name.replace("Level ",""))
        player_level_number = int(self.player_data["level"])
        if player_level_number <= level_number:
            self.player_data["level"] = level_number + 1

        self.save_player_data()
        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return

    def you_died(self):
        font_size = 64
        my_ft_font_header_1 = pygame.freetype.Font("venv/fonts/EdgeOfTheGalaxyRegular-OVEa6.otf", font_size)
        for m in range(1,20):
            my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m), "Level failed!", (255, 255, 0))
            my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m + 100),
                                      "No gold.. ",
                                      (255, 255, 0))
        my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m), "Level failed!",
                                      (255, 0, 0))
        my_ft_font_header_1.render_to(self.screen, (self.screen_setting[0] / 3 + m, self.screen_setting[1] / 3 + m + 100 ),
                                      "No gold.. ",
                                      (255, 0, 0))
        pygame.display.flip()
        if str(self.player_data["sound"]) == "on":
            self.you_died_sound.play()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return

if __name__ == '__main__':
    pygame.init()
    wizardy = Game()
    wizardy.menu_start = 1
    donePlaying = False
    while not donePlaying:
        # open main menu
        wizardy.menu(wizardy.menu_start)
        # Open level listed (menu will return this)
        if "Level" in wizardy.level_playing:
            play_level = wizardy.level(wizardy.level_playing)
        if "options" in wizardy.level_playing:
            wizardy.menu("options")
        if "credits" in wizardy.level_playing:
            wizardy.menu("credits")
        if wizardy.level_playing == "end game":
            donePlaying = True
    # Done! Time to quit.
    pygame.quit()

# Developed using PyCharm https://www.jetbrains.com/help/pycharm/
