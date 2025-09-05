import pygame
import random
import numpy as np
import sounddevice as sd
import librosa
import sys

# === CONFIGURAÇÕES ===
WIDTH, HEIGHT = 1280, 720
PLAYER_SIZE = 80
OBJECT_SIZE = 40
FPS = 60

# === ÁUDIO ===
MUSIC_FILE = "musica.mp3"
y, sr = librosa.load(MUSIC_FILE, sr=None, mono=True)
music_pos = 0
chunk_size = 2048

stream = sd.OutputStream(samplerate=sr, channels=1, dtype='float32')
stream.start()

def get_audio_chunk():
    """Lê um pedaço da música e retorna volume normalizado"""
    global music_pos
    if music_pos + chunk_size >= len(y):
        return 0.0
    
    chunk = y[music_pos:music_pos+chunk_size]
    music_pos += chunk_size
    stream.write(chunk.astype(np.float32))
    
    volume = np.sqrt(np.mean(chunk**2))
    return volume * 10


# === FUNÇÃO GAME OVER ===
def game_over_screen(score):
    font_big = pygame.font.SysFont("Arial", 64, bold=True)
    font_small = pygame.font.SysFont("Arial", 32)
    
    while True:
        screen.blit(background, (0, 0))
        
        # Texto principal
        text_game_over = font_big.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text_game_over, (WIDTH//2 - text_game_over.get_width()//2, HEIGHT//3))
        
        text_score = font_small.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text_score, (WIDTH//2 - text_score.get_width()//2, HEIGHT//3 + 80))
        
        # Botões
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        # Botão Jogar Novamente
        retry_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2, 300, 60)
        pygame.draw.rect(screen, (0, 200, 0), retry_rect, border_radius=15)
        retry_text = font_small.render("Jogar Novamente", True, (255, 255, 255))
        screen.blit(retry_text, (retry_rect.centerx - retry_text.get_width()//2, retry_rect.centery - 15))
        
        # Botão Sair
        quit_rect = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 100, 300, 60)
        pygame.draw.rect(screen, (200, 0, 0), quit_rect, border_radius=15)
        quit_text = font_small.render("Sair", True, (255, 255, 255))
        screen.blit(quit_text, (quit_rect.centerx - quit_text.get_width()//2, quit_rect.centery - 15))
        
        # Verifica cliques
        if retry_rect.collidepoint(mouse) and click[0]:
            return True
        if quit_rect.collidepoint(mouse) and click[0]:
            pygame.quit()
            sys.exit()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        pygame.display.flip()
        clock.tick(30)


# === INICIALIZAÇÃO DO JOGO ===
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Beat Breaker Prototype")
clock = pygame.time.Clock()

# === CARREGAR IMAGENS ===
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

player_img = pygame.image.load("player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (PLAYER_SIZE, PLAYER_SIZE))
player_img_flipped = pygame.transform.flip(player_img, True, False)  # versão invertida

enemy_img = pygame.image.load("enemy.png").convert_alpha()
enemy_img = pygame.transform.scale(enemy_img, (int(OBJECT_SIZE * 0.7), OBJECT_SIZE))

font = pygame.font.SysFont("Arial", 32)

# === LOOP PRINCIPAL ===
while True:
    # Reset do jogo
    player = player_img.get_rect(center=(WIDTH//2, HEIGHT-100))
    objects = []
    score = 0
    direction = "right"
    running = True
    
    while running:
        screen.blit(background, (0, 0))

        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                stream.stop()
                stream.close()
                sys.exit()

        # Movimento do player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            player.x -= 10
            direction = "left"
        if keys[pygame.K_RIGHT] and player.x < WIDTH - PLAYER_SIZE:
            player.x += 10
            direction = "right"

        # Volume da música
        volume = get_audio_chunk()

        # Cria novos inimigos
        if random.random() < 0.05 + volume * 0.02:
            obj_rect = enemy_img.get_rect(
                center=(random.randint(OBJECT_SIZE//2, WIDTH-OBJECT_SIZE//2), 0)
            )
            objects.append(obj_rect)

        # Atualiza inimigos
        for obj in objects[:]:
            obj.y += int(2 + volume * 4)  # mais lento
            screen.blit(enemy_img, obj)

            if obj.colliderect(player):
                running = False
            
            if obj.y > HEIGHT:
                objects.remove(obj)
                score += 1

        # Desenha player (invertido conforme direção)
        if direction == "left":
            screen.blit(player_img_flipped, player)
        else:
            screen.blit(player_img, player)

        # HUD
        text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

        # Atualiza tela
        pygame.display.flip()
        clock.tick(FPS)
    
    # Tela de Game Over
    retry = game_over_screen(score)
    if not retry:
        break
