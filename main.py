import pygame
import random
import os
import sys
#RU:4477878
#NOME: DIMAS ROCHA DA SILVA PEREIRA
# Inicialização do Pygame
pygame.init()

# Configurações do jogo
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # ms

# Configurações da tela
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird Clone")
clock = pygame.time.Clock()

# Função para lidar com caminhos de recursos
def resource_path(relative_path):
    
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Funções de carregamento de assets
def load_image(name, scale=1):
    
    try:
        img_path = os.path.join('assets', 'images', name)
        img = pygame.image.load(img_path).convert_alpha()
    except FileNotFoundError:
        img_path = resource_path(os.path.join('assets', 'images', name))
        img = pygame.image.load(img_path).convert_alpha()
    
    if scale != 1:
        new_size = (int(img.get_width() * scale), int(img.get_height() * scale))
        img = pygame.transform.scale(img, new_size)
    return img

def load_sound(name):
   
    try:
        sound_path = os.path.join('assets', 'sounds', name)
        sound = pygame.mixer.Sound(sound_path)
    except FileNotFoundError:
        sound_path = resource_path(os.path.join('assets', 'sounds', name))
        sound = pygame.mixer.Sound(sound_path)
    sound.set_volume(0.3)
    return sound

# Classes do jogo
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = load_image("bird.png", 0.05)
        self.rect = self.image.get_rect(center=(100, SCREEN_HEIGHT//2))
        self.movement = 0
        self.flap_sound = load_sound("wing.wav")
        self.can_flap = True
        
    def update(self):
        # Aplicar gravidade
        self.movement += GRAVITY
        self.rect.y += self.movement
        
        # Rotacionar o pássaro
        self.image = pygame.transform.rotate(load_image("bird.png", 0.05), -self.movement * 3)
        
        # Resetar o controle de batida quando estiver no chão
        if self.rect.bottom >= SCREEN_HEIGHT - 50:
            self.can_flap = True
        
    def flap(self):
        if self.can_flap:
            self.movement = FLAP_STRENGTH
            self.flap_sound.play()
            self.can_flap = False
    
    def reset_flap(self):
        self.can_flap = True

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, inverted=False):
        super().__init__()
        self.image = load_image("pipe.png", 0.5)
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(midbottom=(x, y - PIPE_GAP//2))
        else:
            self.rect = self.image.get_rect(midtop=(x, y + PIPE_GAP//2))
        
        # Criar um retângulo de colisão menor (hitbox)
        self.hitbox = self.rect.inflate(-60, -60)  # Reduz pixels de cada lado
        self.passed = False
        
    def update(self):
        self.rect.x -= 3
        self.hitbox.x -= 3  # Atualizar a hitbox junto com o retângulo visual
        if self.rect.right < 0:
            self.kill()
    
    def collided_with(self, sprite):
        return self.hitbox.colliderect(sprite.rect)

class Ground(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = load_image("ground.png", 0.5)
        self.rect = self.image.get_rect(midtop=(x, SCREEN_HEIGHT - 50))
        
    def update(self):
        self.rect.x -= 3
        if self.rect.right < SCREEN_WIDTH:
            self.rect.left = 0

# Funções auxiliares
def create_pipes():
    pipe_height = random.randint(200, 400)
    bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height)
    top_pipe = Pipe(SCREEN_WIDTH, pipe_height, True)
    return bottom_pipe, top_pipe

def display_score(score):
    score_surface = font.render(f"Score: {score}", True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(score_surface, score_rect)

def draw_hitboxes():
    for pipe in pipes:
        pygame.draw.rect(screen, (255, 0, 0), pipe.hitbox, 1)

# Inicialização do jogo
bg_surface = load_image("bg.png")
bg_surface = pygame.transform.scale(bg_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))

bird = Bird()
bird_group = pygame.sprite.Group(bird)

ground = Ground(0)
ground_group = pygame.sprite.Group(ground)

pipes = pygame.sprite.Group()
pipe_timer = pygame.USEREVENT + 1
pygame.time.set_timer(pipe_timer, PIPE_FREQUENCY)

font = pygame.font.SysFont('Arial', 30)
score = 0
point_sound = load_sound("point.wav")
game_active = True
show_hitboxes = False  # Variável para debug

# Loop principal do jogo
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and game_active:
                bird.flap()
            if event.key == pygame.K_SPACE and not game_active:
                # Reiniciar o jogo
                game_active = True
                pipes.empty()
                bird.rect.center = (100, SCREEN_HEIGHT//2)
                bird.movement = 0
                score = 0
            if event.key == pygame.K_h:  # Tecla H para mostrar hitboxes (debug)
                show_hitboxes = not show_hitboxes
                
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                bird.reset_flap()
                
        if event.type == pipe_timer and game_active:
            bottom_pipe, top_pipe = create_pipes()
            pipes.add(bottom_pipe)
            pipes.add(top_pipe)
    
    # Desenhar fundo
    screen.blit(bg_surface, (0, 0))
    
    if game_active:
        # Atualizar sprites
        bird_group.update()
        pipes.update()
        ground_group.update()
        
        # Verificar colisões com canos usando a hitbox
        for pipe in pipes:
            if pipe.collided_with(bird):
                game_active = False
        
        # Verificar colisão com o chão
        if bird.rect.bottom >= SCREEN_HEIGHT - 50:
            game_active = False
        
        # Verificar pontuação
        for pipe in pipes:
            if pipe.rect.right < bird.rect.left and not pipe.passed:
                pipe.passed = True
                score += 0.5  # 0.5 por cano (par completo = 1 ponto)
                point_sound.play()
        
        # Desenhar sprites
        pipes.draw(screen)
        ground_group.draw(screen)
        bird_group.draw(screen)
        
        # Mostrar hitboxes (debug)
        if show_hitboxes:
            draw_hitboxes()
        
        # Mostrar pontuação
        display_score(int(score))
    else:
        # Tela de game over
        game_over_surface = font.render("Game Over! " \
        "Press SPACE to Restart", True, (255, 255, 255))
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(game_over_surface, game_over_rect)
        display_score(int(score))
        
        # Instrução para debug
        debug_surface = font.render("Press H to toggle hitboxes", True, (255, 255, 255))
        debug_rect = debug_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        screen.blit(debug_surface, debug_rect)
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()