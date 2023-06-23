from screen_handler import State
from screens.import_screen import ImportScreen
from screens.query_screen import QueryScreen

class MainScreen(State):
    def __init__(self):
        super()

        self.options = {
            'import': self.handle_import,
            'run': self.handle_query,
            'exit': self.exit,
        }
        self.print_options()

    def handle_option(self, option) -> None:

        if option in self.options.keys():
            stage_function = self.options[option]
            stage_function()

        else:
            self.print_options()

    def print_options(self) -> None:
        print(f"[!] Select an option:")

        for key in self.options:
            print(f"\t[*] {key}")

    def handle_import(self) -> None:
        print("Handle import")
        self.context.transition_to(ImportScreen())


    def handle_query(self) -> None:
        print("Handle query")
        self.context.transition_to(QueryScreen())

    def exit(self):
        quit(code=0)
