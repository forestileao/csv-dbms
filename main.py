from import_screen import ImportScreen
from screen_handler import ScreenHandler


def start_loop():
    running = True

    screen_handler = ScreenHandler(ImportScreen())

    while running:
        try:
            option = input("> ")
            screen_handler.handle_option(option)

        except KeyboardInterrupt:
            print('Exiting...')
            running = False


if __name__ == '__main__':
    start_loop()
