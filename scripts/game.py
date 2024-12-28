import pygame
import random
import sys
import os
import math
import time
import threading

from scripts.tilemap import Tilemap
from scripts.entities import Player, Enemy
from scripts.clouds import Clouds
from scripts.visual_effects import Particle, Spark
from scripts.animation import Animation
from scripts.utils import load_image, load_images, fade_out
from scripts.socket.client import GameClient, MAX_CLIENT_COUNT



class GameBase:
	def __init__(self, clock, screen, outline_display, normal_display):
		self.clock = clock
		self.screen = screen
		self.outline_display = outline_display  # Outline display
		self.normal_display = normal_display  # Normal display

		# Assets database for images, audio,...
		# Values are lists for multiple images.
		self.assets = {
			"clouds": load_images("clouds"),
			"decor": load_images("tiles/decor"),
			"grass": load_images("tiles/grass"),
			"large_decor": load_images("tiles/large_decor"),
			"stone": load_images("tiles/stone"),

			"player/idle": Animation(load_images("entities/player/idle"), image_duration=6),
			"player/run": Animation(load_images("entities/player/run"), image_duration=4),
			"player/jump": Animation(load_images("entities/player/jump")),
			"player/slide": Animation(load_images("entities/player/slide")),
			"player/wall_slide": Animation(load_images("entities/player/wall_slide")),

			"enemy/idle": Animation(load_images("entities/enemy/idle"), image_duration=6),
			"enemy/run": Animation(load_images("entities/enemy/run"), image_duration=4),
			
			"particle/leaf": Animation(load_images("particles/leaf"), image_duration=20, loop=False),
			"particle/dust": Animation(load_images("particles/dust"), image_duration=6, loop=False),
			
			"background": load_image("background.png"),
			"gun": load_image("gun.png"),
			"projectile": load_image("projectile.png")
		}

		self.sounds = {
			"ambience": pygame.mixer.Sound("assets/sfx/ambience.wav"),
			"dash": pygame.mixer.Sound("assets/sfx/dash.wav"),
			"hit": pygame.mixer.Sound("assets/sfx/hit.wav"),
			"jump": pygame.mixer.Sound("assets/sfx/jump.wav"),
			"shoot": pygame.mixer.Sound("assets/sfx/shoot.wav")
		}

		self.sounds["ambience"].set_volume(0.2)
		self.sounds["dash"].set_volume(0.35)
		self.sounds["hit"].set_volume(0.9)
		self.sounds["jump"].set_volume(0.6)
		self.sounds["shoot"].set_volume(0.45)

		self.clouds = Clouds(self.assets["clouds"], count=16)

		self.tilemap = Tilemap(self, 16)

		self.movement = [False, False]

		self.screenshake = 0

		self.level_id = 0
		self.max_level = len(os.listdir("assets/maps")) - 1
		self.running = False


	def load_level(self, id):
		self.tilemap.load(f"assets/maps/{id}.json")
		self.leaf_spawners = []
		for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
			self.leaf_spawners.append(pygame.Rect(tree.pos[0] + 4, tree.pos[1] + 4, 23, 13))

		self.particles = []
		self.projectiles = []
		self.sparks = []

		self.camera_scroll = [0, 0]
		self.dead = 0
		self.transition = -30


	def start_game(self):
		self.load_level(self.level_id)
		self.running = True


	def run(self):
		self.sounds["ambience"].play(-1)


	def render_terrain(self, render_scroll):
		# Spawn leaf particles.
		for rect in self.leaf_spawners:
			if random.random() * 49999 < rect.width * rect.height:
				pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
				velocity = [random.random() * 0.1 - 0.2, random.random() * 0.2 + 0.1]
				start_frame = random.randint(0, 17)
				self.particles.append(Particle(self, "leaf", pos, velocity, start_frame))

		# Render clouds.
		self.clouds.update()
		self.clouds.render(self.normal_display, offset=render_scroll)

		# Render the tilemap.
		self.tilemap.render(self.outline_display, offset=render_scroll)


	def render_effects(self, render_scroll):
		# Render sparks.
		for spark in self.sparks.copy():
			died = spark.update()
			spark.render(self.outline_display, offset=render_scroll)
			if died:
				self.sparks.remove(spark)

		# Render the outline for sprites.
		display_mask = pygame.mask.from_surface(self.outline_display)
		display_silhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
		for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
			self.normal_display.blit(display_silhouette, offset)

		# Render particles and remove expired ones.
		for particle in self.particles.copy():
			died = particle.update()
			particle.render(self.outline_display, offset=render_scroll)
			if particle.type == "leaf":
				particle.pos[0] += math.sin(particle.animation.frame * 0.035) * (random.random() * 0.3 + 0.2)
			if died:
				self.particles.remove(particle)


	def handle_level_transition(self):
		# Render the level transition effect.
		if self.transition:
			transition_surf = pygame.Surface(self.outline_display.get_size())
			pygame.draw.circle(transition_surf, (255, 255, 255), (self.outline_display.get_width() // 2,
								self.outline_display.get_height() // 2), (30 - abs(self.transition)) * 8)
			transition_surf.set_colorkey((255, 255, 255))
			self.outline_display.blit(transition_surf, (0, 0))


# The list of player serves as a template for each client.
PLAYERS = [
	Player("unnamed_player_1", None, (50, 50), (8, 15), id="player_1", client_id=""),
	Player("unnamed_player_2", None, (50, 50), (8, 15), id="player_2", client_id=""),
	Player("unnamed_player_3", None, (50, 50), (8, 15), id="player_3", client_id=""),
	Player("unnamed_player_4", None, (50, 50), (8, 15), id="player_4", client_id="")
]


class MultiplayerGameBase(GameBase):
	def initialize(self):
		# First 4 elements are players.
		self.entities = PLAYERS.copy()
		for player in self.entities:
			player.game = self

		self.level_id = 0
		self.player_index = -1
		self.client = None
		self.connected = False
		self.spawn_pos = (0, 0)


	def get_player_name(self):
		return self.client.nickname


	def get_main_player(self):
		return self.entities[self.player_index]


	def respawn(self):
		self.get_main_player().respawn(self.spawn_pos)
		self.particles.clear()
		self.projectiles.clear()
		self.sparks.clear()

		self.camera_scroll = [0, 0]
		self.dead = 0
		self.transition = -30


	def ready_for_launch(self):
		for i in range(MAX_CLIENT_COUNT):
			self.entities[i].ready = self.entities[i].initialized


	""" Initialize the all previously connected clients' players if the connection is made the frist time.
		Or if the server forces re-initialization.
		Otherwise, initialize just the newly connected client."""
	def on_connection_made(self, player_index, nicknames, client_ids, re_initialized=False):
		if not self.connected or re_initialized:
			self.player_index = player_index
			
			main_player = self.get_main_player()
			for i in range(MAX_CLIENT_COUNT):
				if i == self.player_index:
					main_player.initialize_client(nicknames[i], client_id=client_ids[i],
											player_id="main_player", re_initialized=re_initialized)
				elif i < len(nicknames):
					self.entities[i].initialize_client(nicknames[i], client_id=client_ids[i],
											player_id=f"player_{i + 1}", re_initialized=re_initialized)
				else:
					self.entities[i].unregister_client(i)
			self.connected = True
		else:
			self.entities[player_index].initialize_client(nicknames[player_index],
										client_id=client_ids[player_index], player_id=f"player_{player_index + 1}")
		
		print("\n".join(map(str, self.entities)), end="\n\n")


	def load_level(self, id):
		super().load_level(id)
		enemy_count = 1
		for spawner in self.tilemap.extract([("spawners", 0), ("spawners", 1)]):
			if spawner.variant == 0:
				# Set the spawn position for all 4 players at once.
				self.spawn_pos = tuple(spawner.pos)
				for i in range(MAX_CLIENT_COUNT):
					self.entities[i].pos = list(self.spawn_pos)
					self.entities[i].air_time = 0
			else:
				self.entities.append(Enemy(self, spawner.pos, (8, 15), id=f"enemy_{enemy_count}", client_id=self.client.client_id))
				enemy_count += 1


	def disconnect_from_server(self):
		self.running = False
		self.connected = False
		for i in range(MAX_CLIENT_COUNT):
			self.entities[i].unregister_client(i)
		self.client.disconnect()
		self.entities.clear()


	def run(self):
		super().run()
		self.client.game_started = True

