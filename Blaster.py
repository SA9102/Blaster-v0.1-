import pygame
from sys import exit
import random

# Classes
class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        original_image = pygame.image.load('graphics/player/player_a.png').convert_alpha()
        self.image = pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2))
        self.rect = self.image.get_rect(center = (100, 100))
        self.lives = 3
        self.invincible = False
        self.invincible_timer = 0

    # Go to the mouse cursor (the user controls the player with the mouse).
    def get_movement(self):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.x = mouse_pos[0] - (self.rect.width // 2)
        self.rect.y = mouse_pos[1] - (self.rect.height // 2)

    # Shoot a laser when the user click the mouse.
    def create_laser(self):
        laser_sound_1.play()
        return Laser(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])

    # When the player gets hit by a meteor, reduce life by one.
    # Make the player invincible for a while so that the player cannot get hit
    # by more than one meteor in quick succession. The invincibility is
    # controlled by a timer.
    def receive_damage(self):
        global game_active
        if pygame.sprite.spritecollide(self, meteor_group, True) and self.invincible == False:
            self.invincible = True
            self.lives -= 1
            if self.lives < 1:
                lose.play()
                game_active = False
                self.kill()
            else:
                self.invincible_timer = 120

    # Draw the player's lives on the screen.
    def render_lives(self):
        for life in range(self.lives):
            screen.blit(life_image_surf, (life * 30 + 10, 42))


    # In every frame, call these methods to update the player's actions.
    def update(self):
        self.get_movement()
        self.receive_damage()
        self.render_lives()
        if self.invincible_timer > 0:
            if self.invincible_timer >= 100 or (self.invincible_timer < 80 and self.invincible_timer >= 60) or (self.invincible_timer < 40 and self.invincible_timer >= 20):
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(300)
            self.invincible_timer -= 1
            if self.invincible_timer == 0:
                self.image.set_alpha(255)
                self.invincible = False

class Laser(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        laser_1 = pygame.image.load('graphics/lasers/laser_1.png')
        laser_2 = pygame.image.load('graphics/lasers/laser_7.png')
        laser_3 = pygame.image.load('graphics/lasers/laser_12.png')

        laser_images = [pygame.transform.scale(laser_1, (laser_1.get_width() // 2, laser_1.get_height() // 2)),
                        pygame.transform.scale(laser_2, (laser_2.get_width() // 2, laser_2.get_height() // 2)),
                        pygame.transform.scale(laser_3, (laser_3.get_width() // 2, laser_3.get_height() // 2))]
        # laser_image_index = 
        self.image = random.choice(laser_images)
        self.rect = self.image.get_rect(center = (x, y))

    def destroy(self):
        if self.rect.left > WIDTH:
            self.kill()

    def update(self):
        self.destroy()
        self.rect.x += 6
        # if pygame.sprite.spritecollide(self, meteor_group, False):
            # damage_group.add(Damage(self.rect.right, self.rect.centery))

# The stars that float in the background.
class Star(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()

        star_1 = pygame.image.load('graphics/effects/star_1.png').convert_alpha()
        star_2 = pygame.image.load('graphics/effects/star_2.png').convert_alpha()
        star_3 = pygame.image.load('graphics/effects/star_3.png').convert_alpha()

        star_images = [pygame.transform.scale(star_1, (star_1.get_width() // 5, star_1.get_height() // 5)),
                       pygame.transform.scale(star_2, (star_2.get_width() // 5, star_2.get_height() // 5)),
                       pygame.transform.scale(star_3, (star_3.get_width() // 5, star_3.get_height() // 5))]

        self.image = random.choice(star_images)
        self.rect = self.image.get_rect(center = (WIDTH + random.randint(100, 200), random.randint(-5, HEIGHT + 5)))
        self.speed = random.randint(1,3)

    # Remove the star from memory when it is out of sight.
    def destroy(self):
        if self.rect.x < -50:
            self.kill()

    def update(self):
        self.rect.x -= self.speed
        self.destroy()

# The objects which the player can shoot, and can make the player lose life if they hit the player
class Meteor(pygame.sprite.Sprite):

    def __init__(self, meteor_image, multiplier):
        super().__init__()
        self.original_image = meteor_image
        self.image = self.original_image
        self.rect = self.image.get_rect(center = (WIDTH + random.randint(100, 200), random.randint(-5, HEIGHT + 5)))
        # The multiplier determines the meteor's health, as well as the number
        # of points gained from destroying it. The bigger the meteor, the greater
        # the multiplier.
        self.multiplier = multiplier
        self.speed = random.randint(1,4)
        self.rotation_speed = random.randint(1,4)
        self.angle = 0
        self.health = self.multiplier
        self.damage_timer = 0
        self.timer = 0

    
    def destroy(self):
        # If the meteor is out of sight, or the game is no longer active (which happens when the player loses)
        if self.rect.x < -100 or game_active == False:
            self.kill()

        # If the player shoots and destroys the meteor
        global extra_score
        if self.health <= 0:
            self.kill()
            explosion.play()
            points_message_group.add(PointsMessage(self.rect.centerx, self.rect.centery, (1500 * self.multiplier) // 50))
            
            extra_score += 1500 * self.multiplier

    # Each meteor will constantly rotate about its center while moving
    def rotate(self):
        self.angle += self.rotation_speed
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

    def update(self):
        # self.image.set_colorkey((100, 100, 200))
        self.rect.x -= self.speed
        self.rotate()
        # Reduce the health of the meteor if it gets hit by the player's laser
        if pygame.sprite.spritecollide(self, laser_group, True):
            # damage_group.add(Damage(self.rect.left, self.rect.centery))
            self.timer = 5
            self.damage_timer = 5
            self.health -= 1
            # self.image.set_colorkey((0, 0, 0))

        # Create a transparency effect when the meteor took damage.
        if self.damage_timer > 0:
            self.damage_timer -= 1
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)
        self.destroy()

# A message that appears when the player destroys a meteor.
# This will be a number that represents the points gained.
class PointsMessage(pygame.sprite.Sprite):

    def __init__(self, x, y, points):
        super().__init__()
        
        self.image = text_font_tiny.render(f'{points}', True, (255, 255, 255))
        self.rect = self.image.get_rect(center = (x, y))
        self.alpha = 350

    # When a meteor is destroyed, the message will appear.
    # It will float up and reduce opacity simultaneously.
    def update(self):
        self.rect.y -= 0.1
        self.image.set_alpha(self.alpha)
        self.alpha -= 7
        if self.alpha <= 0:
            self.kill()

# class Damage(pygame.sprite.Sprite):

#     def __init__(self, x, y):
#         super().__init__()

#         original_image = pygame.image.load('graphics/lasers/damage.png').convert_alpha()
#         self.image = pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2))
#         self.rect = self.image.get_rect(center = (x, y))
#         # self.alpha = 300
#         self.timer = 2

#     def update(self):
#         # self.alpha -= 10
#         # self.image.set_alpha(self.alpha)
#         # if self.alpha <= 10:
#         #     self.kill()

#         self.timer -= 1
#         if self.timer <= 0:
#             self.kill()

# Calculates current score and renders it to the screen
def display_score(extra_score):
    global score
    global high_score
    score = pygame.time.get_ticks() - start_time + extra_score
    if score > high_score:
        high_score = score
    score_surf = text_font_small.render(f'{score // 50}', True, (255, 255, 255))
    score_rect = score_surf.get_rect(topleft = (10, 10))
    screen.blit(score_surf, score_rect)

pygame.init()
WIDTH = 650
HEIGHT = 350
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Blaster')
clock = pygame.time.Clock()

# Game variables
game_active = False
begin = True
score = 0
high_score = 0
extra_score = 0
message_visible = True
start_time = 0

# Fonts
text_font_tiny = pygame.font.Font('font/kenvector_future.ttf', 15)
text_font_small = pygame.font.Font('font/kenvector_future.ttf', 20)
text_font_big = pygame.font.Font('font/kenvector_future.ttf', 25)
text_font_large = pygame.font.Font('font/kenvector_future.ttf', 40)

# Objects
player = pygame.sprite.GroupSingle()
laser_group = pygame.sprite.Group()
damage_group = pygame.sprite.Group()
star_group = pygame.sprite.Group()
meteor_group = pygame.sprite.Group()
points_message_group = pygame.sprite.Group()

# Surfaces
background_1 = pygame.transform.scale2x(pygame.image.load('graphics/backgrounds/black.png').convert_alpha())

life_image_surf = pygame.transform.rotozoom(pygame.image.load('graphics/player/player_a.png'), 0, 0.3).convert_alpha()

meteor_brown_tiny_1 = pygame.image.load('graphics/meteors/meteorBrown_tiny1.png').convert_alpha()
meteor_brown_tiny_2 = pygame.image.load('graphics/meteors/meteorBrown_tiny2.png').convert_alpha()
meteor_brown_small_1 = pygame.image.load('graphics/meteors/meteorBrown_small1.png').convert_alpha()
meteor_brown_small_2 = pygame.image.load('graphics/meteors/meteorBrown_small2.png').convert_alpha()

meteor_grey_tiny_1 = pygame.image.load('graphics/meteors/meteorGrey_tiny1.png').convert_alpha()
meteor_grey_tiny_2 = pygame.image.load('graphics/meteors/meteorGrey_tiny2.png').convert_alpha()
meteor_grey_small_1 = pygame.image.load('graphics/meteors/meteorGrey_small1.png').convert_alpha()
meteor_grey_small_2 = pygame.image.load('graphics/meteors/meteorGrey_small2.png').convert_alpha()

meteors_list = [[meteor_brown_tiny_1, 1],
           [meteor_brown_tiny_2, 1],
           [meteor_grey_tiny_1, 1],
           [meteor_grey_tiny_2, 1],
           [meteor_brown_small_1, 2],
           [meteor_brown_small_2, 2],
           [meteor_grey_small_1, 2],
           [meteor_grey_small_2, 2],
           [meteor_brown_small_1, 2],
           [meteor_brown_small_2, 2],
           [meteor_grey_small_1, 2],
           [meteor_grey_small_2, 2]]


# Sounds
laser_sound_1 = pygame.mixer.Sound('sound/sfx_laser1.ogg')
laser_sound_2 = pygame.mixer.Sound('sound/sfx_laser2.ogg')
lose = pygame.mixer.Sound('sound/sfx_lose.ogg')
explosion = pygame.mixer.Sound('sound/sfx_explosion.wav')
start = pygame.mixer.Sound('sound/sfx_twoTone.ogg')

# Timers
star_render_timer = pygame.USEREVENT + 1
meteor_render_timer = pygame.USEREVENT + 2
message_timer = pygame.USEREVENT + 3

pygame.time.set_timer(star_render_timer, 800)
pygame.time.set_timer(meteor_render_timer, 1000)
pygame.time.set_timer(message_timer, 800)

while True:
    for event in pygame.event.get():

        # If the user presses the 'cross' on the top right of the windows to exit.
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Timer that renders a star.
        if event.type == star_render_timer:
            star_group.add(Star())

        # If the user is playing the game
        if game_active:

            # Shoot a laser when the user clicks the mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                laser_group.add(player.sprite.create_laser())


            # Timer that renders a meteor
            if event.type == meteor_render_timer:
                meteor = random.choice(meteors_list)
                meteor_group.add(Meteor(meteor[0], meteor[1]))

        # If the game is not active
        else:

            # Every time this timer is triggered, the visibility of the message
            # is toggled, to create a blinking effect.
            if event.type == message_timer:
                message_visible = not message_visible

            # Start the game when the users presses the space bar.
            # Reset the score and player lives.
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                start.play()
                player.add(Player())
                start_time = pygame.time.get_ticks()
                extra_score = 0
                # player.sprite.lives = 3
                game_active = True
                begin = False

    screen.fill('#141414')




    # screen.fill(sky_colour)
    #121012
    #2A2D33
    #3A2E3F
    #5E3F6B
    # screen.blit(background_1, (0, 0))

    # Draw stars and update their positions
    star_group.draw(screen)
    star_group.update()

    # If the game is active
    if game_active:

        # Draw the assets on the screen and update their positions.

        laser_group.draw(screen)
        laser_group.update()

        player.draw(screen)
        player.update()

        meteor_group.draw(screen)
        meteor_group.update()

        damage_group.draw(screen)
        damage_group.update()

        display_score(extra_score)

        points_message_group.draw(screen)
        points_message_group.update()

    # If the game is not active
    else:

        # If the user has just opened the game.
        # Render the title and the message prompting the user to start the game.
        if begin == True:
            title_surf = text_font_large.render('Blaster', True, (255, 255, 255))
            title_rect = title_surf.get_rect(center = (WIDTH // 2, 125))

            message_surf = text_font_big.render('Press SPACE to start', True, (255, 255, 255))
            message_rect = message_surf.get_rect(center = (WIDTH // 2, 300))

            screen.blit(title_surf, title_rect)
            if message_visible:
                screen.blit(message_surf, message_rect)

        # If the user just lost.
        # Render the score, high score, and the message prompting the user to start the game.
        else:
            score_surf = text_font_large.render(f'Score: {score // 30}', True, (255, 255, 255))
            score_rect = score_surf.get_rect(center = (WIDTH // 2, 100))

            high_score_surf = text_font_large.render(f'High Score: {high_score // 30}', True, (255, 255, 255))
            high_score_rect = high_score_surf.get_rect(center = (WIDTH // 2, 160))

            message_surf = text_font_big.render('Press SPACE to restart', True, (255, 255, 255))
            message_rect = message_surf.get_rect(center = (WIDTH // 2, 300))

            screen.blit(score_surf, score_rect)
            screen.blit(high_score_surf, high_score_rect)
            if message_visible:
                screen.blit(message_surf, message_rect)

    # Update the display.
    pygame.display.update()
    # Maximum FPS is 60.
    clock.tick(60)