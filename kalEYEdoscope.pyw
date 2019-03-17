import math
import operator
import os
import random
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pygame
import statsmodels.api as sm
import yaml
from pylab import sin

# DEFINE CONSTANT VARIABLES

NUMCIRCLES = 10
WIDTH = 128
HEIGHT = 128


# DEFINE CONSTANT FUNCTIONS

def clear_screen():
    """
    Clears the screen by filling with background
    """
    game.screen.fill(color_background)


def update():
    """
    Updates screen
    """
    pygame.display.flip()


def update_data():
    """
    Saves current data to file
    """
    with open('data/data', "w") as save_data:
        yaml.dump(data, save_data)


def update_buttons(left, right, title=None, subtitle=None):
    """
    Updates the text displayed for each button instruction
    :param subtitle: text to be displayed just below title
    :param title: text to be displayed above option buttons
    :param left: text to be displayed for the left button
    :param right: text to be displayed for the right button
    """

    right_text = font_normal.render(right, True, color_black)
    left_text = font_normal.render(left, True, color_black)
    right_surface = pygame.Surface(tuple(map(operator.add, font_normal.size(right), (5, 5))))
    left_surface = pygame.Surface(tuple(map(operator.add, font_normal.size(left), (7, 7))))
    right_surface.fill(color_background)
    left_surface.fill(color_background)

    pygame.draw.rect(right_surface, color_right, right_surface.get_rect(), 2)
    pygame.draw.rect(left_surface, color_left, left_surface.get_rect(), 2)

    right_surface.blit(right_text, (right_surface.get_width() // 2 - right_text.get_width() // 2,
                                    right_surface.get_height() // 2 - right_text.get_height() // 2))
    left_surface.blit(left_text, (left_surface.get_width() // 2 - left_text.get_width() // 2,
                                  left_surface.get_height() // 2 - left_text.get_height() // 2))

    game.screen.blit(right_surface, (game.w // 2 - right_surface.get_width() // 2, game.h // 2))
    game.screen.blit(left_surface, (game.w // 2 - left_surface.get_width() // 2, game.h * 3 // 4))

    if title:
        title_text = font_title.render(title, True, color_black)
        game.screen.blit(title_text, (game.w // 2 - title_text.get_width() // 2, title_text.get_height()))

    if subtitle:
        subtitle_text = font_title.render(subtitle, True, color_black)
        game.screen.blit(subtitle_text, (game.w // 2 - subtitle_text.get_width() // 2,
                                         subtitle_text.get_height() * 2 + padding))


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

os.environ["SDL_FBDEV"] = "/dev/fb1"

# Load frequently used variables

game = Game()
data = yaml.safe_load(open("data/data"))

# Fonts
font_title = pygame.font.Font(None, 22)
font_subtitle = pygame.font.Font(None, 16)
font_normal = pygame.font.Font(None, 22)

# Spacings
padding = 2

# Colors
color_black = (0, 0, 0)
color_gray = (100, 100, 100)
color_background = (200, 200, 200)
color_right = (255, 0, 0)
color_left = (0, 255, 0)


# ACTIVITY FUNCTIONS

def start():
    """"
    Main screen event.
    """
    clear_screen()
    text = font_title.render("Welcome to your", True, color_black)
    surface = pygame.Surface(font_title.size("Welcome to your"))
    surface.fill(color_background)
    surface.blit(text, (0, 0))
    text2 = font_title.render("KalEYEdoscope", True, color_black)
    surface2 = pygame.Surface(font_title.size("KalEYEdoscope"))
    surface2.fill(color_background)
    surface2.blit(text2, (0, 0))
    for x in range(100):
        surface.set_alpha(x)
        surface2.set_alpha(x)
        game.screen.blit(surface, (game.w // 2 - text.get_width() // 2, text.get_height()))
        game.screen.blit(surface2, (game.w // 2 - text2.get_width() // 2, text.get_height() * 2 + padding))
        update()
        game.clock.tick(60)

    update_buttons("Exit", "Start")
    update()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    if data["new_user"]:
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

    data["new_user"] = False
    data["tests"] = {"0": None}
    data["number_of_tests"] = -1
    update_data()

    update_buttons("Start", "Start", "Record a ", "baseline.")
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


def display_circle(angle, theta, r, circle_num):
    """
    Displays a circle for half a second, then prompts the user to answer whether the circle is distorted.
    :param angle: angle of the circle
    :param theta: theta for the circle
    :param r: circle radius
    :param circle_num: current test number
    :return: user's selection
    """
    tan = math.tan(math.radians(angle))
    if tan != 0:
        slope = 1 / tan
    else:
        slope = 99999
    b = random.randint(5, 8)
    phi = random.random() * 2 * np.pi
    distortions = [r / (slope * 5), r / (slope * 6), r / (slope * 7), r / (slope * 8)]
    rho = r + distortions[b - 5] * sin(b * (theta + phi))
    plt.polar(theta, rho, linewidth=2, color='black')
    ax = plt.gca()
    ax.grid(False)
    ax.set_rmax(6)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.spines['polar'].set_visible(False)
    plt.gcf().savefig('images/current_circle.png', bbox_inches='tight', dpi=(WIDTH // 4.5), transparent=True)
    plt.close(plt.gcf())
    circle = pygame.image.load("images/current_circle.png")
    clear_screen()
    if circle_num < 0:
        text = font_subtitle.render("sanity check", True, color_gray)
    else:
        text = font_subtitle.render("%d" % circle_num, True, color_gray)
    game.screen.blit(text, (game.w - text.get_width() - padding, padding))
    game.screen.blit(circle, (game.w // 2 - circle.get_width() // 2,
                              game.h // 2 - circle.get_height() // 2))
    update()
    pygame.time.delay(500)
    clear_screen()
    game.screen.blit(text, (game.w - text.get_width() - padding, padding))
    update_buttons("Yes", "No", "Distorted?")
    update()

    running = True
    choice = "error"
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    # normal
                    choice = "n"
                    running = False
                elif e.key == pygame.K_l:
                    # distorted
                    choice = "y"
                    running = False
            update()

    return choice


def test():
    """
    Test event
    """
    # Pick eye
    clear_screen()
    update_buttons("Left", "Right", "Select an eye", "to test.")
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

    # Read user data
    testnum = str(data["number_of_tests"] + 1)
    data["tests"][testnum] = {}
    data["number_of_tests"] = data["number_of_tests"] + 1
    data["tests"][testnum]["eye"] = eye

    # Calculate Circle Parameters
    upper_threshold = [15]
    lower_threshold = [0]
    current_test = 0
    threshold_difference = 15
    convergence = 0.372
    theta = np.arange(0, 4 * np.pi, 0.01)[1:]
    r = random.randint(3, 5)
    incorrect_sanity_checks = 0
    num_sanity_checks = 0
    while threshold_difference >= 0.5:
        current_big_t = upper_threshold[current_test]
        current_small_t = lower_threshold[current_test]
        # threshold_difference = abs(current_big_t - current_small_t)
        if random.randint(0, 100) <= 75 or current_test == 0:
            # Normal Test
            angle = current_big_t - convergence * threshold_difference
            choice = display_circle(angle, theta, r, current_test + 1)
            if choice == "y":
                upper_threshold.append(angle)
            else:
                upper_threshold.append(
                    (current_big_t + min(np.median(upper_threshold), np.mean(upper_threshold))) / 2
                )
            angle = current_small_t + convergence * abs(upper_threshold[current_test + 1] - current_small_t)
            choice = display_circle(angle, theta, r, current_test + 1)
            if choice == "y":
                lower_threshold.append(
                    (current_small_t + min(np.median(lower_threshold), np.mean(lower_threshold))) / 2
                )
            else:
                lower_threshold.append(angle)
        else:
            # Sanity Check Test
            num_sanity_checks += 1
            angle = random.choice([current_big_t, current_small_t])
            choice = display_circle(angle, theta, r, -1)
            if choice == "y":
                upper_threshold.append(current_big_t)
                if angle == current_small_t:
                    lower_threshold.append(lower_threshold[current_test - 1])
                    incorrect_sanity_checks += 1
                else:
                    lower_threshold.append(current_small_t)
            elif choice == "n":
                lower_threshold.append(current_small_t)
                if angle == current_small_t:
                    upper_threshold.append(upper_threshold[current_test - 1])
                    incorrect_sanity_checks += 1
                else:
                    upper_threshold.append(current_big_t)

        current_test += 1
        current_big_t = upper_threshold[current_test]
        current_small_t = lower_threshold[current_test]
        threshold_difference = abs(current_big_t - current_small_t)

    data["tests"][testnum]["lower_thresholds"] = [float(x) for x in lower_threshold]
    data["tests"][testnum]["upper_thresholds"] = [float(x) for x in upper_threshold]
    data["tests"][testnum]["check_sanity_num"] = num_sanity_checks
    data["tests"][testnum]["incorrect_sanity_checks"] = incorrect_sanity_checks
    update_data()

    clear_screen()
    update_buttons("Start Menu", "Start Menu", "Test Completed")
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
                    # game.state = "Profile"
                    game.state = "Start"
                    running = False


def profile():
    """
    View profile event
    """
    scores = data["scores"]
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
    df = pd.DataFrame({"Passed": data["passed"],
                       "Eye": data["eye"]})

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
                        data.pop("user")
                        data.pop("scores")
                        data.pop("eye")
                        update_data()
                        running = False
                    else:
                        clear_result_count -= 1
                        clear_screen()
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
