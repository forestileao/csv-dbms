from screens.import_screen import ImportScreen
from screens.main_screen import MainScreen
from screen_handler import ScreenHandler

from dotenv import load_dotenv


def start_loop():
    running = True

    screen_handler = ScreenHandler(MainScreen())

    while running:
        try:
            screen_handler.print_options()
            option = input("> ")
            screen_handler.handle_option(option)

        except KeyboardInterrupt:
            print('Exiting...')
            running = False


if __name__ == '__main__':
    load_dotenv()
    start_loop()
