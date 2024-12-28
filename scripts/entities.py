import math
import random
import time
import pygame

from scripts.visual_effects import Particle, Projectile, Spark
from scripts.ui.ui_elements import Text


DARK_SLATE_GRAY = pygame.Color("darkslategray")
DARK_GOLDEN_ROD = pygame.Color("darkgoldenrod")














class Player(PhysicsEntity):
	def __init__(self, player_name, game, pos, size, id="", client_id="solo"):
		super().__init__(game, "player", pos, size, id=id, client_id=client_id)
		self.air_time = 0
		self.jump_count = 1
		self.dashing = 0

		self.wall_slide = False
		self.jumped = False
		self.died = False

		self.player_name = player_name
		self.name_text = Text(self.player_name, "gamer", self.pos, size=15, color=DARK_SLATE_GRAY)
		self.text_offset = (4, -15)
		self.initialized = False
		self.ready = False

		if self.client_id == "solo":
			self.set_action("idle")


	def __repr__(self):
		return (f"Player: [ID={self.id:<12}, Client_ID={self.client_id:<9}, Nickname={self.player_name:^20}, " +
				f"Initialized={self.initialized!s:<5}, Ready={self.ready!s:<5}]")


	def initialize_client(self, nickname, client_id, player_id, re_initialized=False):
		if not self.initialized or re_initialized:
			self.player_name = nickname
			self.client_id = client_id
			self.id = player_id
			self.name_text.set_text(self.player_name)
			
			if self.id == "main_player":
				self.name_text.color = DARK_GOLDEN_ROD
			
			self.initialized = True
			self.set_action("idle")



	def unregister_client(self, client_index):
		self.player_name = f"unnamed_player_{client_index + 1}"
		self.name_text.set_text(self.player_name)
		self.name_text.color = DARK_SLATE_GRAY
		self.id = f"player_{client_index + 1}"
		self.client_id = ""
		self.initialized = False
		self.ready = False


	def respawn(self, spawn_pos):
		self.pos = list(spawn_pos)
		self.died = False
		self.air_time = 0


	def render_name_tag(self, surface, offset=(0, 0)):
		self.name_text.render(surface, offset=offset)


	def update(self, tilemap, movement=(0, 0), override_pos=(0, 0)):
		super().update(tilemap, movement=movement)
		if tuple(self.pos) != override_pos and override_pos != (0, 0):
			self.pos = list(override_pos)

		self.name_text.update_pos((self.pos[0] + self.text_offset[0], self.pos[1] + self.text_offset[1]))

		# Handle air time and reset when grounded.
		self.air_time += 1
		if self.air_time > 120 and (self.id == "main_player" or self.client_id == "solo"):
			self.died = True
			self.game.dead += 1
			self.game.screenshake = max(self.game.screenshake, 16)

		if self.collisions["down"]:
			self.air_time = 0
			self.jump_count = 1
			self.jumped = False

		# Handle dashing.
		if abs(self.dashing) in {60, 50}:
			# A burst of particles at the beginning and end of a dash.
			for i in range(20):
				angle = random.random() * math.pi * 2
				speed = random.random() * 0.5 + 0.5
				p_velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
				self.game.particles.append(Particle(self.game, "dust", self.rect().center, velocity=p_velocity, start_frame=random.randint(0, 7)))
		
		if self.dashing > 0:  # Dash to the right.
			self.dashing = max(self.dashing - 1, 0)
		else:  # Dash to the left.
			self.dashing = min(self.dashing + 1, 0)
		
		# Generate trail particles.
		if abs(self.dashing) > 50:
			# Get the dash direction and multiply it with an amplitude.
			self.velocity[0] = abs(self.dashing) / self.dashing * 8
			# Make a sudden stop at the end of a dash.
			if abs(self.dashing) == 51:
				self.velocity[0] *= 0.1

			# A stream of particles following the dash.
			p_velocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
			self.game.particles.append(Particle(self.game, "dust", self.rect().center, velocity=p_velocity, start_frame=random.randint(0, 7)))

		# Gradually reduce horizontal movement to 0.
		if self.velocity[0] > 0:
			self.velocity[0] = max(self.velocity[0] - 0.1, 0)
		else:
			self.velocity[0] = min(self.velocity[0] + 0.1, 0)

		# Handle wall slide.
		self.wall_slide = False
		if (self.collisions["right"] or self.collisions["left"]) and self.air_time > 7:
			self.wall_slide = True
			self.jumped = False
			self.air_time = 8
			self.velocity[1] = min(self.velocity[1], 0.5)
			self.facing_left = self.collisions["left"]
			self.set_action("wall_slide")
			# Prioritize wall slide animation over the others, so we return here
			return

		# Handle animation transitions.
		if self.air_time > 7 and not self.wall_slide:
			self.set_action("jump")
		elif movement[0] != 0:
			self.set_action("run")
		else:
			self.set_action("idle")



	def render(self, outline_surface, offset=(0, 0)):
		if abs(self.dashing) <= 50:
			super().render(outline_surface, offset=offset)


	def jump(self):
		if not self.died:
			if self.wall_slide:
				self.jumped = True
				if self.facing_left and self.last_movement[0] < 0:
					self.velocity[0] = 2.5
					self.velocity[1] = -2.5
					self.air_time = 8
					self.jump_count = max(self.jump_count - 1, 0)
				elif not self.facing_left and self.last_movement[0] > 0:
					self.velocity[0] = -2.5
					self.velocity[1] = -2.5
					self.air_time = 8
					self.jump_count = max(self.jump_count - 1, 0)
			
			elif self.jump_count:
				self.jumped = True
				self.velocity[1] = -3
				self.jump_count -= 1
				self.air_time = 8

		return self.jumped

		
	def dash(self):
		if not self.dashing and not self.died:
			self.game.sounds["dash"].play()
			self.dashing = -60 if self.facing_left else 60
