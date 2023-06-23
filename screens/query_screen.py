from screen_handler import State
from query_processor import QueryProcessor


class QueryScreen(State):

    def __init__(self):
        super()
        self.query_processor = QueryProcessor()

    def handle_option(self, option) -> None:
        self.query_processor.process(option)

    def print_options(self):
        pass