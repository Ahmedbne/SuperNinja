import pygame
import socket
import sys
import re
import threading

from scripts.game import GameForHost, GameForClient
from scripts.utils import load_image, show_running_threads
from scripts.ui.ui_elements import Text, Button, InputField, Border
from scripts.socket.server import GameServer
from scripts.socket.client import MAX_CLIENT_COUNT


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
AZURE4 = pygame.Color("azure4")

FADE_DECREMENT = 15
DARK_SLATE_GRAY = pygame.Color("darkslategray")
DARK_GOLDEN_ROD = pygame.Color("darkgoldenrod")
FOREST_GREEN = pygame.Color("forestgreen")
FIRE_BRICK = pygame.Color("firebrick")

WIDTH, HEIGHT = 640, 480
CENTER = WIDTH / 2
IP_REGEX = r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$"
PORT_REGEX = r"^[1-9][0-9]{3,4}$"


class MenuBase:
	# Class variables.
	clock = pygame.time.Clock()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))

	outline_display = pygame.Surface((WIDTH / 2, HEIGHT / 2), pygame.SRCALPHA)  # Outline display
	normal_display = pygame.Surface((WIDTH / 2, HEIGHT / 2))  # Normal display
	fade_in = pygame.Surface((WIDTH, HEIGHT))


	# Load and scale the background image once as a class variable.
	background_image = pygame.transform.scale(load_image("background.png"), screen.get_size())

	def __init__(self):
		pygame.init()

		self.background = MenuBase.background_image
		self.fade_alpha = 0
		self.click = False
		self.running = True


	def handle_fade_in(self, surface):
		# Handle the fade-in effect.
		if self.fade_alpha > 0:
			if self.fade_alpha == 255:
				MenuBase.fade_in.fill(BLACK)
			self.fade_alpha -= FADE_DECREMENT
			MenuBase.fade_in.set_alpha(self.fade_alpha)
			surface.blit(MenuBase.fade_in, (0, 0))
			self.fade_alpha -= 15


	def handle_events(self, event):
		if event.type == pygame.QUIT:
			self.terminate()
		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:  # When the LMB is clicked.
				self.click = True


	def terminate(self):
		pygame.quit()
		sys.exit()


	def back_out(self):
		self.running = False


class SubMenuBase(MenuBase):
	def __init__(self):
		super().__init__()
		self.back_button = Button("Back", "gamer", (220, 390), (150, 60), on_click=self.back_out)


	def handle_events(self, event):
		super().handle_events(event)
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				self.back_button.click(MenuBase.screen, self.fade_alpha)


