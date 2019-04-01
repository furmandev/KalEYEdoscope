import math
import random
import sys

import matplotlib

matplotlib.use('pdf')
import matplotlib.pyplot as plt
import numpy as np
import yaml
from pylab import sin

# DEFINE CONSTANT VARIABLES

NUMCIRCLES = 10
WIDTH = 128
HEIGHT = 128
BUTTON1 = 14
BUTTON2 = 15
INTYPE = "BUTTON"
DISPLAYTYPE = "OLED"

# Interpret command-line arguments
if len(sys.argv) > 1:
    if "-k" in sys.argv:
        INTYPE = "KEYBOARD"
    if "-d" in sys.argv:
        DISPLAYTYPE = "HDMI"
        WIDTH = 384
        HEIGHT = 384
        import pygame
        import os
        import operator
    else:
        import RPi.GPIO as GPIO
        import OLED_Driver as OLED
        import Image
        import ImageDraw
        import ImageFont
    if "-c" in sys.argv:
        INTYPE = "SHELL"


# DEFINE CONSTANT FUNCTIONS

def get_input():
    quit_count = 0
    if INTYPE == "BUTTON":
        while True:
            if GPIO.input(BUTTON1) == GPIO.HIGH and GPIO.input(BUTTON2) == GPIO.HIGH:
                if quit_count == 2:
                    program_quit()
                OLED.Delay(1000)
                quit_count += 1
            elif GPIO.input(BUTTON1) == GPIO.HIGH:
                return 1
            elif GPIO.input(BUTTON2) == GPIO.HIGH:
                return 2
    elif INTYPE == "SHELL":
        while True:
            if sys.version_info[0] < 3:
                i = raw_input("input: ")
            else:
                i = input("input: ")
            if i == "12": program_quit()
            if i == "1": return 1
            if i == "2": return 2
    elif INTYPE == "KEYBOARD":
        while True:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_UP: return 1
                    if e.key == pygame.K_DOWN: return 2
                    if e.key == pygame.K_q: program_quit()


def clear_screen():
    """
    Clears the screen by filling with background
    """
    if DISPLAYTYPE == "OLED":
        OLED.Clear_Screen()
        clear_image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "DIMGREY")
        clear_draw = ImageDraw.Draw(clear_image)
        return clear_draw, clear_image
    elif DISPLAYTYPE == "HDMI":
        screen.fill(color_background)
        return None, None


def update(update_image=None):
    if DISPLAYTYPE == "OLED":
        OLED.Display_Image(update_image)
    elif DISPLAYTYPE == "HDMI":
        pygame.display.flip()


def update_data():
    """
    Saves current data to file
    """
    with open('data/data', "w") as save_data:
        yaml.dump(data, save_data)


