import pygame
from classes.Animation import Animation
from classes.Camera import Camera
from classes.Collider import Collider
from classes.EntityCollider import EntityCollider
from classes.Input import Input
from classes.Pause import Pause
from entities.EntityBase import EntityBase
from traits.bounce import bounceTrait
from traits.go import GoTrait
from traits.jump import JumpTrait

pygame.init()

sprite_sheet = pygame.image.load("Pictures/Warrior_Sheet-Effect.png")


FRAME_WIDTH, FRAME_HEIGHT = 32, 32 


def load_animation_frames(row, num_frames):
    frames = []
    for i in range(num_frames):
        frame = sprite_sheet.subsurface((i * FRAME_WIDTH, row * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
        frames.append(frame)
    return frames

# Define character animations
character_sprites = {
    "idle": load_animation_frames(row=0, num_frames=4),    
    "run": load_animation_frames(row=1, num_frames=6),      
    "jump": load_animation_frames(row=2, num_frames=4),     
    "attack": load_animation_frames(row=3, num_frames=6),   
    "death": load_animation_frames(row=4, num_frames=6)     
}



small_animation = Animation(character_sprites["run"], character_sprites["idle"], character_sprites["jump"])
big_animation = Animation(character_sprites["run"], character_sprites["idle"], character_sprites["jump"])


class Player(EntityBase):
    def __init__(self, x, y, level, screen, dashboard, sound, gravity=0.8):
        super(Player, self).__init__(x, y, gravity)
        self.camera = Camera(self.rect, self)
        self.sound = sound
        self.input = Input(self)
        self.inAir = False
        self.inJump = False
        self.powerUpState = 0
        self.invincibilityFrames = 0
        self.current_animation = "idle"
        self.animation = small_animation  # Default to small character animation
        self.traits = {
            "jumpTrait": JumpTrait(self),
            "goTrait": GoTrait(small_animation, screen, self.camera, self),
            "bounceTrait": bounceTrait(self),
        }
        
        self.levelObj = level
        self.collision = Collider(self, level)
        self.screen = screen
        self.EntityCollider = EntityCollider(self)
        self.dashboard = dashboard
        self.restart = False
        self.pause = False
        self.pauseObj = Pause(screen, self, dashboard)

    def update(self):
        if self.invincibilityFrames > 0:
            self.invincibilityFrames -= 1

        # Update animation based on state
        self.update_animation_state()
        self.updateTraits()
        self.move()
        self.camera.move()
        self.applyGravity()
        self.checkEntityCollision()
        self.input.checkForInput()

    def update_animation_state(self):
        # Choose animation based on state
        if self.inJump:
            self.current_animation = "jump"
        elif self.traits["goTrait"].velocity != 0:
            self.current_animation = "run"
        else:
            self.current_animation = "idle"

        # Update animation frames based on power-up state
        if self.powerUpState == 0:
            self.traits['goTrait'].updateAnimation(small_animation)
        else:
            self.traits['goTrait'].updateAnimation(big_animation)

    def move(self):
        self.rect.y += self.vel.y
        self.collision.checkY()
        self.rect.x += self.vel.x
        self.collision.checkX()

    def checkEntityCollision(self):
        for ent in self.levelObj.entityList:
            collisionState = self.EntityCollider.check(ent)
            if collisionState.isColliding:
                if ent.type == "Item":
                    self._onCollisionWithItem(ent)
                elif ent.type == "Block":
                    self._onCollisionWithBlock(ent)
                elif ent.type == "Mob":
                    self._onCollisionWithMob(ent, collisionState)

    def _onCollisionWithItem(self, item):
        self.levelObj.entityList.remove(item)
        self.dashboard.points += 100
        self.dashboard.coins += 1
        self.sound.play_sfx(self.sound.coin)

    def _onCollisionWithBlock(self, block):
        if not block.triggered:
            self.dashboard.coins += 1
            self.sound.play_sfx(self.sound.bump)
        block.triggered = True

    def _onCollisionWithMob(self, mob, collisionState):
        if isinstance(mob, RedMushroom) and mob.alive:
            self.powerup(1)
            self.killEntity(mob)
            self.sound.play_sfx(self.sound.powerup)
        elif collisionState.isTop and (mob.alive or mob.bouncing):
            self.sound.play_sfx(self.sound.stomp)
            self.rect.bottom = mob.rect.top
            self.bounce()
            self.killEntity(mob)
        elif collisionState.isColliding and mob.alive and not self.invincibilityFrames:
            if self.powerUpState == 0:
                self.gameOver()
            elif self.powerUpState == 1:
                self.powerUpState = 0
                self.traits['goTrait'].updateAnimation(small_animation)
                x, y = self.rect.x, self.rect.y
                self.rect = pygame.Rect(x, y + 32, 32, 32)
                self.invincibilityFrames = 60
                self.sound.play_sfx(self.sound.pipe)

    def bounce(self):
        self.traits["bounceTrait"].jump = True

    def killEntity(self, ent):
        ent.alive = False
        self.dashboard.points += 100

    def gameOver(self):
        self.current_animation = "death"  # Set death animation
        srf = pygame.Surface((640, 480))
        srf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
        srf.set_alpha(128)
        self.sound.music_channel.stop()
        self.sound.music_channel.play(self.sound.death)

        for i in range(500, 20, -2):
            srf.fill((0, 0, 0))
            pygame.draw.circle(
                srf,
                (255, 255, 255),
                (int(self.camera.x + self.rect.x) + 16, self.rect.y + 16),
                i,
            )
            self.screen.blit(srf, (0, 0))
            pygame.display.update()
            self.input.checkForInput()
        while self.sound.music_channel.get_busy():
            pygame.display.update()
            self.input.checkForInput()
        self.restart = True

    def powerup(self, powerupID):
        if self.powerUpState == 0:
            if powerupID == 1:
                self.powerUpState = 1
                self.traits['goTrait'].updateAnimation(big_animation)
                self.rect = pygame.Rect(self.rect.x, self.rect.y - 32, 32, 64)  # Adjust for larger character
                self.invincibilityFrames = 20

