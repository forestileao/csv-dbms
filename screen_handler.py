from __future__ import annotations
from abc import ABC, abstractmethod
import os


class ScreenHandler:

    """
    Screen current state reference
    """
    state_stack = []

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        # print(f"Context: Transition to {type(state).__name__}")
        self.state_stack.append(state)
        self.state_stack[-1].context = self

    def return_last_state(self) -> None:
        if len(self.state_stack) > 1:
            self.state_stack.pop()
        self.state_stack[-1].context = self

    def handle_option(self, option):
        if option == "..":
            self.return_last_state()
        else:
            self.state_stack[-1].handle_option(option)

    def print_options(self):
        # os.system('clear')
        self.state_stack[-1].print_options()

class State(ABC):
    @property
    def context(self) -> ScreenHandler:
        return self._context

    @context.setter
    def context(self, context: ScreenHandler) -> None:
        self._context = context

    @abstractmethod
    def handle_option(self, option) -> None:
        pass
