from __future__ import annotations
from abc import ABC, abstractmethod


class ScreenHandler:

    """
    Screen current state reference
    """
    _state = None

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def handle_option(self, option):
        self._state.handle_option(option)


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
