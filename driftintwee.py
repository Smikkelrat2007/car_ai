import pygame
import math
import sys
from collections import deque
import random
import os
import glob

os.chdir(os.path.dirname(os.path.abspath(__file__)))


track_info_dictionary = {"untitled-2.png":[200, 100, 90],"track.png":[400, 300, 90],"track2.png":[200, 100, 90],"lukeenbastrack.png": [500, 500, 270]} #"track_naam.png":[spawn_positie_x, spawn_positie_y, spawn_hoek]

def krijg_alle_tracks_in_directory():
    directory_python_file = os.path.dirname(os.path.abspath(__file__))
    image_files = glob.glob(os.path.join(directory_python_file, '*.*'))
    return [os.path.basename(file) for file in image_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

def absolute_waarde(value):
    return abs(value)

def spawn_rays(ray_angles, a, x, y, skipping_factor, background_image):
    length_list = []
    for angle in ray_angles:
        if isinstance(angle, list):
            length_list.extend(spawn_rays(angle, ray_angle, length_list[-1][1][0], length_list[-1][1][1], skipping_factor, background_image))
        else:
            ray_angle = angle + a
            ray = Ray(x, y, ray_angle, skipping_factor, background_image)
            ray.start()
            while not ray.check_intersect():
                ray.step()
            length_list.append([ray.get_length(), ray.get_position()])
    return length_list

def position_mask(x, y, dictionary, i, background_image, screen_width, screen_height):
    queue = deque([(x, y, i)])
    visited = set([(x, y)])
    highest_value = 0
    while queue:
        x, y, current_value = queue.popleft()
        if current_value > highest_value:
            highest_value = current_value
        color_at_position = background_image.get_at((x, y))
        if color_at_position != BLACK:
            continue
        dictionary[x, y] = current_value
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < screen_width and 0 <= new_y < screen_height:
                if (new_x, new_y) not in visited:
                    new_color = background_image.get_at((new_x, new_y))
                    if new_color != WHITE:
                        if (new_x, new_y) not in dictionary or abs(dictionary[(x, y)] - dictionary[(new_x, new_y)]) > 1:
                            next_value = current_value + 1
                            queue.append((new_x, new_y, next_value))
                            visited.add((new_x, new_y))
    return dictionary, highest_value

class Ray:
    def __init__(self, position_x, position_y, angle, skipping_factor, background_image):
        self.x = position_x
        self.y = position_y
        self.angle = angle
        self.skipping_factor = skipping_factor
        self.length = 0
        self.background_image = background_image

    def start(self):
        self.angle_radians = math.radians(self.angle)
        self.ray_interval_x = self.skipping_factor * math.sin(self.angle_radians)
        self.ray_interval_y = self.skipping_factor * math.cos(self.angle_radians)

    def step(self):
        self.x += self.ray_interval_x
        self.y += self.ray_interval_y
        self.length += self.skipping_factor
        screen.set_at((round(self.x), round(self.y)), RED)

    def check_intersect(self):
        if self.background_image.get_at((round(self.x), round(self.y))) == WHITE or self.x < 0 or self.x > screen_width or self.y < 0 or self.y > screen_height:
            return True
        return False

    def get_length(self):
        return self.length
    
    def get_position(self):
        return [round(self.x - self.ray_interval_x), round(self.y - self.ray_interval_y)]

class Auto:
    def __init__(self, angle, position_x, position_y, friction, speed, colour, width, height, speed_factor, engine_factor,hoe_sneller_je_gaat_hoe_slomer_je_stuurt, steering_factor, brake_factor, backwards_driving_factor, ray_angles, player, rays, wasd, arrows, dictionary):
        self.keys = []
        self.acceleration = 0
        self.left_right = 0
        self.angle = angle
        self.force_f = 0
        self.speed = speed
        self.speed_x = 0
        self.speed_y = 0
        self.speed_modifier = 0
        self.position_x = position_x
        self.position_y = position_y

        self.colour = colour
        self.width = width
        self.height = height
        self.rect_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect_surf.fill(self.colour)
        
        self.player = player
        self.rays = rays
        self.wasd = wasd
        self.arrows = arrows
        self.ray_angles = ray_angles

        self.highscore = 0 #moet je nog maken
        self.laps = 0 #moet je nog maken
        self.dictionary = dictionary
        
        self.friction = friction
        self.speed_factor = speed_factor
        self.engine_factor = engine_factor
        self.steering_factor = steering_factor
        self.backwards_driving_factor = backwards_driving_factor
        self.brake_factor = brake_factor
        self.hoe_sneller_je_gaat_hoe_slomer_je_stuurt = hoe_sneller_je_gaat_hoe_slomer_je_stuurt

    def mechanica_bijwerken(self):
        if self.friction != 0:
            self.force_f = -self.friction * self.speed ** 2
        else:
            if self.acceleration > 0:
                if self.speed >= 0:
                    self.force_f = self.acceleration * self.engine_factor * self.speed_factor
                else:
                    self.force_f = self.acceleration * self.brake_factor * self.speed_factor
            else:
                if self.speed>= 0:
                    self.force_f = self.acceleration * self.brake_factor * self.speed_factor
                else:
                    self.force_f = self.acceleration * self.backwards_driving_factor * self.speed_factor
        if self.speed != 0:
            self.speed_modifier = min(1, self.hoe_sneller_je_gaat_hoe_slomer_je_stuurt / absolute_waarde(self.speed))
        self.angle += self.left_right * self.steering_factor * self.speed_modifier * self.speed_factor
        self.speed += self.force_f
        self.speed_x = self.speed * math.sin(math.radians(self.angle))
        self.speed_y = self.speed * math.cos(math.radians(self.angle))

    def positie_bijwerken(self):
        self.position_x += self.speed_x
        self.position_y += self.speed_y
        # if (round(self.position_x), round(self.position_y)) in self.dictionary:
        #     print(self.dictionary[round(self.position_x), round(self.position_y)])

    def print_auto(self, screen):
        rotated_surf = pygame.transform.rotate(self.rect_surf, self.angle)
        rotated_rect = rotated_surf.get_rect(center=(self.position_x, self.position_y))
        screen.blit(rotated_surf, rotated_rect.topleft)

    def verwerk_inputs_wasd(self):
        self.keys = pygame.key.get_pressed()
        self.left_right = 1 if self.keys[pygame.K_a] else -1 if self.keys[pygame.K_d] else 0
        self.acceleration = 1 if self.keys[pygame.K_w] else -1 if self.keys[pygame.K_s] else 0

    def verwerk_inputs_arrows(self):
        self.keys = pygame.key.get_pressed()
        self.left_right = 1 if self.keys[pygame.K_LEFT] else -1 if self.keys[pygame.K_RIGHT] else 0
        self.acceleration = 1 if self.keys[pygame.K_UP] else -1 if self.keys[pygame.K_DOWN] else 0

    def out_of_bounds(self, cars, background_image):
        if self.position_x < 0 or self.position_x > screen_width or self.position_y < 0 or self.position_y > screen_height or background_image.get_at((round(self.position_x), round(self.position_y))) == WHITE:
            cars.remove(self)

    def spawn_rays(self, background_image):
        return spawn_rays(self.ray_angles, self.angle, self.position_x, self.position_y, 5, background_image)

def create_player_car(arrows_or_wasd, dictionary, spawn_x, spawn_y, spawn_rotation):
    return Auto(spawn_rotation, spawn_x, spawn_y, 0, 0, (255, 255, 200), 20, 40, 0.2, 1, 4, 10, 2,0.5,[], player=True, rays=False, wasd=(arrows_or_wasd == 2), arrows=(arrows_or_wasd == 1), dictionary=dictionary)

def create_test_car(dictionary, spawn_x, spawn_y, spawn_rotation):
    return Auto(spawn_rotation, spawn_x, spawn_y, 0, 0, (155, 0, 200), 20, 40, 0.2, 1, 4, 20, 2,0.5,[-90,-45,[-140,-130,-100,-90, 90, 100, 130, 140],-30,[-140,-130,-100,-90, 90, 100, 130, 140],-15,[-140,-130,-100,-90, 90, 100, 130, 140], 0, [-140,-130,-100,-90, 90, 100, 130, 140],15,[-140,-130,-100,-90, 90, 100, 130, 140], 90], player=True, rays=True, wasd=True, arrows=True, dictionary=dictionary)

def load_track(screen_width, screen_height, track_info_dictionary):
    alle_track_file_namen_lijst = krijg_alle_tracks_in_directory()
    
    random_track_naam = random.choice(alle_track_file_namen_lijst)
    
    background_image = pygame.image.load(random_track_naam)
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))

    sys.setrecursionlimit(screen_width * screen_height)
    dictionary, farthest_point_on_track = position_mask(track_info_dictionary[random_track_naam][0], track_info_dictionary[random_track_naam][1], {}, 0, background_image, screen_width, screen_height)
    spawn_x, spawn_y, spawn_rotation = track_info_dictionary[random_track_naam][0], track_info_dictionary[random_track_naam][1], track_info_dictionary[random_track_naam][2]
    return background_image, dictionary, farthest_point_on_track, spawn_x, spawn_y, spawn_rotation


