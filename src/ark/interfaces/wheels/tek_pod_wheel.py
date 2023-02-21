import pyautogui  # type:ignore[import]

from .wheel import ActionWheel


class TekPodWheel(ActionWheel):
    def __init__(self) -> None:
        super().__init__("Tek Sleeping Pod", "assets/wheels/pod.png")

    def lay_on(self) -> None:
        self.select_action((1166, 495), click=False)
        pyautogui.keyUp(self.keybinds.use)
