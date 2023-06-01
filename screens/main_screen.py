from screen_handler import State


class MainScreen(State):
    def __init__(self):
        super()

    def handle_option(self, option) -> None:
        if option == 'pastel':
            print('gosto bastante')
        else:
            print('Vc tem mau gosto')