def update_buttons(left, right, title=None, subtitle=None, update_draw=None, update_image=None):
    """
    Updates the text displayed for each button instruction
    :param update_image:
    :param update_draw:
    :param subtitle: text to be displayed just below title
    :param title: text to be displayed above option buttons
    :param left: text to be displayed for the left button
    :param right: text to be displayed for the right button
    """
    if DISPLAYTYPE == "OLED":
        right_text = update_draw.textsize(right, font=font_normal)
        left_text = update_draw.textsize(left, font=font_normal)

        update_draw.rectangle([(WIDTH // 2 - right_text[0] // 2 - padding, HEIGHT // 2),
                               (WIDTH // 2 + right_text[0] // 2 + padding, HEIGHT // 2 + right_text[1] + padding)],
                              fill="BLUE")

        update_draw.rectangle([(WIDTH // 2 - left_text[0] // 2 - padding, HEIGHT * 3 // 4),
                               (WIDTH // 2 + left_text[0] // 2 + padding, HEIGHT * 3 // 4 + left_text[1] + padding)],
                              fill="DARKORANGE")

        update_draw.text((WIDTH // 2 - right_text[0] // 2, HEIGHT // 2), right, font=font_normal)
        update_draw.text((WIDTH // 2 - left_text[0] // 2, HEIGHT * 3 // 4), left, font=font_normal)

        if title:
            title_text = update_draw.textsize(title, font_subtitle)
            update_draw.text((WIDTH // 2 - title_text[0] // 2, padding), title, font=font_subtitle)

        if subtitle:
            subtitle_text = update_draw.textsize(subtitle, font_subtitle)
            update_draw.text((WIDTH // 2 - subtitle_text[0] // 2, subtitle_text[1] + padding * 2), subtitle,
                             font=font_subtitle)

        update(update_image)
        button = get_input()
        if button == 1:
            update_draw.rectangle([(WIDTH // 2 - right_text[0] // 2 - padding, HEIGHT // 2),
                                   (WIDTH // 2 + right_text[0] // 2 + padding, HEIGHT // 2 + right_text[1] + padding)],
                                  outline="BLACK")
            update(update_image)
            return 1
        if button == 2:
            update_draw.rectangle([(WIDTH // 2 - left_text[0] // 2 - padding, HEIGHT * 3 // 4),
                                   (
                                       WIDTH // 2 + left_text[0] // 2 + padding,
                                       HEIGHT * 3 // 4 + left_text[1] + padding)],
                                  outline="BLACK")
            update(update_image)
            return 2

    elif DISPLAYTYPE == "HDMI":
        right_text = font_normal.render(right, True, color_white)
        left_text = font_normal.render(left, True, color_white)
        right_surface = pygame.Surface(tuple(map(operator.add, font_normal.size(right), (5, 5))))
        left_surface = pygame.Surface(tuple(map(operator.add, font_normal.size(left), (7, 7))))
        right_surface.fill(color_background)
        left_surface.fill(color_background)

        pygame.draw.rect(right_surface, color_right, right_surface.get_rect())
        pygame.draw.rect(left_surface, color_left, left_surface.get_rect())

        right_surface.blit(right_text, (right_surface.get_width() // 2 - right_text.get_width() // 2,
                                        right_surface.get_height() // 2 - right_text.get_height() // 2))
        left_surface.blit(left_text, (left_surface.get_width() // 2 - left_text.get_width() // 2,
                                      left_surface.get_height() // 2 - left_text.get_height() // 2))

        screen.blit(right_surface, (WIDTH // 2 - right_surface.get_width() // 2, HEIGHT // 2))
        screen.blit(left_surface, (WIDTH // 2 - left_surface.get_width() // 2, HEIGHT * 3 // 4))

        if title:
            title_text = font_title.render(title, True, color_white)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, title_text.get_height()))

        if subtitle:
            subtitle_text = font_title.render(subtitle, True, color_white)
            screen.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2,
                                        subtitle_text.get_height() * 2 + padding))

        update()
        button = get_input()
        if button == 1:
            pygame.draw.rect(right_surface, color_black, right_surface.get_rect(), 2)
            right_surface.blit(right_text, (right_surface.get_width() // 2 - right_text.get_width() // 2,
                                            right_surface.get_height() // 2 - right_text.get_height() // 2))
            screen.blit(right_surface, (WIDTH // 2 - right_surface.get_width() // 2, HEIGHT // 2))

            update()
            pygame.time.delay(100)
            return 1
        if button == 2:
            pygame.draw.rect(left_surface, color_black, left_surface.get_rect(), 2)
            left_surface.blit(left_text, (left_surface.get_width() // 2 - left_text.get_width() // 2,
                                          left_surface.get_height() // 2 - left_text.get_height() // 2))
            screen.blit(left_surface, (WIDTH // 2 - left_surface.get_width() // 2, HEIGHT * 3 // 4))

            update()
            pygame.time.delay(100)
            return 2


# INITIALIZATION

# Start display

if DISPLAYTYPE == "OLED":
    OLED.Device_Init()
elif DISPLAYTYPE == "HDMI":
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()
    size = WIDTH, HEIGHT
    pygame.display.set_caption("KalEYEdoscope")
    screen = pygame.display.set_mode(size, pygame.NOFRAME)
    clock = pygame.time.Clock()

# Initialize buttons

if INTYPE == "BUTTON":
    GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Load frequently used variables

data = yaml.safe_load(open("data/data"))
state = "Start"

# Fonts
if DISPLAYTYPE == "OLED":
    font_title = ImageFont.truetype('cambriab.ttf', 24)
    font_subtitle = ImageFont.truetype('cambriab.ttf', 16)
    font_normal = ImageFont.truetype('cambriab.ttf', 18)
else:
    font_title = pygame.font.Font(None, 66)
    font_subtitle = pygame.font.Font(None, 48)
    font_normal = pygame.font.Font(None, 66)

# Spacings
padding = 2

# Colors
color_black = (0, 0, 0)
color_gray = (100, 100, 100)
color_white = (255, 255, 255)
color_background = (105, 105, 105)
color_right = (0, 0, 255)
color_left = (255, 140, 0)


# ACTIVITY FUNCTIONS

def start():
    """"
    Main screen event.
    """
    global state
    if DISPLAYTYPE == "OLED":
        draw, image = clear_screen()
        welcome = "Welcome to your"
        title = "KalEYEdoscope"
        welcome_text = draw.textsize(welcome, font_subtitle)
        title_text = draw.textsize(title, font_subtitle)
        draw.text((WIDTH // 2 - welcome_text[0] // 2, welcome_text[1]), welcome, font=font_subtitle, fill="BLACK")
        draw.text((WIDTH // 2 - title_text[0] // 2, welcome_text[1] * 2 + padding), title, font=font_subtitle,
                  fill="BLACK")

        button = update_buttons("Exit", "Start", update_draw=draw, update_image=image)

    else:
        clear_screen()
        text = font_title.render("Welcome to your", True, color_white)
        surface = pygame.Surface(font_title.size("Welcome to your"))
        surface.fill(color_background)
        surface.blit(text, (0, 0))
        text2 = font_title.render("KalEYEdoscope", True, color_white)
        surface2 = pygame.Surface(font_title.size("KalEYEdoscope"))
        surface2.fill(color_background)
        surface2.blit(text2, (0, 0))
        screen.blit(surface, (WIDTH // 2 - text.get_width() // 2, text.get_height()))
        screen.blit(surface2, (WIDTH // 2 - text2.get_width() // 2, text.get_height() * 2 + padding))
        update()
        button = update_buttons("Exit", "Start")
        update()

    if button == 1:
        if data["new_user"]:
            state = "Baseline"
        else:
            state = "Test"

    else:
        program_quit()


def baseline():
    """
    Record a baseline test event.
    """
    global state
    draw, image = clear_screen()

    data["new_user"] = False
    data["tests"] = {"0": None}
    data["number_of_tests"] = -1
    update_data()

    update_buttons("Start", "Start", "Record a ", "baseline.", draw, image)
    state = "Test"


def display_circle(angle, theta, r):
    """
    Displays a circle for half a second, then prompts the user to answer whether the circle is distorted.
    :param angle: angle of the circle
    :param theta: theta for the circle
    :param r: circle radius
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
    plt.polar(theta, rho, linewidth=2, color='w')
    ax = plt.gca()
    ax.grid(False)
    ax.set_rmax(6)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.spines['polar'].set_visible(False)
    plt.gcf().savefig('images/current_circle.png', bbox_inches='tight', dpi=(WIDTH // 4), transparent=True,
                      facecolor='k')
    plt.close(plt.gcf())

    if DISPLAYTYPE == "OLED":
        circle_image = Image.open("images/current_circle.png", mode='r')
        draw = ImageDraw.Draw(circle_image)
        # Center cross hair
        draw.line((WIDTH // 2, HEIGHT // 2 - 2, WIDTH // 2, HEIGHT // 2 + 2))
        draw.line((WIDTH // 2 - 2, HEIGHT // 2, WIDTH // 2 + 2, HEIGHT // 2))

        OLED.Clear_Screen()
        update(circle_image)
        OLED.Delay(500)
    elif DISPLAYTYPE == "HDMI":
        circle = pygame.image.load("images/current_circle.png")
        clear_screen()
        screen.blit(circle, (WIDTH // 2 - circle.get_width() // 2,
                             HEIGHT // 2 - circle.get_height() // 2))
        pygame.draw.line(screen, color_white, (WIDTH // 2, HEIGHT // 2 - 5), (WIDTH // 2, HEIGHT // 2 + 5))
        pygame.draw.line(screen, color_white, (WIDTH // 2 - 5, HEIGHT // 2), (WIDTH // 2 + 5, HEIGHT // 2))
        update()
        pygame.time.delay(500)
        clear_screen()

    draw, image = clear_screen()
    button = update_buttons("No", "Yes", "Was that a", "perfect circle?", draw, image)

    # Note that choice returns "y" for a distorted circle and "n" for a normal circle
    if button == 1:
        choice = "n"
    elif button == 2:
        choice = "y"
    else:
        choice = "error"

    return choice


def test():
    """
    Test event
    """
    global state

    # Pick eye
    draw, image = clear_screen()
    button = update_buttons("Left", "Right", "Select an eye", "to test.", draw, image)
    eye = "Error"

    if button == 1:
        eye = "L"
    elif button == 2:
        eye = "R"

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
    while threshold_difference >= 0.75:
        current_big_t = upper_threshold[current_test]
        current_small_t = lower_threshold[current_test]
        # threshold_difference = abs(current_big_t - current_small_t)
        if random.randint(0, 100) <= 85 or current_test == 0:
            # Normal Test
            angle = current_big_t - convergence * threshold_difference
            choice = display_circle(angle, theta, r)
            if choice == "y":
                upper_threshold.append(angle)
            else:
                upper_threshold.append(
                    (current_big_t + min(np.median(upper_threshold), np.mean(upper_threshold))) / 2
                )
            angle = current_small_t + convergence * abs(upper_threshold[current_test + 1] - current_small_t)
            choice = display_circle(angle, theta, r)
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
            choice = display_circle(angle, theta, r)
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

    draw, image = clear_screen()
    update_buttons("Start Menu", "Start Menu", "Test Completed", draw, image)
    state = "Start"


def program_quit():
    if DISPLAYTYPE == "OLED":
        OLED.Clear_Screen()
        GPIO.cleanup()
        exit()
    else:
        sys.exit()


# MAIN RUNNING LOOP
while True:
    if state == "Start":
        start()

    elif state == "Baseline":
        baseline()

    elif state == "Test":
        test()

    elif state == "Quit":
        program_quit()

    else:
        print(state)
        print(" not implemented yet\n")
        state = "Quit"
