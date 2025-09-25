from dataclasses import dataclass

@dataclass
class MiniGameResult:
    success: bool
    score: int = 0
    extra: dict | None = None

class SaveData:
    def __init__(self):
        self.m1_done = False
        self.m2_choice = None
        self.m3_score = 0
        self.m4_recipe = None
