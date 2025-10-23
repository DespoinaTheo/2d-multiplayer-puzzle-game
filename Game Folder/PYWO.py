import pygame
import os
import time
from squares import Square
from boxes import Box
import random
from random import randint
import sqlite3
from sqlite3 import Error

# initialization pygame & pygame.mixer
pygame.init()
pygame.mixer.init()

# variables initialization

# color definition
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE= (255, 105, 30)
YELLOW = (255, 255, 0)

# screen setup
screen_width = 1280
screen_heigh = 720
screen = pygame.display.set_mode((screen_width, screen_heigh))
pygame.display.set_caption("PYWO - Puzzle Your Way Out")

clock = pygame.time.Clock() # clock initialization

vel = 5 # players' velocity
# initial positions for Ms. Ghost
x1 = 0
y1 = screen_heigh-160 
# initial positions for Mr. Pumpkin
x2 = screen_width-160
y2 = screen_heigh-160

# images
bg = pygame.image.load('backround.jpg')
story_im = pygame.image.load('story_im.png')
info_im = pygame.image.load('info_im.jpg')
victory_im = pygame.image.load('victory_im.jpg')
game_over_im = pygame.image.load('game_over_im.jpg')
login_im = pygame.image.load('login_im.jpg')
menu_image = pygame.image.load('menu_im.png')

# fonts
font = pygame.font.Font(None, 36)
font2 = pygame.font.Font(None, 50)
font3 = pygame.font.Font(None, 25)

# music clips
pygame.mixer.music.load("backround_music.mp3")
pygame.mixer.music.play(loops=-1)
click_sound = pygame.mixer.Sound("correct_placement.mp3")
game_over_sound = pygame.mixer.Sound("witch.mp3")
gm_cnt = 0 # game over sound play times 

# Ms. Ghost animation
player1_right = pygame.image.load('ghost_right.png')
player1_left = pygame.image.load('ghost_left.png')
left1 = False # direction variable

# Mr. Pumpkin animation
player2_left = pygame.image.load('pumkin_left.png')
player2_right = pygame.image.load('pumkin_right.png')
right2 = False # direction variable

# menu buttons position base
button_x = 130
button_y = 620
button_width = 100
button_height = 50

story_pressed_cnt = 0 # story-button clicked times
info_pressed_cnt = 0 # info-button clicked times


# square sprites
all_sprites1 = pygame.sprite.Group()
all_sprites2 = pygame.sprite.Group()

# levels' setup
box = Box (YELLOW, 420, 270) # puzzle image outline
box.rect.center = (screen_width // 4, screen_heigh // 4)
puzzle = Box (YELLOW, 420, 270) # puzzle to solve outline
puzzle.rect.center = (3*screen_width // 4, screen_heigh // 4)

# menu and levels state initialization
menu_scene = True
level1 = False
level1_initialized = False
level2 = False
level2_initialized = False
level3 = False
level3_initialized = False

# victory/ game over state initialization
victory= False
game_over = False

# white square movement
carrying1 = False # if Ms. Ghost carries a square
carried_square1 = None
# orange square movement
carrying2 = False # if Mr. Pumpkin carries a square
carried_square2 = None

# time / score variables
level1_start_time = None 
level2_start_time = None 
level2_time_limit = 3.5 * 60 * 1000
level3_start_time = None 
level3_time_limit = 2.5 * 60 * 1000
# time initialization for calculations
time1=0
time2=0
time3=0

# db variables
name = None # team name (input_name() return)
entering_name = False
log_cnt=0 # login times


# functions' definition
# connect to data base function
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite was succesfull.")
    except Error as e:
        print(f"The Error '{e}' occured.")
    return connection

# dbase queries requests function
def create_query(connection, query, parameters=None):
    try:
        cursor = connection.cursor()
        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)
        connection.commit()
        print("Ερώτημα εκτελέστηκε με επιτυχία.")
    except Exception as e:
        print(f"Σφάλμα κατά την εκτέλεση του ερωτήματος: {e}")
    finally:
        cursor.close()

# function for creating a list with all the saved teams' scores
def fetch_scores(connection):
    try:
        cursor = connection.cursor()
        query = "SELECT Score FROM Teams;"
        cursor.execute(query)

        rows = cursor.fetchall()  
        
        scores_list = [row[0] for row in rows]
        
        return scores_list

    except Exception as e:
        print(f"Σφάλμα κατά την ανάκτηση των Scores: {e}")
    finally:
        cursor.close()

# asking from user to give a team name
def input_name(screen):
    input_active = True
    user_text = ""
    clock = pygame.time.Clock()

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False  # input ends with Enter
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]  # last character erasion
                else:
                    user_text += event.unicode  # letter addition

        # screen update
        screen.fill(BLACK)
        image_load(login_im)
        enter_text = font3.render("(Press Enter to apply your name)", True, WHITE)
        screen.blit(enter_text, (50, 650))
        text_surface = font2.render("Team Name: " + user_text, True, ORANGE)
        screen.blit(text_surface, (50, 50))
        pygame.display.flip()

        clock.tick(60)

    return user_text


