import arcade
from games.core.state import MiniGameResult

VOCAB = [
    ("Sampurasun", "Salam / Sapaan"),
    ("Anjeun", "Kamu"),
    ("Lembur", "Desa"),
    ("Hapunten", "Maaf"),
    ("Ti mana asalna?", "Dari mana asalnya?")
]

CHOICES = {
    "prompt": "Pilih balasan (tekan A / B):",
    "A": '“Muhun, abdi ti lembur nu jauh.”',
    "B": '“Saéstuna abdi ti tempat nu jauh pisan…”'
}
CORRECT = "A"  # ubah ke "B" kalau kamu mau jawaban benar = B

class Mission2View(arcade.View):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_SLATE_BLUE)
        self.show_vocab = True
        self.timer = 5.0

        # feedback salah
        self.feedback_active = False
        self.feedback_timer = 0.0

        # pre-render text
        self.title = arcade.Text("MISI 2 — Percakapan di Kampung", 20, 540, arcade.color.WHITE, 16)
        self.npc_line = arcade.Text('NPC: "Sampurasun, Anjeun ti mana asalna?"', 20, 500,
                                    arcade.color.ANTIQUE_WHITE, 14, width=980)
        self.prompt = arcade.Text(CHOICES["prompt"], 20, 460, arcade.color.WHITE, 14)
        self.choice_a = arcade.Text("[A] " + CHOICES["A"], 40, 430, arcade.color.WHITE, 12, width=940)
        self.choice_b = arcade.Text("[B] " + CHOICES["B"], 40, 400, arcade.color.WHITE, 12, width=940)
        self.hint = arcade.Text("Hint: [V] toggle Kosakata • [ESC] batal", 20, 40,
                                arcade.color.LIGHT_GRAY, 12)
        self.vocab_title = arcade.Text("Kosakata (auto-hilang 5 dtk, bisa toggle [V])",
                                       640, 500, arcade.color.ELECTRIC_LIME, 12)

        # panel vocab area (kanan)
        self.left, self.right, self.bottom, self.top = 620, 1000, 360, 520

        # text feedback SALAH
        self.fb_text = arcade.Text("SALAH", 0, 0, arcade.color.RED, 40, bold=True)
        # posisi tengah layar diatur di on_draw pakai ukuran window

    def on_update(self, dt):
        if self.show_vocab and self.timer > 0:
            self.timer -= dt
            if self.timer <= 0:
                self.show_vocab = False

        if self.feedback_active:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback_active = False

    def on_draw(self):
        self.clear()
        self.title.draw()
        self.npc_line.draw()
        self.prompt.draw()
        self.choice_a.draw()
        self.choice_b.draw()
        self.hint.draw()

        if self.show_vocab:
            arcade.draw_lrbt_rectangle_filled(self.left, self.right, self.bottom, self.top, (0, 0, 0, 180))
            self.vocab_title.draw()
            y = self.top - 40
            for su, idn in VOCAB:
                arcade.draw_text(f"{su} = {idn}", self.left + 20, y, arcade.color.WHITE, 11)
                y -= 20

        # overlay feedback SALAH
        if self.feedback_active:
            # panel semi-transparan
            arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 120))
            # posisikan teks di tengah
            self.fb_text.x = (self.window.width // 2) - 70
            self.fb_text.y = (self.window.height // 2) - 20
            self.fb_text.draw()

    def _trigger_wrong_feedback(self, seconds: float = 1.2):
        self.feedback_active = True
        self.feedback_timer = seconds

    def on_key_press(self, key, modifiers):
        if key == arcade.key.A:
            if CORRECT == "A":
                self.on_finish(MiniGameResult(success=True, extra={"choice": "A"}))
            else:
                self._trigger_wrong_feedback()
        elif key == arcade.key.B:
            if CORRECT == "B":
                self.on_finish(MiniGameResult(success=True, extra={"choice": "B"}))
            else:
                self._trigger_wrong_feedback()
        elif key == arcade.key.V:
            self.show_vocab = not self.show_vocab
        elif key == arcade.key.ESCAPE:
            self.on_finish(MiniGameResult(success=False, extra={"choice": None}))
