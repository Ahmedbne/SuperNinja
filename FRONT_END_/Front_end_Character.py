import pygame

# Initialisation de Pygame
pygame.init()

# Paramètres de la fenêtre du jeu
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Side-Scrolling Game")

# Définition des couleurs
WHITE = (255, 255, 255)

# Chargement des sprites
# Assurez-vous d'utiliser votre propre chemin d'accès pour charger les sprites.
sprite_sheet = pygame.image.load("red-hoodie-boy-game-sprites-side-scrolling-action-adventure-endless-runner-d-mobile-64180971-removebg-preview.png").convert_alpha()

# Classe pour le personnage
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames = []
        self.load_sprites()
        self.image = self.frames[0]  # Frame initiale
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.current_frame = 0
        self.frame_rate = 5
        self.counter = 0
        self.speed_x = 0
        self.speed_y = 0

    def load_sprites(self):
        # Découper les sprites à partir de l'image (taille et position à ajuster selon votre sprite)
        for i in range(4):  # Par exemple 4 frames d'animation pour chaque action
            frame = sprite_sheet.subsurface(pygame.Rect(i * 64, 0, 64, 64))  # Ajustez les dimensions ici
            self.frames.append(frame)

    def update(self):
        # Gérer les mouvements
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Gérer l'animation
        self.counter += 1
        if self.counter >= self.frame_rate:
            self.counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]

    def move_left(self):
        self.speed_x = -5

    def move_right(self):
        self.speed_x = 5

    def stop(self):
        self.speed_x = 0

# Création de l'objet joueur
player = Player()
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Boucle du jeu
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(30)  # Limite à 30 FPS
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Gérer les événements du clavier
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.move_left()
            if event.key == pygame.K_RIGHT:
                player.move_right()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.stop()

    # Mise à jour des sprites
    all_sprites.update()

    # Dessin de l'arrière-plan et des sprites
    screen.fill(WHITE)
    all_sprites.draw(screen)

    # Rafraîchir l'écran
    pygame.display.flip()

pygame.quit()
