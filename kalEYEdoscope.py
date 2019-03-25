import math
import random
import sys

import matplotlib

matplotlib.use('pdf')
import matplotlib.pyplot as plt
import numpy as np
import yaml
from pylab import sin

import RPi.GPIO as GPIO
import OLED_Driver as OLED
import Image
import ImageDraw
import ImageFont

# DEFINE CONSTANT VARIABLES

NUMCIRCLES = 10
WIDTH = 128
HEIGHT = 128
BUTTON1 = 14
BUTTON2 = 15
INTYPE = "BUTTON"
if len(sys.argv > 1):
    if sys.argv[1] == "-k":
        INTYPE = "KEYBOARD"


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
            if GPIO.input(BUTTON1) == GPIO.HIGH: return 1
            if GPIO.input(BUTTON2) == GPIO.HIGH: return 2
    elif INTYPE == "KEYBOARD":
        while True:
            i = raw_input("input: ")
            if i == "12": program_quit()
            if i == "1": return 1
            if i == "2": return 2


def clear_screen():
    """
    Clears the screen by filling with background
    """
    OLED.Clear_Screen()
    clear_image = Image.new("RGB", (OLED.SSD1351_WIDTH, OLED.SSD1351_HEIGHT), "DIMGREY")
    clear_draw = ImageDraw.Draw(clear_image)
    return clear_draw, clear_image


def update(update_image):
    OLED.Display_Image(update_image)


def update_data():
    """
    Saves current data to file
    """
    with open('data/data', "w") as save_data:
        yaml.dump(data, save_data)


