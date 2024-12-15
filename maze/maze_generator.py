import pygame
from random import choice, randint
import json
import time

RES = WIDTH, HEIGHT = 1400, 900
TILE = 50
cols, rows = WIDTH // TILE, HEIGHT // TILE
FPS = 60
first_move_made = False
NUM_STARS = 5  

pygame.init()
sc = pygame.display.set_mode(RES, pygame.RESIZABLE)
pygame.display.set_caption('Maze Generator')
clock = pygame.time.Clock()

player_image = pygame.image.load('vv.png')
player_image = pygame.transform.scale(player_image, (TILE - 10, TILE - 10))

try:
    star_image = pygame.image.load('roshen.png')
    star_image = pygame.transform.scale(star_image, (TILE - 20, TILE - 20))
    use_star_image = True
except FileNotFoundError:
    print("No file 'roshen.png' found, using fallback method for drawing stars.")
    use_star_image = False

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw_current_cell(self):
        x, y = self.x * TILE, self.y * TILE
        pygame.draw.rect(sc, pygame.Color('#f70067'), (x + 2, y + 2, TILE - 2, TILE - 2))

    def draw(self):
        x, y = self.x * TILE, self.y * TILE
        if self.visited:
            pygame.draw.rect(sc, pygame.Color('#3eb489'), (x, y, TILE, TILE))
        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('#030659'), (x, y), (x + TILE, y), 6)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('#030659'), (x + TILE, y), (x + TILE, y + TILE), 6)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('#030659'), (x + TILE, y + TILE), (x, y + TILE), 6)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('#030659'), (x, y + TILE), (x, y), 6)

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x >= cols or y < 0 or y >= rows:
            return False
        return grid_cells[find_index(x, y)]

    def check_neighbors(self):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False

def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

def reset_game_state():
    global grid_cells, current_cell, stack, colors, color, player_pos, start_time, stars, collected_stars, first_move_made, game_won, valid_moves, total_moves, move_count, maze_generated
    grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
    current_cell = grid_cells[0]
    stack = []
    colors, color = [], 40
    player_pos = [0, 0]
    start_time = None
    stars = []  
    collected_stars = 0
    first_move_made = False
    game_won = False
    valid_moves = 0
    total_moves = 0
    move_count = 0
    maze_generated = False  

def generate_stars():
    star_positions = []
    max_attempts = 100  
    attempts = 0

    while len(star_positions) < NUM_STARS and attempts < max_attempts:
        x, y = randint(0, cols - 1), randint(0, rows - 1)
        if (x, y) != (0, 0) and (x, y) != (cols - 1, rows - 1) and is_valid_star_position(x, y, star_positions):
            star_positions.append((x, y))
        attempts += 1

    return star_positions

def is_valid_star_position(x, y, star_positions):
    cell = grid_cells[x + y * cols]
    if any(cell.walls.values()):  
        return False
    for star_x, star_y in star_positions:
        if abs(x - star_x) <= 1 and abs(y - star_y) <= 1:  
            return False
    return True

reset_game_state()

def draw_player(x, y):
    sc.blit(player_image, (x * TILE + 5, y * TILE + 5))

def draw_end_point():
    end_x, end_y = cols - 1, rows - 1
    pygame.draw.rect(sc, pygame.Color('#00FF00'), (end_x * TILE + 5, end_y * TILE + 5, TILE - 10, TILE - 10))

