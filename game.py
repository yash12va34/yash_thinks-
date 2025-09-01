# Asteroid Dodger (≈100 lines)
# Controls: Arrow keys/WASD to move, Space to shoot, Esc to quit
import pygame, random, sys
pygame.init()
W, H = 480, 720
WIN = pygame.display.set_mode((W, H))
pygame.display.set_caption("Asteroid Dodger")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 28)

# Colors
BG = (15, 12, 30)
SHIP_C = (80, 200, 255)
ROCK_C = (240, 90, 90)
BULLET_C = (250, 250, 170)
STAR_C = (200, 200, 255)

# Helpers
def draw_ship(x, y):
    # Triangle ship
    pts = [(x, y-12), (x-10, y+10), (x+10, y+10)]
    pygame.draw.polygon(WIN, SHIP_C, pts)

def new_rock():
    x = random.randint(15, W-15)
    s = random.randint(14, 26)
    sp = random.uniform(2.0, 5.0)
    return pygame.Rect(x, -40, s, s), sp

def new_star():
    return [random.randint(0, W), random.randint(0, H), random.uniform(0.5, 1.8)]

def text(t, x, y, c=(230,230,240)):
    WIN.blit(FONT.render(t, True, c), (x, y))

def clamp(v, lo, hi): return max(lo, min(hi, v))

# Game state
ship_x, ship_y = W//2, H-70
ship_spd = 5
bullets = []      # rects
rocks = []        # (rect, speed)
stars = [new_star() for _ in range(80)]
shoot_cd, shoot_delay = 0, 140  # ms
spawn_timer, spawn_delay = 0, 500
score, lives = 0, 3
running, invuln, inv_timer = True, False, 0
level_timer = 0
shake = 0

def reset():
    global bullets, rocks, lives, invuln, inv_timer, ship_x, ship_y, shake
    bullets.clear(); rocks.clear()
    ship_x, ship_y = W//2, H-70
    invuln, inv_timer = True, 1200
    shake = 8

while running:
    dt = clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    # Input
    keys = pygame.key.get_pressed()
    dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
    dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
    ship_x = clamp(ship_x + dx*ship_spd, 15, W-15)
    ship_y = clamp(ship_y + dy*ship_spd, 40, H-30)

    # Shooting
    shoot_cd = max(0, shoot_cd - dt)
    if (keys[pygame.K_SPACE]) and shoot_cd == 0:
        bullets.append(pygame.Rect(ship_x-3, ship_y-16, 6, 14))
        shoot_cd = shoot_delay

    # Stars parallax
    for s in stars:
        s[1] += s[2]*2
        if s[1] > H: s[:] = [random.randint(0, W), 0, random.uniform(0.5, 1.8)]

    # Spawn rocks (faster over time)
    spawn_timer += dt
    level_timer += dt
    spawn_rate = max(150, spawn_delay - level_timer//6)  # ramp difficulty
    if spawn_timer >= spawn_rate:
        rocks.append(new_rock())
        spawn_timer = 0

    # Update bullets
    bullets = [b for b in bullets if b.y > -20]
    for b in bullets: b.y -= 9

    # Update rocks
    for i, (r, sp) in enumerate(rocks):
        r.y += sp
    rocks = [(r, sp) for (r, sp) in rocks if r.y < H+40]

    # Collisions: bullets vs rocks
    kill = []
    for b in bullets:
        for j, (r, _) in enumerate(rocks):
            if b.colliderect(r):
                kill.append((b, j))
                score += 10
                shake = min(10, shake + 2)
                break
    for b, j in kill[::-1]:
        if b in bullets: bullets.remove(b)
        if 0 <= j < len(rocks): rocks.pop(j)

    # Collisions: ship vs rocks
    ship_hitbox = pygame.Rect(ship_x-10, ship_y-10, 20, 20)
    if not invuln:
        for r, _ in rocks:
            if ship_hitbox.colliderect(r):
                lives -= 1
                reset()
                break
    else:
        inv_timer -= dt
        if inv_timer <= 0: invuln = False

    # Game over
    if lives <= 0:
        WIN.fill((5, 0, 10))
        text("GAME OVER", W//2-70, H//2-20)
        text(f"Score: {score}", W//2-45, H//2+10)
        text("Press R to restart or Esc to quit", W//2-155, H//2+40, (180,180,200))
        pygame.display.flip()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            score, lives, level_timer = 0, 3, 0
            reset()
        continue

    # Camera shake
    ox = random.randint(-shake, shake) if shake>0 else 0
    oy = random.randint(-shake, shake) if shake>0 else 0
    shake = max(0, shake-1)

    # Draw
    WIN.fill(BG)
    # stars
    for s in stars:
        WIN.fill(STAR_C, (int(s[0]+ox)%W, int(s[1]+oy)%H, 2, 2))
    # rocks
    for r, _ in rocks:
        pygame.draw.rect(WIN, ROCK_C, r.move(ox, oy), border_radius=4)
    # bullets
    for b in bullets:
        pygame.draw.rect(WIN, BULLET_C, b.move(ox, oy), border_radius=2)
    # ship (blink while invulnerable)
    if not invuln or (pygame.time.get_ticks()//120)%2==0:
        draw_ship(ship_x+ox, ship_y+oy)

    # HUD
    text(f"Score: {score}", 10, 10)
    text(f"Lives: {lives}", 10, 36)
    text("Esc: Quit  Space: Shoot  Arrows/WASD: Move", 10, H-28, (170,190,220))
    pygame.display.flip()