# function for creating each level's puzzle
static_positions = None

def level_build(area, width, height, start_x, start_y):
    global static_positions

    if static_positions is None:
        global squares_list
        position_list = []
        for i in range(0, width, 50):  # each square requires width 50
            for j in range(0, height, 50):  # each square requires height 50
                position_list.append((i, j)) # possible positions for the squares in the puzzle 

        static_positions = []  # list for newly created squares (in the given puzzle)
        # for orange squares
        for i in range(area // 2):
            position = random.choice(position_list)
            position_list.remove(position)
            static_positions.append((position, ORANGE))

        # for white squares
        for i in range(area // 2):
            position = random.choice(position_list)
            position_list.remove(position)
            static_positions.append((position, WHITE))

    all_sprites1 = pygame.sprite.Group()  # white squares sprite
    all_sprites2 = pygame.sprite.Group()  # orange squares sprite

    squares_list = []  # List of all created squares (in the given puzzle)
    for pos, color in static_positions:
        square = Square(color, 50, 50)
        square.rect.x = start_x + pos[0]
        square.rect.y = start_y + pos[1]
        squares_list.append([square.rect.x, square.rect.y, color])
        if color == ORANGE:
            all_sprites2.add(square)
        else:
            all_sprites1.add(square)

    all_sprites = pygame.sprite.Group(all_sprites1, all_sprites2)
    all_sprites.update()
    all_sprites.draw(screen)

    return squares_list

# function that places a square to the right position
puzzle_squares=[] # list of squares that are correctly placed
def square_placement(carried_square):
    for elem in squares_list:
        if carried_square != None:
            # checks if a square is centered to right position
            if (carried_square.rect.x == elem[0] +screen_width//2 
                and carried_square.rect.y == elem[1]
                 and carried_square.color == elem[2]
                ):
                for square in puzzle_squares:
                    if square.rect.x == elem[0] + screen_width // 2 and square.rect.y == elem[1]:
                    # if the position is occupied nothing happens
                        return carried_square
                # if the poisition is empty a new square (with the correct) is drawn       
                square = Square(carried_square.color, 50, 50)
                square.rect.x = elem[0] + screen_width //2
                square.rect.y = elem[1]

                # sound that plays with every square's right placement
                click_sound.play()

                puzzle_squares.append(square)

                all_sprites1.add(square)
                # the carried square gets destroyed
                carried_square = None
                return carried_square
                    
    return carried_square

# victory check function
def check_victory(level):
    if len(puzzle_squares)== 40:
        level = False
    return level

# setup level function
def setup_level():
    box.drawOutline(screen) # given puzzle's outline
    puzzle.drawOutline(screen) # new puzzle's outline 
    squares_list = level_build(40,400,250, screen_width//4 -200, screen_heigh//4 -125)

# destroy function after level pass
def destroy_level():
    global puzzle_squares, all_sprites1, all_sprites2

    # empty sprite
    all_sprites1.empty()
    all_sprites2.empty()

    # empty lists
    puzzle_squares.clear()

    # empty static positions (if needed)
    global static_positions
    static_positions = None

# function to create the available puzzle squares
def available_squares():
    global all_sprites1, all_sprites2
    # orange squares
    all_sprites1 = pygame.sprite.Group()
    all_sprites2 = pygame.sprite.Group()
    for i in range(21):
        square = Square(ORANGE, 50, 50) 
        # random position
        rand_x = randint(135, screen_width -185)
        rand_y = randint(2*screen_heigh//3, screen_heigh-60)
        square.rect.x = rand_x
        square.rect.y = rand_y
        all_sprites2.add(square)
    # white squares
    for i in range(21):
        square = Square(WHITE, 50, 50) 
        # random position
        rand_x = randint(135, screen_width -185)
        rand_y = randint(2*screen_heigh//3, screen_heigh-60)
        square.rect.x = rand_x
        square.rect.y = rand_y
        all_sprites1.add(square)
    all_sprites = pygame.sprite.Group(all_sprites1, all_sprites2)
    all_sprites.update()
    all_sprites.draw(screen)

# function to create menu buttons
def draw_button():
    # story button
    pygame.draw.rect(screen, BLACK, (button_x, button_y, button_width, button_height))
    text = font2.render("Story", True, ORANGE)
    text_rect = text.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

    # info button
    pygame.draw.rect(screen, BLACK, (button_x + 315, button_y, button_width, button_height))
    text = font2.render("Info", True, WHITE)
    text_rect = text.get_rect(center=(button_x + 315 + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

    # login button
    pygame.draw.rect(screen, BLACK, (button_x + 640, button_y, button_width, button_height))
    text = font2.render("Login", True, WHITE)
    text_rect = text.get_rect(center=(button_x + 640 + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

    # play button
    pygame.draw.rect(screen, BLACK, (button_x + 950, button_y, button_width, button_height))
    text = font2.render("Play", True, ORANGE)
    text_rect = text.get_rect(center=(button_x + 950 + button_width // 2, button_y + button_height // 2))
    screen.blit(text, text_rect)

# create menu function
def menu():
    screen.blit(menu_image, (0, 0))
    draw_button()

# function to display images
def image_load(image):
    screen.blit(image, (0,0))


# data base creation
connection = create_connection("Login.sqlite3") # connect game to a data base

# the only needed tables are Team_name and Score
create_table = """
CREATE TABLE IF NOT EXISTS Teams(
Team_Name TEXT NOT NULL,
Score ΙΝΤ
);
"""
create_query(connection, create_table, None)



# main loop
done= False

while not done:

    screen.fill(BLACK)
    
    # levels' background
    screen.blit(bg, (0, 0))
    
    # animations blit
    if left1:
        screen.blit(player1_left,(x1, y1))
    else:
        screen.blit(player1_right,(x1, y1))
    if right2:
        screen.blit(player2_right,(x2, y2))
    else:
        screen.blit(player2_left,(x2, y2))
    
    
    # menu scene management when it's active
    if menu_scene:
        menu() # menu scene create
        for event in pygame.event.get():
            # exit game
            if event.type == pygame.QUIT: 
                done = True
            # if mouse click occurs
            if event.type == pygame.MOUSEBUTTONDOWN:  
                mouse_pos = pygame.mouse.get_pos()  # active mouse position
            # checks if mouse position is equal to any button's position
                if (button_x <= mouse_pos[0] <= button_x + button_width and
                    button_y <= mouse_pos[1] <= button_y + button_height):
                    story_pressed_cnt += 1 # click times counter

                elif (button_x + 315  <= mouse_pos[0] <= button_x + 315 + button_width and
                    button_y <= mouse_pos[1] <= button_y + button_height):
                    info_pressed_cnt += 1 # click times counter

                elif (button_x + 640  <= mouse_pos[0] <= button_x + 640 + button_width and
                    button_y <= mouse_pos[1] <= button_y + button_height):
                    entering_name = True # activates the login process

                elif (button_x + 950  <= mouse_pos[0] <= button_x + 950 + button_width and
                    button_y <= mouse_pos[1] <= button_y + button_height):
                    menu_scene = False # deactivates menu scene
                    level1 = True # activates level1 

        # checks if click counter for button "story" is odd or not
        if story_pressed_cnt % 2 !=0:
            image_load(story_im)
        # checks if click counter for button "info" is odd or not
        if info_pressed_cnt % 2 !=0:
            image_load(info_im)
        # login process
        if entering_name and log_cnt== 0:
            name = input_name(screen)
            entering_name = False  # when Enter is pressed input gets done
            
            # team is registered to dbase with the given name and a big default score value
            insert_teams = """
            INSERT INTO Teams(Team_Name, Score)
            values
            (?, ?)
            """
            values = (name, "100000")
            create_query(connection, insert_teams, values)
            log_cnt=1 # login can happen once
            

    if level1:
        setup_level()
        if level1_initialized == False:
            level1_start_time = pygame.time.get_ticks()
            available_squares()
            level1_initialized = True

        # checks for squares' placement for both players
        carried_square1= square_placement(carried_square1)
        carried_square2= square_placement(carried_square2)

        time1 = pygame.time.get_ticks() - level1_start_time # timer for level 1
        # level and score UI
        level1_text = font.render(f"LEVEL 1", True, ORANGE)
        time1_text = font.render(f"Time: {time1//1000}", True, WHITE)
        screen.blit(level1_text, (screen_width//2 -20, 10))
        screen.blit(time1_text, (10, 10))
        
        # if level 1 is completed it gets deactivated and level 2 gets activated
        if not check_victory(level1):
            level1 = False
            destroy_level()
            level2 = True


    if level2:
        setup_level()
        if level2_initialized == False:
            level2_start_time = pygame.time.get_ticks()
            available_squares()
            level2_initialized = True

        # checks for squares' placement for both players
        carried_square1= square_placement(carried_square1)
        carried_square2= square_placement(carried_square2)

        elapsed_time = pygame.time.get_ticks() - level2_start_time  # level 2 timer
        remaining_time = level2_time_limit - elapsed_time  # remaining time
        time2 = time1 + elapsed_time # total time so far
        
        # if level 2 is completed it gets deactivated and level 3 gets activated
        if not check_victory(level2):
            level2 = False
            destroy_level()
            level3 = True

        if remaining_time <= 0:  # if time is over -> game over
            game_over = True
        else:
            # level and score UI
            level2_text = font.render(f"LEVEL 2", True, ORANGE)
            time_left_text2 = font.render(f"Time Left: {remaining_time // 1000} sec", True, WHITE)
            time2_text = font.render(f"Time: {time2 // 1000} sec", True, WHITE)
            screen.blit(level2_text, (screen_width//2 -20, 10))
            screen.blit(time_left_text2, (10, 10))
            screen.blit(time2_text, (10, 50))

            
    if level3:
        setup_level()
        if level3_initialized == False:
            level3_start_time = pygame.time.get_ticks()
            available_squares()
            level3_initialized = True

        # checks for squares' placement for both players
        carried_square1= square_placement(carried_square1)
        carried_square2= square_placement(carried_square2)
        
        elapsed_time = pygame.time.get_ticks() - level3_start_time  # level 3 timer
        remaining_time = level3_time_limit - elapsed_time  # remaining time
        time3 = time2 + elapsed_time # total time so far = score

        # if level 3 is completed it gets deactivated and victory gets activated
        if not check_victory(level3):
            level3 = False
            destroy_level()
            victory =True    

        if remaining_time <= 0: # if time is over -> game over
            game_over = True
        else:
            # level and score UI
            level3_text = font.render(f"LEVEL 3", True, ORANGE)
            time_left_text3 = font.render(f"Time Left: {remaining_time // 1000} sec", True, WHITE)
            time3_text = font.render(f"Time: {time3// 1000} sec", True, WHITE)
            screen.blit(level3_text, (screen_width//2 -20, 10))  
            screen.blit(time3_text, (10, 50))
            screen.blit(time_left_text3, (10, 10))
        
    if  victory:
        image_load(victory_im)
        pygame.draw.rect(screen, BLACK, (0, 0, 300, 60))
        # score display
        score_text = font2.render(f"Score:{time3//1000}",True, WHITE)
        screen.blit(score_text, (75, 15))
        score = time3//1000
        # if team loged in it updates its score to dbase
        if name != None:
            update_score=f"UPDATE Teams set Score = '{score}' where Team_name = '{name}';"
            create_query(connection, update_score, None)

        # a list with all scores is created and sorted (min to max)
        score_list = fetch_scores(connection)
        score_list.sort()

        pygame.draw.rect(screen, BLACK, (1130, 0, 150, 500))
        top_10_text = font.render(f"Top Scores",True, WHITE)
        screen.blit(top_10_text, (1140, 430))
        
        # it displays all scores min to max (if there are less than 10 teams registered)
        if len(score_list) < 10:
            for i in range(len(score_list)):
                top_10_text = font.render(f"{i+1}. {score_list[i]}",True, ORANGE)
                screen.blit(top_10_text, (1160, 40*i +10))
        # it displays the top 10 scores min to max (if there are more than 10 teams registered)
        else:    
            for i in range(10):
                top_10_text = font.render(f"{i+1}. {score_list[i]}",True, ORANGE)
                screen.blit(top_10_text, (1160, 40*i +10))

    if game_over:
        image_load(game_over_im)
        destroy_level()
        pygame.mixer.music.stop() # background music stops
        if gm_cnt < 1: # game ove clip plays once
            game_over_sound.play() 
            gm_cnt+=1
        

    # Exit Game 
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            done = True
    # orange squares movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        for square in all_sprites2:
            if y2 > screen_heigh//2: # player can grab squares from the second half of y axis
                if square.rect.colliderect(pygame.Rect(x2, y2, 160, 160)): # it defines a collider box close to the player
                    carrying2= True # the square is carried by the player
                    carried_square2= square
                    break

    # white squares movement
    if keys[pygame.K_n]:
        for square in all_sprites1:
            if y1 > screen_heigh//2: # player can grab squares from the second half of y axis
                if square.rect.colliderect(pygame.Rect(x1, y1, 160, 160)):  # it defines a collider box close to the player
                    carrying1 = True # the square is carried by the player
                    carried_square1 = square
                    break  

    # player1 movement
    # movement in x axis
    if keys[pygame.K_LEFT] and x1 > 0: 
        x1-= vel
        left1 = True
        # it permits diagonal movement 
        if keys[pygame.K_UP] and y1 > 0: 
            y1 -= vel
        elif keys[pygame.K_DOWN] and y1 < screen_heigh - 160:
            y1 +=vel

    elif keys[pygame.K_RIGHT] and x1 < screen_width - 160:
        x1 += vel
        left1 = False
        # it permits diagonal movement 
        if keys[pygame.K_UP] and y1 > 0: 
            y1 -= vel
        elif keys[pygame.K_DOWN] and y1 < screen_heigh - 160:
            y1 +=vel
    # movement in y axis
    elif keys[pygame.K_UP] and y1 > 0:
        y1 -= vel
        # it permits diagonal movement
        if keys[pygame.K_LEFT] and x1 > 0:
            x1 -= vel
            left1 = True
        elif keys[pygame.K_RIGHT] and x1 < screen_heigh - 160:
            x1 +=vel
            left1 = False
            
    elif keys[pygame.K_DOWN] and y1 < screen_heigh - 160:
        y1 +=vel
        # it permits diagonal movement
        if keys[pygame.K_LEFT] and x1 > 0:
            x1 -= vel
            left1 = True
        elif keys[pygame.K_RIGHT] and x1 < screen_heigh - 160:
            x1 +=vel
            left1 = False
            

    # player2 movement
    # movement in x axis
    if keys[pygame.K_a] and x2 > 0: 
        x2-= vel
        right2 = False
        # it permits diagonal movement
        if keys[pygame.K_w] and y2 > 0:
            y2 -= vel
        elif keys[pygame.K_s] and y2 < screen_heigh - 160:
            y2 +=vel

    elif keys[pygame.K_d] and x2 < screen_width - 160:
        x2 += vel
        right2 = True
        # it permits diagonal movement
        if keys[pygame.K_w] and y2 > 0:
            y2 -= vel
        elif keys[pygame.K_s] and y2 < screen_heigh - 160:
            y2 +=vel
    
    # movement in y axis
    elif keys[pygame.K_w] and y2 > 0:
        y2 -= vel
        # it permits diagonal movement
        if keys[pygame.K_a] and x2 > 0:
            x2 -= vel
            right2 = False
        elif keys[pygame.K_d] and x2 < screen_heigh - 160:
            x2 +=vel
            right2 = True

    elif keys[pygame.K_s] and y2 < screen_heigh - 160:
        y2 +=vel
        # it permits diagonal movement
        if keys[pygame.K_a] and x2 > 0:
            x2 -= vel
            right2 = False
        elif keys[pygame.K_d] and x2 < screen_heigh - 160:
            x2 +=vel
            right2 = True
    
    # if a square is carried it moves along with the player (for both players)
    if carrying1 and carried_square1:
        carried_square1.rect.x = x1 + 25  # position adjust
        carried_square1.rect.y = y1 + 25

    if carrying2 and carried_square2:
        carried_square2.rect.x = x2 + 25  # position adjust
        carried_square2.rect.y = y2 + 25

    # all squares needed are drawn
    all_sprites1.draw(screen)
    all_sprites2.draw(screen)

    # screen update
    pygame.display.update()
    pygame.display.flip()
    clock.tick(60) # define fps

# Thank you :)
# Despoina & Nikos 