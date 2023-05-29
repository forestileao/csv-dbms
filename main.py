from screen_handler import ScreenHandler
from main_screen import MainScreen


def start_loop():
    running = True

    screen_handler = ScreenHandler(MainScreen())

    while running:
        try:
            option = input("> ")
            screen_handler.handle_option(option)

        except KeyboardInterrupt:
            print('Exiting...')
            running = False


if __name__ == '__main__':
    start_loop()
