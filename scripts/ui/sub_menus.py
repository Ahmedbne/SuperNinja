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
class Lobby(SubMenuBase):
	def __init__(self, game_instance, server=None, is_host=False):
		super().__init__()

		self.server = server
		self.is_host = is_host

		self.game_instance = game_instance
		self.game_players = game_instance.entities
		self.connected_players = 0

		# UI Elements.
		self.title = Text("LOBBY", "retro gaming", (CENTER, 10), size=70, bold=True)
		self.sub_title = Text("----- Current Players: 1/4 -----", "retro gaming", (CENTER, 90), size=16)

		self.borders = [
			Border((CENTER, 125), (400, 55), color=AZURE4, line_width=2),
			Border((CENTER, 185), (400, 55), color=AZURE4, line_width=2),
			Border((CENTER, 245), (400, 55), color=AZURE4, line_width=2),
			Border((CENTER, 305), (400, 55), color=AZURE4, line_width=2)
		]

		self.player_names = [
			Text("EMPTY SLOT", "gamer", (CENTER, 120), size=50, color=DARK_SLATE_GRAY),
			Text("EMPTY SLOT", "gamer", (CENTER, 180), size=50, color=DARK_SLATE_GRAY),
			Text("EMPTY SLOT", "gamer", (CENTER, 240), size=50, color=DARK_SLATE_GRAY),
			Text("EMPTY SLOT", "gamer", (CENTER, 300), size=50, color=DARK_SLATE_GRAY)
		]

		self.player_status = [
			Text("--- Disconnected ---", "retro gaming", (CENTER, 160), size=14, color=DARK_SLATE_GRAY),
			Text("--- Disconnected ---", "retro gaming", (CENTER, 220), size=14, color=DARK_SLATE_GRAY),
			Text("--- Disconnected ---", "retro gaming", (CENTER, 280), size=14, color=DARK_SLATE_GRAY),
			Text("--- Disconnected ---", "retro gaming", (CENTER, 340), size=14, color=DARK_SLATE_GRAY)
		]

		self.status_text = Text("", "retro gaming", (CENTER, 365), size=13, color=pygame.Color("crimson"))

		if self.is_host:
			self.launch_button = Button("Launch", "gamer", (420, 390), (150, 60), on_click=self.launch, fade_out=False)
		else:
			self.back_button.pos = (CENTER, 390)
			self.back_button.display_text.pos = (CENTER, 390)


	def run(self):
		self.running = True
		print("Lobby running...")

		while self.running:
			self.running = self.game_instance.connected and not self.game_instance.running

			MenuBase.screen.blit(self.background, (0, 0))

			mx, my = pygame.mouse.get_pos()

			# Render title.
			self.title.render(MenuBase.screen)
			self.sub_title.set_text(f"----- Current Players: {self.connected_players}/{MAX_CLIENT_COUNT} -----")
			self.sub_title.render(MenuBase.screen)

			# Update and Render player slots.
			self.update_player_slots()
			for i in range(MAX_CLIENT_COUNT):
				self.borders[i].render(MenuBase.screen)
				self.player_names[i].render(MenuBase.screen)
				self.player_status[i].render(MenuBase.screen)

			# Render the status text.
			self.status_text.render(MenuBase.screen)

			# Render the launch button, only for the host lobby.
			if self.is_host:
				self.fade_alpha = self.launch_button.update(MenuBase.screen, self.fade_alpha, mx, my, self.click)
				self.launch_button.render(MenuBase.screen)

			# Render the back button.
			self.fade_alpha = self.back_button.update(MenuBase.screen, self.fade_alpha, mx, my, self.click)
			self.back_button.render(MenuBase.screen)

			# Handle the fade int effect.
			self.handle_fade_in(MenuBase.screen)

			# Handle events.
			self.click = False
			for event in pygame.event.get():
				self.handle_events(event)

			pygame.display.update()
			MenuBase.clock.tick(60)


	def update_player_slots(self):
		for i in range(MAX_CLIENT_COUNT):
			player = self.game_players[i]
			# Update player slots when new players joined.
			if player.initialized:
				self.borders[i].color = FOREST_GREEN if player.ready else FIRE_BRICK
				if self.player_names[i].text != player.player_name:
					self.player_names[i].set_text(player.player_name)
					self.player_names[i].color = DARK_GOLDEN_ROD if player.id == "main_player" else DARK_SLATE_GRAY
					self.player_status[i].set_text("--- Host ---" if player.client_id == "host" else "--- Connected ---")
					self.connected_players += 1
			
			# Or reset slots when players left.
			elif not player.initialized and self.player_names[i].text != "EMPTY SLOT":
				self.borders[i].color = AZURE4
				self.player_names[i].set_text("EMPTY SLOT")
				self.player_names[i].color = DARK_SLATE_GRAY
				self.player_status[i].set_text("--- Disconnected ---")
				self.connected_players -= 1


	def launch(self):
		if all(player.ready for player in self.game_players[:self.connected_players]):
			threading.Thread(target=self.game_instance.launch_session, args=(self.status_text, self.set_buttons_interactable)).start()
		else:
			self.status_text.set_text("[WAITING]: Players joining, can not launch.")


	def set_buttons_interactable(self, state):
		if self.back_button.interactable != state:
			self.back_button.interactable = bool(state)
			if self.is_host:
				self.launch_button.interactable = bool(state)


	def back_out(self):
		super().back_out()
		
		if self.is_host and self.server is not None:
			self.server.shutdown()
		else:
			self.game_instance.disconnect_from_server()