def next_frame(background_image):
    pygame.display.flip()
    pygame.time.Clock().tick(MAX_FPS)
    screen.blit(background_image, (0, 0))
    return background_image

def run_cars(cars, background_image):
    for car in cars:
        if car.left_right != 0 or car.acceleration != 0:
            car.mechanica_bijwerken()
        car.positie_bijwerken()
        car.print_auto(screen)
        if car.player:
            if car.wasd:
                car.verwerk_inputs_wasd()
            if car.arrows:
                car.verwerk_inputs_arrows()
        car.out_of_bounds(cars, background_image)
        if car.rays:
            car.spawn_rays(background_image)
    return cars

def left_over_inputs(event, cars, dictionary, spawn_x, spawn_y, spawn_rotation):
    if event.key == pygame.K_l:
        if any(isinstance(car, Auto) and car.arrows for car in cars):
            cars = [car for car in cars if not car.arrows]
        else:
            cars.append(create_player_car(1, dictionary, spawn_x, spawn_y, spawn_rotation))
    if event.key == pygame.K_t:
        if any(isinstance(car, Auto) and car.wasd for car in cars):
            cars = [car for car in cars if not car.wasd]
        else:
            cars.append(create_player_car(2, dictionary, spawn_x, spawn_y, spawn_rotation))
    if event.key == pygame.K_3:
        if any(isinstance(car, Auto) and car.rays for car in cars):
            cars = [car for car in cars if not car.rays]
        else:
            cars.append(create_test_car(dictionary, spawn_x, spawn_y, spawn_rotation))
    return cars

RED = (255, 0, 0, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

MAX_FPS = 60
screen_width = 1200
screen_height = 800

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))

def game(screen_width, screen_height):
    background_image, dictionary, farthest_point_on_track, spawn_x, spawn_y, spawn_rotation = load_track(screen_width, screen_height, track_info_dictionary)

    cars = []
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                cars = left_over_inputs(event, cars, dictionary, spawn_x, spawn_y, spawn_rotation)
            if event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.w, event.h
                screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
                background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
            if event.type == pygame.QUIT:
                running = False

        background_image = next_frame(background_image)
        cars = run_cars(cars, background_image)

        # If no player cars exist, create one at the spawn position
        

game(screen_width, screen_height)
pygame.quit()

