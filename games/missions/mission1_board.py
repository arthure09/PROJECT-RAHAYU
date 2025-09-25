# games/missions/mission1_board.py
import arcade
from games.core.state import MiniGameResult  # pakai import absolut biar konsisten

TARGET = ["a","n","ki","ng","to","ng","h","ri","w"]  # 9 slot

class DragLetter(arcade.SpriteSolidColor):
    def __init__(self, char, x, y):
        super().__init__(52, 52, arcade.color.DARK_SLATE_GRAY)
        self.char = char
        self.center_x, self.center_y = x, y
        self.drag = False

class Slot(arcade.SpriteSolidColor):
    def __init__(self, x, y, target_char):
        super().__init__(60, 60, arcade.color.LIGHT_GRAY)
        self.center_x, self.center_y = x, y
        self.target = target_char
        self.filled = False

class Mission1View(arcade.View):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK_OLIVE)
        self.slots = arcade.SpriteList()
        self.letters = arcade.SpriteList()
        self.slot_labels: list[arcade.Text] = []   # nomor kecil di tiap slot

        # slots
        start_x, y_slot = 140, 360
        for i, ch in enumerate(TARGET):
            s = Slot(start_x + i*76, y_slot, ch)
            self.slots.append(s)
            self.slot_labels.append(
                arcade.Text(str(i+1), s.center_x - 5, s.center_y - 28, arcade.color.BLACK, 10)
            )

        # tray huruf (sementara urut, nanti bisa kamu acak)
        tray_x, tray_y = 140, 180
        for i, ch in enumerate(TARGET):
            d = DragLetter(ch, tray_x + (i % 9) * 76, tray_y - (i // 9) * 76)
            self.letters.append(d)

        self.held = None
        self.title = arcade.Text("MISI 1 — Tarik huruf Latin ke slot. Selesai? Tekan ENTER.",
                                 20, 540, arcade.color.WHITE, 16)

    def _all_correct(self):
        return all(s.filled for s in self.slots)

    def on_draw(self):
        self.clear()
        self.title.draw()

        # Gambar semua slot & huruf via SpriteList.draw()
        self.slots.draw()
        self.letters.draw()

        # Label nomor slot
        for lbl in self.slot_labels:
            lbl.draw()

        # Label huruf (boleh draw_text biasa; warning performa aman diabaikan sekarang)
        for d in self.letters:
            arcade.draw_text(d.char, d.center_x - 10, d.center_y - 6, arcade.color.WHITE, 12)

        if self._all_correct():
            arcade.draw_text("Selesai! Tekan [ENTER] untuk kembali.",
                             280, 60, arcade.color.ELECTRIC_LIME, 16)

    def on_mouse_press(self, x, y, button, mods):
        for d in reversed(self.letters):
            if d.collides_with_point((x, y)):
                self.held = d
                d.drag = True
                break

    def on_mouse_motion(self, x, y, dx, dy):
        if self.held and self.held.drag:
            self.held.center_x += dx
            self.held.center_y += dy

    def on_mouse_release(self, x, y, button, mods):
        if not self.held:
            return
        hit = arcade.get_sprites_at_point((x, y), self.slots)
        if hit:
            slot = hit[0]
            if (not slot.filled) and (slot.target == self.held.char):
                self.held.center_x, self.held.center_y = slot.center_x, slot.center_y
                slot.filled = True
                slot.color = arcade.color.ELECTRIC_LIME
            else:
                # salah → balikin ke bawah (posisi Y saja cukup)
                self.held.center_y = 120
        self.held.drag = False
        self.held = None

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ENTER and self._all_correct():
            self.on_finish(MiniGameResult(success=True))
        if key == arcade.key.ESCAPE:
            self.on_finish(MiniGameResult(success=False))
