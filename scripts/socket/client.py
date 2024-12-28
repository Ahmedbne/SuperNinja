# Importing necessary libraries
import socket  # For handling network communication
import threading  # For running send and receive operations concurrently
import traceback  # For detailed error reporting
import time 
import os 
import pygame 

# Constants
FORMAT = "utf-8"  # Encoding format used for sending and receiving messages
DISCONNECT_MESSAGE = "!leave"  # Command string for disconnecting from the server
MAX_CLIENT_COUNT = 4  # Maximum number of clients allowed
os.system("")  # Enables ANSI escape characters in the terminal for text formatting

# Custom exception for handling client disconnection scenarios
class ClientDisconnectException(Exception):
    pass

# ChatClient class for managing basic chat functionalities
class ChatClient:
    def __init__(self, ip="", port=5050, nickname="Default_Client"):
        """
        Initializes the chat client with a socket connection and basic configurations.
        :param ip: Server's IP address (default is empty)
        :param port: Server's port (default is 5050)
        :param nickname: Nickname for the client (default is "Default_Client")
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        self.server_ip = ip  # Store server IP
        self.port = port  # Store port number
        self.nickname = nickname  # Store client nickname
        self.running = True  # Flag to control the client's activity

    def receive(self):
        """Handles receiving messages from the server."""
        while self.running:
            try:
                # Receive a message from the server
                message = self.client_socket.recv(1024).decode(FORMAT)
                if message == "NICKNAME":
                    # If the server requests the client's nickname, send it
                    self.client_socket.send(self.nickname.encode(FORMAT))
                elif message == DISCONNECT_MESSAGE:
                    # If the server sends a disconnect message, raise a custom exception
                    raise ClientDisconnectException("You have disconnected from the server.")
                else:
                    # Print any other messages received from the server
                    print(message)
            except ClientDisconnectException as cde:
                # Handle disconnection gracefully
                self.running = False
                print(f"[DISCONNECTED]: {cde}")
                self.client_socket.close()
            except Exception:
                # Handle unexpected errors during message reception
                self.running = False
                print(f"[ERROR]: An unexpected error occurred!\n{traceback.format_exc()}")
                self.client_socket.close()

    def send(self):
        """Handles sending messages to the server."""
        while self.running:
            try:
                # Get user input for a message
                user_input = input().strip()
                message = f"{self.nickname}: {user_input}"  # Format the message
                print("\033[1A" + "\033[K", end='')  # Clear the terminal input line
                self.client_socket.send(message.encode(FORMAT))  # Send the message to the server
                
                if user_input == DISCONNECT_MESSAGE:
                    # If the user wants to disconnect, raise a custom exception
                    raise ClientDisconnectException("Closing connection...")
            except ClientDisconnectException as cde:
                # Handle graceful disconnection
                self.running = False
                print(f"[DISCONNECTING]: {cde}")
                self.client_socket.close()
            except Exception:
                # Handle unexpected errors during message sending
                self.running = False
                print(f"[ERROR]: An unexpected error occurred!\n{traceback.format_exc()}")
                self.client_socket.close()

    def send_manually(self, message):
        """
        Sends a pre-defined message to the server.
        :param message: The message to be sent
        """
        self.client_socket.send(str(message).encode(FORMAT))

    def connect(self):
        """Handles the connection to the server."""
        while True:
            # Prompt user to choose the connection scope (Local or Public)
            connection_scope = input("Enter connection scope (\"Local\" or \"Public\"): ").strip().lower()
            if connection_scope != "local" and connection_scope != "public":
                print("[ERROR]: Please enter a valid scope (\"Local\" or \"Public\").")
            else:
                break

        while True:
            try:
                # Prompt user for the server's IP address and port
                self.server_ip = input(f"Enter server's {connection_scope} IP: ").strip()
                self.port = int(input("Enter port number.\n(DEFAULT: '5050' for local connection, '5001' for public connection): ").strip())
                break
            except ValueError:
                # Handle invalid port inputs
                print("[ERROR]: Port number must be an integer.")

        try:
            # Prompt user for their nickname and connect to the server
            self.nickname = input("Choose a nickname: ")
            print(f"[CONNECTING]: Attempting to connect to Server ({self.server_ip} - port {self.port})...")
            self.client_socket.connect((self.server_ip, self.port))

            # Start threads for receiving and sending messages
            threading.Thread(target=self.receive).start()
            threading.Thread(target=self.send).start()
        except ConnectionRefusedError:
            # Handle connection refusal by the server
            print("[ERROR]: Connect failed, please check the server's IP and Port, then try again.")
            print(traceback.format_exc())
            self.client_socket.close()
        except (ConnectionResetError, ConnectionAbortedError):
            # Handle unexpected connection resets
            print("[ERROR]: Connection disrupted, possibly due to a forcibly closed session from the server side or network error.")
            print(traceback.format_exc())
            self.client_socket.close()


class GameClient(ChatClient):
	def __init__(self, game, client_id, ip="", port=5050, nickname="Default_Client"):
		"""
		Initializes the game client with a socket connection and game-specific configurations.
		:param game: The game instance to which this client is connected
		:param client_id: The unique identifier for this client
		:param ip: Server's IP address (default is empty)
		:param port: Server's port (default is 5050)
		:param nickname: Nickname for the client (default is "Default_Client")
		"""
		super().__init__(ip=ip, port=port, nickname=nickname)
		self.game = game
		self.entities = game.entities if hasattr(game, 'entities') else []  # A list of entities to update.
		self.tilemap = game.tilemap

		self.fps = 60
		self.clock = pygame.time.Clock()

		self.client_id = client_id  # Host, Client1, Client2,...
		# Initialize client index to -1 to indicate that the client has not yet been assigned an index by the server
		self.game_started = False  # Indicates whether the game has started; initially set to False
		self.client_index = -1  # Initialize client index to -1 to indicate that the client has not yet been assigned an index by the server
		self.game_started = False


	def disconnect(self):
		"""
		Handles the disconnection process from the server.
		Closes the socket connection and updates the running and game_started flags.
		"""
		if self.running:
			try:
				print(f"[DISCONNECTING]: You have disconnected from the server.")
				self.running = False
				self.game_started = False
				time.sleep(0.1)
				self.client_socket.send(DISCONNECT_MESSAGE.encode(FORMAT))
				self.client_socket.close()
			except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
				print("[CLOSED]: Server has shutdown.")



	def update_entity(self, sender_id, infos):
		"""
		Updates the state of an entity based on information received from the server.
		
		:param sender_id: The ID of the client sending the update.
		:param infos: A list containing the entity's state information.
		"""
		# Only update other clients' players and enemies.
		for entity in self.entities.copy():
			if entity.id == infos[0]:
				# [player_ID, last_movement[0], last_movement[1], pos[0], pos[1], dashing, jump, is_dead]
				if entity.type == "player":
					#print(f"{self.client_id} updating player: {entity.id}")
					entity.dashing = int(infos[5])
					entity.died = infos[7] == "True"
					entity.update(self.tilemap, movement=tuple(map(int, infos[1:3])), override_pos=tuple(map(float, infos[3:5])))
					if infos[6] == "True":
						entity.jump()
				
				elif entity.type == "enemy" and sender_id == "host":
					# [enemy_ID, walking, facing_left]
					dead = entity.update(self.tilemap, walking=int(infos[1]), facing_left=infos[2] == "True")
					if dead:
						self.entities.remove(entity)
				return


	def receive(self):
		super().receive()
		while self.running:
			try:
				message = self.client_socket.recv(1024).decode(FORMAT)
				#print(f"RECEIVED: {message}")
				message = message.split("|")[0]

				if message == DISCONNECT_MESSAGE:
					raise ClientDisconnectException("Disconnected by server.")
				elif message == "[NICKNAME]":
					self.client_socket.send(self.nickname.encode(FORMAT))
				elif message == "[CLIENT ID]" and self.client_id is not None:
					self.client_socket.send(self.client_id.encode(FORMAT))
				elif message == "[START GAME]":
					self.game.start_game()
				elif "PLAYER READY" in message:
					self.game.ready_for_launch()
				
				elif "NEW PLAYERS JOINED" in message:
					# [str(index), str(client_id), str(nicknames), str(client_ids)]
					player_infos = message.split(":")[1].split(";")
					index = int(player_infos[0])

					if self.client_index == -1:
						self.client_index = index
						self.client_id = player_infos[1]

					# [int(index), str(client_id), list(nicknames), list(client_ids)]
					self.game.on_connection_made(index, player_infos[2].split(","), player_infos[3].split(","))
					
					player_index = int(message.split(":")[1])
					if 0 <= player_index < len(self.entities):
						self.entities[player_index].unregister_client(player_index)
					else:
						print(f"[ERROR]: Invalid player index {player_index}.")
					self.entities[player_index].unregister_client(player_index)

				elif "RE_INITIALIZE" in message:
					# [str(index), str(client_id), str(nicknames), str(client_ids)]
					infos = message.split(":")[1].split(";")
					index = int(infos[0])
					self.client_index = index
					self.client_id = infos[1]
					self.game.on_connection_made(index, infos[2].split(","), infos[3].split(","), re_initialized=True)
				
				elif self.game_started:
					message_segments = message.split(";")
					sender_id = message_segments[0]
					for segment in message_segments[1:]:
						infos = segment.split(",")
						self.update_entity(sender_id, infos)

				self.game.disconnect_from_server()
				print(f"[DISCONNECTED]: Disconnected by server.")
		
			except ClientDisconnectException:
				self.game.disconnect_from_server()
			
			except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError):
				print("[INTERRUPTED]: Connection has been interrupted. Disconnecting...")
				self.game.disconnect_from_server()

			except Exception:
				print(f"[ERROR]: An unexpected error occurred!\n{traceback.format_exc()}")
				self.game.disconnect_from_server()


	def send(self):
		while self.running:
			try:
				if self.game_started:
					message = [self.client_id]
					
					# Clear the message list at the beginning of each iteration
					message.clear()
					
					# Send info of both entity types if this is the host.
					# Otherwise only send info of the corresponding client's player.
					# [player_ID, last_movement[0], last_movement[1], pos[0], pos[1], dashing, jump, is_dead]
					main_player = self.game.get_main_player()
					message.append(f"player_{self.client_index + 1}," +
									f"{main_player.last_movement[0]},{main_player.last_movement[1]}," +
									f"{main_player.pos[0]:.1f},{main_player.pos[1]:.1f}," +
									f"{main_player.dashing}," +
									f"{main_player.jumped}," +
									f"{main_player.died}")
		
					if self.client_id == "host":
						for entity in self.entities[4:]:
							# [enemy_ID, walking, facing_left]
							message.append(f"{entity.id},{entity.walking},{entity.facing_left}")
							if entity.is_dead:
								self.entities.remove(entity)
		
					# Add a delimeter between each message to avoid duplication.
					message = f"{';'.join(message)}|"
					#print(f"SENT: {message}")
					self.client_socket.send(message.encode(FORMAT))
		
				self.clock.tick(self.fps)

			except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, ConnectionResetError, AttributeError):
				print("[INTERRUPTED]: Connection has been interrupted. Disconnecting...")
				self.game.disconnect_from_server()

			except Exception:
				print(f"[ERROR]: An unexpected error occurred!\n{traceback.format_exc()}")
				self.game.disconnect_from_server()


	def connect(self):
		try:
			print(f"[CONNECTING]: Attempting to connect to Server ({self.server_ip} - port {self.port})...")
			self.client_socket.connect((self.server_ip, self.port))

			threading.Thread(target=self.receive).start()
			threading.Thread(target=self.send).start()

			return True
		
		except (ConnectionRefusedError, TimeoutError):
			print("[ERROR]: Connect failed, please check the server's IP and Port, then try again.")
			print(traceback.format_exc())
			self.game.disconnect_from_server()
		
		except (ConnectionResetError, ConnectionAbortedError):
			print("[ERROR]: Connection disrupted, possibly due to a forcibly closed session from the server side or network error.")
			print(traceback.format_exc())
			self.game.disconnect_from_server()


if __name__ == "__main__":
	ChatClient().connect()