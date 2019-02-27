import os
import random
import sys

import matplotlib.pyplot as plt
import numpy as np
import pygame
import yaml
from pylab import sin
import pandas as pd
import statsmodels.api as sm
from scipy import stats

# df = pd.DataFrame({"Passed": [0, 1, 1, 0],
#                    "Eye": ["L", "R", "L", "R"]})
#
# model = sm.formula.glm("Passed ~ Eye",
#                        family=sm.families.Binomial(),
#                        data=df).fit()
# print(model.summary())

# DEFINE CONSTANT VARIABLES

NUMCIRCLES = 10
WIDTH = 240
HEIGHT = 240
MINSCORE = 50


# DEFINE CONSTANT FUNCTIONS

def clear_screen():
    """
    Clears the screen by filling with background
    """
    game.screen.blit(background, (0, 0))


def update():
    """
    Updates screen
    """
    pygame.display.flip()


def update_config():
    """
    Saves current config to file
    """
    with open('data/config', "w") as save_config:
        yaml.dump(config, save_config)


def update_buttons(left, right):
    """
    Updates the text displayed for each button instruction
    :param left: text to be displayed for the left button
    :param right: text to be displayed for the right button
    """
    right_text_message = right + " >"
    left_text_message = "< " + left

    right_text = font_normal.render(right_text_message, True, color_black)
    left_text = font_normal.render(left_text_message, True, color_black)
    game.screen.blit(right_text, (game.w * 9.8 // 10 - right_text.get_width(), game.h * 9.5 // 10))
    game.screen.blit(left_text, (game.w * .2 // 10, game.h * 9.5 // 10))


class Game:
    """
    Class container for important fields and initializations
    """
    state = "Start"
    w = 0
    h = 0
    clock = None

    def __init__(self):
        pygame.init()
        size = self.w, self.h = WIDTH, HEIGHT
        pygame.display.set_caption("KalEYEdoscope")
        self.screen = pygame.display.set_mode(size, pygame.NOFRAME)
        self.clock = pygame.time.Clock()


# INITIALIZATION

# Centers window on screen

os.environ['SDL_VIDEO_CENTERED'] = '1'

# Load frequently used variables

game = Game()
config = yaml.safe_load(open("data/config"))

# Images
background = pygame.image.load("images/table_background_800.jpg")

# Fonts
font_title = pygame.font.Font(None, 30)
font_subtitle = pygame.font.Font(None, 18)
font_normal = pygame.font.Font(None, 20)

# Spacings
padding = 2

# Colors
color_black = (0, 0, 0)
color_gray = (100, 100, 100)


# ACTIVITY FUNCTIONS

def start():
    """"
    Main screen event.
    """
    clear_screen()
    text = font_title.render("Welcome to your", True, color_black)
    text2 = font_title.render("KalEYEdoscope", True, color_black)
    for x in range(0, game.h // 2 + text.get_height() // 2, 4):
        clear_screen()
        game.screen.blit(text, (game.w // 2 - text.get_width() // 2, game.h - x))
        game.screen.blit(text2, (game.w // 2 - text2.get_width() // 2, game.h - x + text.get_height() + padding))
        update()
        game.clock.tick(60)

    pygame.time.delay(500)
    update_buttons("Exit", "Start")
    update()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    if "user" not in config:
                        game.state = "Baseline"
                    else:
                        game.state = "Test"
                    running = False
                elif e.key == pygame.K_l:
                    game.state = "Quit"
                    running = False


def baseline():
    """
    Record a baseline test event.
    """
    clear_screen()

    config["user"] = []
    config["scores"] = []
    config["eye"] = []
    config["passed"] = []
    update_config()

    base_text = font_normal.render("Looks like this is your first time", True, color_black)
    game.screen.blit(base_text, (game.w // 2 - base_text.get_width() // 2, game.h // 2 - base_text.get_height() // 2))
    base_text = font_normal.render("using KalEYEdoscope.", True, color_black)
    game.screen.blit(base_text, (game.w // 2 - base_text.get_width() // 2,
                                 game.h // 2 - base_text.get_height() // 2 + base_text.get_height() + padding))
    text = font_subtitle.render("Record Baseline Test", True, color_gray)
    game.screen.blit(text, (game.w // 2 - text.get_width() // 2, game.h // 2 + base_text.get_height() * 3))

    update_buttons("Start", "Start")
    update()
    game.state = "Test"
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                running = False

            update()


def test():
    """
    Test event
    """
    clear_screen()
    update_buttons("Left", "Right")
    base_text = font_normal.render("Select an eye to test.", True, color_black)
    game.screen.blit(base_text, (game.w // 2 - base_text.get_width() // 2, game.h // 2))
    update()

    eye = "Error"
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_l:
                    eye = "L"
                    running = False
                elif e.key == pygame.K_r:
                    eye = "R"
                    running = False
            update()

    score = 100
    normal_circle_indexes = [random.randint(0, 9), random.randint(0, 9), random.randint(0, 9)]
    distortions = list(range(1, 11))
    random.shuffle(distortions)
    for loop in range(10):
        if loop in normal_circle_indexes:
            distortion = 1
        else:
            distortion = distortions[loop]

        theta = np.arange(0, 4 * np.pi, 0.01)[1:]
        rho = 3 + 0.05 * sin(distortion * theta)
        plt.polar(theta, rho, linewidth=3)
        ax = plt.gca()
        ax.grid(False)
        ax.set_yticklabels([])
        ax.set_xticklabels([])
        ax.spines['polar'].set_visible(False)
        plt.gcf().savefig('images/current_circle.png', bbox_inches='tight', dpi=(WIDTH // 5))
        plt.close(plt.gcf())
        circle = pygame.image.load("images/current_circle.png")

        clear_screen()
        msg = "Testing " + eye + " eye."
        test_text = font_subtitle.render(msg, True, color_black)
        text = font_subtitle.render("%d/10" % loop, True, color_black)
        game.screen.blit(text, (game.w - text.get_width() - padding, padding))
        game.screen.blit(circle, (game.w // 2 - circle.get_width() // 2,
                                  game.h // 2 - circle.get_height() // 2))
        game.screen.blit(test_text, (0, 0))
        update_buttons("Distorted", "Normal")
        update()

        running = True
        while running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_r:
                        # normal
                        if distortion == 1:
                            score += 10
                        score -= distortion * 10
                        running = False
                    elif e.key == pygame.K_l:
                        # distorted
                        if distortion == 1:
                            score -= 30
                        running = False
                update()

    config["scores"].append(score)
    config["eye"].append(eye)
    if score > MINSCORE:
        config["passed"].append(1)
    else:
        config["passed"].append(0)

    update_config()

    clear_screen()
    msg = "You scored: " + str(score)
    text = font_title.render(msg, True, color_black)
    game.screen.blit(text, (game.w // 2 - text.get_width() // 2, game.h // 2 - text.get_height() // 2))
    update()
    pygame.time.delay(500)
    update_buttons("Start Menu", "View Results")
    update()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_l:
                    game.state = "Start"
                    running = False
                elif e.key == pygame.K_r:
                    game.state = "Profile"
                    running = False


def profile():
    """
    View profile event
    """
    scores = config["scores"]
    plt.plot(scores)
    plt.ylabel("Scores")
    plt.xlabel("Test")
    plt.gcf().savefig('images/plot.png', bbox_inches='tight', dpi=(WIDTH // 5))
    plt.close(plt.gcf())

    average = sum(scores) / len(scores)

    text = font_normal.render("Average score: %.2f" % average, True, color_black)

    plot = pygame.image.load("images/plot.png")
    clear_screen()

    game.screen.blit(plot, (game.w // 2 - plot.get_width() // 2, 0))
    game.screen.blit(text, (game.w // 2 - text.get_width() // 2, plot.get_height() + padding))
    update_buttons("Start Menu", "Advanced")
    update()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    game.state = "Advanced"
                    running = False
                elif e.key == pygame.K_l:
                    game.state = "Start"
                    running = False


def advanced():

    df = pd.DataFrame({"Passed": config["passed"],
                       "Eye": config["eye"]})

    model = sm.formula.glm("Passed ~ Eye",
                           family=sm.families.Binomial(),
                           data=df).fit()
    print(model.summary())
    clear_result_count = 5
    clear_screen()
    update_buttons("Start Menu", "Clear Results (%d)" % clear_result_count)
    update()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_l:
                    game.state = "Start"
                    running = False
                elif e.key == pygame.K_r:
                    if clear_result_count == 0:
                        game.state = "Start"
                        config.pop("user")
                        config.pop("scores")
                        config.pop("eye")
                        update_config()
                        running = False
                    else:
                        clear_result_count -= 1
                        clear_screen()
                        # TODO
                        update_buttons("Start Menu", "Clear Results (%d)" % clear_result_count)
                        update()


# MAIN RUNNING LOOP
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if game.state == "Start":
            start()

        if game.state == "Baseline":
            baseline()

        if game.state == "Test":
            test()

        if game.state == "Profile":
            profile()

        if game.state == "Advanced":
            advanced()

        if game.state == "Quit":
            sys.exit()