def draw_stars():
    for x, y in stars:
        if use_star_image:
            sc.blit(star_image, (x * TILE + 15, y * TILE + 15))
        else:
            pygame.draw.circle(sc, pygame.Color('#FFD700'), (x * TILE + TILE // 2, y * TILE + TILE // 2), TILE // 4)

def draw_game_stats(elapsed_time, collected_stars, accuracy, move_count):
    font = pygame.font.Font(None, 36)
    timer_text = font.render(f'Time: {elapsed_time:.2f}s', True, pygame.Color('black'))
    sc.blit(timer_text, (WIDTH - 200, 20))

    star_text = font.render(f'Chocolates: {collected_stars}/5', True, pygame.Color('black'))
    sc.blit(star_text, (WIDTH - 200, 60))
    
    accuracy_text = font.render(f'Accuracy: {accuracy:.2f}%', True, pygame.Color('black'))
    sc.blit(accuracy_text, (WIDTH - 200, 100))
    
    moves_text = font.render(f'Moves: {move_count}', True, pygame.Color('black'))
    sc.blit(moves_text, (WIDTH - 200, 140))

def is_move_valid(x, y, direction):
    cell = grid_cells[x + y * cols]
    if direction == 'top' and not cell.walls['top']:
        return True
    if direction == 'right' and not cell.walls['right']:
        return True
    if direction == 'bottom' and not cell.walls['bottom']:
        return True
    if direction == 'left' and not cell.walls['left']:
        return True
    return False

def draw_statistics_window(elapsed_time, collected_stars, accuracy, move_count):
    font = pygame.font.Font(None, 50)
    window_color = pygame.Color('#FFFFFF')
    window_width, window_height = 420, 360
    window_rect = pygame.Rect(WIDTH // 2 - window_width // 2, HEIGHT // 2 - window_height // 2, window_width, window_height)
    pygame.draw.rect(sc, window_color, window_rect)

    text = font.render('Level Complete!', True, pygame.Color('green'))  
    sc.blit(text, (WIDTH // 2 - 140, HEIGHT // 2 - 130))

    time_text = font.render(f'Time: {elapsed_time:.2f}s', True, pygame.Color('black'))
    sc.blit(time_text, (WIDTH // 2 - 140, HEIGHT // 2 - 80))

    star_text = font.render(f'Chocolates: {collected_stars}/5', True, pygame.Color('black'))
    sc.blit(star_text, (WIDTH // 2 - 140, HEIGHT // 2 - 30))
    
    accuracy_text = font.render(f'Accuracy: {accuracy:.2f}%', True, pygame.Color('black'))
    sc.blit(accuracy_text, (WIDTH // 2 - 140, HEIGHT // 2 + 20))
    
    moves_text = font.render(f'Moves: {move_count}', True, pygame.Color('black'))
    sc.blit(moves_text, (WIDTH // 2 - 140, HEIGHT // 2 + 70))

    button_rects = []
    button_texts = ['Play Again', 'Exit']
    button_colors = [pygame.Color('green'), pygame.Color('red')]
    for i, (button_text, button_color) in enumerate(zip(button_texts, button_colors)):
        if i == 0:
            button_width = 180
            button_x = WIDTH // 2 - window_width // 2 + 20
        else:
            button_width = 160
            button_x = WIDTH // 2 - window_width // 2 + 210 + 40
        button_rect = pygame.Rect(button_x, HEIGHT // 2 + 130, button_width, 40)
        pygame.draw.rect(sc, button_color, button_rect)
        text = font.render(button_text, True, pygame.Color('black'))
        text_rect = text.get_rect(center=button_rect.center)
        sc.blit(text, text_rect)
        button_rects.append(button_rect)

    return button_rects

def handle_statistics_buttons(button_rects):
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    for i, rect in enumerate(button_rects):
        if rect.collidepoint(mouse_pos) and mouse_click[0]:
            return i
    return None

def draw_fireworks():
    fireworks_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  
    fireworks_particles = []  
    for _ in range(100):  
        x = randint(WIDTH - 100, WIDTH)  
        y = randint(HEIGHT - 100, HEIGHT)  
        radius = randint(2, 8)  
        color = choice(fireworks_colors)  
        fireworks_particles.append((x, y, radius, color))  

    for particle in fireworks_particles:
        x, y, radius, color = particle
        pygame.draw.circle(sc, color, (x, y), radius)  

def check_end_condition():
    global game_won, start_time
    end_x, end_y = cols - 1, rows - 1
    if player_pos == [end_x, end_y]:
        game_won = True
        elapsed_time = time.time() - start_time
        accuracy = (valid_moves / total_moves) * 100 if total_moves > 0 else 100
        draw_statistics_window(elapsed_time, collected_stars, accuracy, move_count)
        draw_fireworks()  

fullscreen = False
game_won = False
fullscreen_toggle_pressed = False

while True:
    sc.fill(pygame.Color('#a6d5e2'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game_state()
            elif event.key == pygame.K_F11:
                fullscreen = not fullscreen
                fullscreen_toggle_pressed = True
                if fullscreen:
                    sc = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    sc = pygame.display.set_mode(RES, pygame.RESIZABLE)
            else:
                if not game_won:
                    if not first_move_made:
                        start_time = time.time()
                        first_move_made = True
                    total_moves += 1
                    valid_move = False
                    if (event.key == pygame.K_w or event.key == pygame.K_UP) and player_pos[1] > 0 and is_move_valid(player_pos[0], player_pos[1], 'top'):
                        player_pos[1] -= 1
                        valid_move = True
                    elif (event.key == pygame.K_s or event.key == pygame.K_DOWN) and player_pos[1] < rows - 1 and is_move_valid(player_pos[0], player_pos[1], 'bottom'):
                        player_pos[1] += 1
                        valid_move = True
                    elif (event.key == pygame.K_a or event.key == pygame.K_LEFT) and player_pos[0] > 0 and is_move_valid(player_pos[0], player_pos[1], 'left'):
                        player_pos[0] -= 1
                        valid_move = True
                    elif (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and player_pos[0] < cols - 1 and is_move_valid(player_pos[0], player_pos[1], 'right'):
                        player_pos[0] += 1
                        valid_move = True
                    if valid_move:
                        valid_moves += 1
                        move_count += 1
        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            sc = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            cols, rows = (WIDTH - 200) // TILE, HEIGHT // TILE
            reset_game_state()


    if not fullscreen_toggle_pressed:
        if not game_won:
            [cell.draw() for cell in grid_cells]
            current_cell.visited = True
            current_cell.draw_current_cell()
            [pygame.draw.rect(sc, colors[i], (cell.x * TILE + 2, cell.y * TILE + 2, TILE - 1, TILE - 1), border_radius=8) for i, cell in enumerate(stack)]

            next_cell = current_cell.check_neighbors()
            if next_cell:
                next_cell.visited = True
                stack.append(current_cell)
                colors.append((min(color, 255), 0, 103))
                color += 1
                remove_walls(current_cell, next_cell)
                current_cell = next_cell
            elif stack:
                current_cell = stack.pop()
            else:
                maze_generated = True  
                if not stars:  
                    stars = generate_stars()  

            if maze_generated:
                draw_player(player_pos[0], player_pos[1])
                draw_end_point()
                draw_stars()

            if first_move_made:
                elapsed_time = time.time() - start_time
                accuracy = (valid_moves / total_moves) * 100 if total_moves > 0 else 100
                draw_game_stats(elapsed_time, collected_stars, accuracy, move_count)

            maze_array = [{'x': cell.x, 'y': cell.y, 'walls': cell.walls} for cell in grid_cells]
            with open('walls_data.json', 'w') as json_file:
                json.dump(maze_array, json_file)

            if (player_pos[0], player_pos[1]) in stars:
                stars.remove((player_pos[0], player_pos[1]))
                collected_stars += 1

            check_end_condition()
        else:
            accuracy = (valid_moves / total_moves) * 100 if total_moves > 0 else 100
            button_rects = draw_statistics_window(elapsed_time, collected_stars, accuracy, move_count)
            button_clicked = handle_statistics_buttons(button_rects)
            if button_clicked is not None:
                if button_clicked == 0:
                    reset_game_state()
                    game_won = False
                elif button_clicked == 1:
                    pygame.quit()
                    exit()

    fullscreen_toggle_pressed = False
    pygame.display.flip()
    clock.tick(FPS)