def update_buttons(update_draw, left, right, title=None, subtitle=None):
    """
    Updates the text displayed for each button instruction
    :param update_draw:
    :param subtitle: text to be displayed just below title
    :param title: text to be displayed above option buttons
    :param left: text to be displayed for the left button
    :param right: text to be displayed for the right button
    """

    right_text = update_draw.textsize(right, font=font_normal)
    left_text = update_draw.textsize(left, font=font_normal)

    update_draw.rectangle([(WIDTH // 2 - right_text[0] // 2 - padding, HEIGHT // 2),
                           (WIDTH // 2 + right_text[0] // 2 + padding, HEIGHT // 2 + right_text[1] + padding)],
                          fill="GREEN")

    update_draw.rectangle([(WIDTH // 2 - left_text[0] // 2 - padding, HEIGHT * 3 // 4),
                           (WIDTH // 2 + left_text[0] // 2 + padding, HEIGHT * 3 // 4 + left_text[1] + padding)],
                          fill="RED")

    update_draw.text((WIDTH // 2 - right_text[0] // 2, HEIGHT // 2), right, font=font_normal, fill="BLACK")
    update_draw.text((WIDTH // 2 - left_text[0] // 2, HEIGHT * 3 // 4), left, font=font_normal, fill="BLACK")

    if title:
        title_text = update_draw.textsize(title, font_subtitle)
        update_draw.text((WIDTH // 2 - title_text[0] // 2, padding), title, font=font_subtitle)

    if subtitle:
        subtitle_text = update_draw.textsize(subtitle, font_subtitle)
        update_draw.text((WIDTH // 2 - subtitle_text[0] // 2, subtitle_text[1] + padding * 2), subtitle,
                         font=font_subtitle)


# INITIALIZATION

# Start display

OLED.Device_Init()

# Initialize buttons

GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Load frequently used variables

data = yaml.safe_load(open("data/data"))
state = "Start"

# Fonts
font_title = ImageFont.truetype('cambriab.ttf', 24)
font_subtitle = ImageFont.truetype('cambriab.ttf', 16)
font_normal = ImageFont.truetype('cambriab.ttf', 18)

# Spacings
padding = 2


# ACTIVITY FUNCTIONS

def start():
    """"
    Main screen event.
    """
    global state
    draw, image = clear_screen()
    welcome = "Welcome to your"
    title = "KalEYEdoscope"
    welcome_text = draw.textsize(welcome, font_subtitle)
    title_text = draw.textsize(title, font_subtitle)
    draw.text((WIDTH // 2 - welcome_text[0] // 2, welcome_text[1]), welcome, font=font_subtitle, fill="BLACK")
    draw.text((WIDTH // 2 - title_text[0] // 2, welcome_text[1] * 2 + padding), title, font=font_subtitle, fill="BLACK")

    update_buttons(draw, "Exit", "Start")
    update(image)

    button = get_input()

    if button == 1:
        if data["new_user"]:
            state = "Baseline"
        else:
            state = "Test"

    elif button == 2:
        state = "Quit"


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

    update_buttons(draw, "Start", "Start", "Record a ", "baseline.")
    update(image)
    get_input()
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
    plt.polar(theta, rho, linewidth=2, color='black')
    ax = plt.gca()
    ax.grid(False)
    ax.set_rmax(6)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.spines['polar'].set_visible(False)
    plt.gcf().savefig('images/current_circle.png', bbox_inches='tight', dpi=(WIDTH // 4), transparent=True)
    plt.close(plt.gcf())

    circle_image = Image.open("images/current_circle.png")
    draw, image = clear_screen()
    image.paste(circle_image, (0, 0))
    update(image)
    OLED.Delay(500)
    draw, image = clear_screen()
    update_buttons(draw, "No", "Yes", "Distorted?")
    update(image)

    choice = "error"
    button = get_input()
    if button == 1: choice = "y"
    if button == 2: choice = "n"

    return choice


def test():
    """
    Test event
    """
    global state

    # Pick eye
    draw, image = clear_screen()
    update_buttons(draw, "Left", "Right", "Select an eye", "to test.")
    update(image)
    eye = "Error"

    button = get_input()
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
    while threshold_difference >= 0.5:
        current_big_t = upper_threshold[current_test]
        current_small_t = lower_threshold[current_test]
        # threshold_difference = abs(current_big_t - current_small_t)
        if random.randint(0, 100) <= 75 or current_test == 0:
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
    update_buttons(draw, "Start Menu", "Start Menu", "Test Completed")
    update(image)

    get_input()
    state = "Start"


def program_quit():
    OLED.Clear_Screen()
    GPIO.cleanup()
    exit()

# def profile():
#     """
#     View profile event
#     """
#     scores = data["scores"]
#     plt.plot(scores)
#     plt.ylabel("Scores")
#     plt.xlabel("Test")
#     plt.gcf().savefig('images/plot.png', bbox_inches='tight', dpi=(WIDTH // 5))
#     plt.close(plt.gcf())
#
#     average = sum(scores) / len(scores)
#
#     text = font_normal.render("Average score: %.2f" % average, True, color_black)
#
#     plot = pygame.image.load("images/plot.png")
#     clear_screen()
#
#     game.screen.blit(plot, (game.w // 2 - plot.get_width() // 2, 0))
#     game.screen.blit(text, (game.w // 2 - text.get_width() // 2, plot.get_height() + padding))
#     update_buttons("Start Menu", "Advanced")
#     update()
#
#     running = True
#     while running:
#         for e in pygame.event.get():
#             if e.type == pygame.QUIT:
#                 sys.exit()
#             if e.type == pygame.KEYDOWN:
#                 if e.key == pygame.K_r:
#                     game.state = "Advanced"
#                     running = False
#                 elif e.key == pygame.K_l:
#                     game.state = "Start"
#                     running = False


# def advanced():
#     df = pd.DataFrame({"Passed": data["passed"],
#                        "Eye": data["eye"]})
#
#     model = sm.formula.glm("Passed ~ Eye",
#                            family=sm.families.Binomial(),
#                            data=df).fit()
#     print(model.summary())
#     clear_result_count = 5
#     clear_screen()
#     update_buttons("Start Menu", "Clear Results (%d)" % clear_result_count)
#     update()
#     running = True
#     while running:
#         for e in pygame.event.get():
#             if e.type == pygame.QUIT:
#                 sys.exit()
#             if e.type == pygame.KEYDOWN:
#                 if e.key == pygame.K_l:
#                     game.state = "Start"
#                     running = False
#                 elif e.key == pygame.K_r:
#                     if clear_result_count == 0:
#                         game.state = "Start"
#                         data.pop("user")
#                         data.pop("scores")
#                         data.pop("eye")
#                         update_data()
#                         running = False
#                     else:
#                         clear_result_count -= 1
#                         clear_screen()
#                         update_buttons("Start Menu", "Clear Results (%d)" % clear_result_count)
#                         update()


# MAIN RUNNING LOOP
while True:
    if state == "Start":
        start()

    elif state == "Baseline":
        baseline()

    elif state == "Test":
        test()

    # if state == "Profile":
    #     profile()
    #
    # if state == "Advanced":
    #     advanced()

    elif state == "Quit":
        program_quit()

    else:
        print(state)
        print(" not implemented yet\n")
        state = "Quit"
