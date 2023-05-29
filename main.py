from screen_handler import ScreenHandler
from main_screen import MainScreen


def start_loop():
    running = True

    screen_handler = ScreenHandler(MainScreen())

    while running:
        option = input("> ")

        if option == 'exit':
            running = False
        else:
            screen_handler.handle_option(option)


if __name__ == '__main__':
    start_loop()
