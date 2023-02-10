class State:
    """Controls the state of the program."""

    running = True
    paused = False

    def __init__(self) -> None:
        raise RuntimeError("State class is not meant to be instantiated")