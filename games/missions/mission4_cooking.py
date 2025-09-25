# games/missions/mission4_cooking.py
import arcade
from games.core.state import MiniGameResult

# ---------- Konfigurasi dasar ----------
WINDOW_W, WINDOW_H = 1024, 576

# ---------- Util ----------
class Item(arcade.SpriteSolidColor):
    def __init__(self, iid: str, label: str, x: float, y: float, w=90, h=36, color=arcade.color.DARK_SLATE_GRAY):
        super().__init__(w, h, color)
        self.iid = iid
        self.label = label
        self.center_x, self.center_y = x, y
        self.origin = (x, y)
        self.drag = False
        self.used = False

class Mission4View(arcade.View):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish

    # --------- Data resep (CIRÉNG) ----------
    def _build_recipe(self):
        # Tiap step punya: text, req: item-id yang harus dimasukkan ke target
        return [
            {"text": "Masukkan ke panci: daun bawang, bawang putih, 1 sdm tapioka, garam, kaldu, air.",
             "req": ["daun","bawang","tapioka1","garam","kaldu","air"], "target": "pot"},
            {"text": "Aduk & masak api kecil hingga kental. (Tekan A untuk mengaduk)",
             "req": [], "key": "A"},
            {"text": "Tuang ke sisa tapioka. Seret 'tapioka sisa' ke panci.",
             "req": ["tapioka2"], "target": "pot"},
            {"text": "Bentuk adonan. (Tekan B)",
             "req": [], "key": "B"},
            {"text": "Goreng adonan di wajan. Seret 'adonan' ke wajan.",
             "req": ["adonan"], "target": "pan"}
        ]

    # ---- Layout helper: posisi tray 2 baris, 4 kolom per baris ----
    def _tray_pos(self, idx: int, per_row=4, x0=140, gap=150, y_row1=150, y_row2=90):
        row = idx // per_row
        col = idx % per_row
        x = x0 + col * gap
        y = y_row1 if row == 0 else y_row2
        return x, y

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BROWN_NOSE)

        # UI kontainer (panci & wajan) — statis (memang tidak bisa digeser)
        self.ui = arcade.SpriteList()
        self.pot = arcade.SpriteSolidColor(200, 120, arcade.color.GRAY)
        self.pot.center_x, self.pot.center_y = 300, 330
        self.ui.append(self.pot)

        self.pan = arcade.SpriteSolidColor(220, 90, arcade.color.DARK_SLATE_BLUE)
        self.pan.center_x, self.pan.center_y = 720, 300
        self.ui.append(self.pan)

        # Teks statis
        self.title = arcade.Text("MISI 4 — Memasak CIRÉNG", 20, 540, arcade.color.WHITE, 16)
        self.hint  = arcade.Text("Drag bahan ke target. [A/B] untuk aksi, [ESC] batal", 20, 515, arcade.color.WHITE, 12)

        # Label besar & kecil
        self.lbl_pot_big = arcade.Text("PANCI", self.pot.center_x - 50, self.pot.center_y + 70, arcade.color.WHITE, 16, bold=True)
        self.lbl_pan_big = arcade.Text("WAJAN", self.pan.center_x - 52, self.pan.center_y + 60, arcade.color.WHITE, 16, bold=True)
        self.lbl_pot = arcade.Text("PANCI", self.pot.center_x - 30, self.pot.center_y - 10, arcade.color.WHITE, 12)
        self.lbl_pan = arcade.Text("WAJAN", self.pan.center_x - 30, self.pan.center_y - 10, arcade.color.WHITE, 12)

        # Feedback overlay
        self.feedback = ""
        self.feedback_timer = 0.0
        self.feedback_text = arcade.Text("", WINDOW_W//2 - 60, WINDOW_H//2 - 20, arcade.color.WHITE, 34, bold=True)

        # Resep & progres
        self.steps = self._build_recipe()
        self.step_idx = 0
        self.current_ok: set[str] = set()

        # Items (tray 2 baris)
        self.items = arcade.SpriteList()
        base_items = [
            ("daun",     "daun bawang"),
            ("bawang",   "bawang putih"),
            ("tapioka1", "tapioka (1 sdm)"),
            ("garam",    "garam"),
            ("kaldu",    "kaldu bubuk"),
            ("air",      "air"),
            ("tapioka2", "tapioka sisa"),
        ]
        for i, (iid, label) in enumerate(base_items):
            x, y = self._tray_pos(i)  # otomatis 2 baris
            self.items.append(Item(iid, label, x, y))

        # Text runtime
        self.step_text = arcade.Text("", 20, 470, arcade.color.ANTIQUE_WHITE, 13, width=980)
        self.progress_text = arcade.Text("", 20, 440, arcade.color.LIGHT_GREEN, 12)
        self._refresh_texts()

        self.held: Item | None = None

    # ---------- Helpers ----------
    def _show_feedback(self, text: str, color):
        self.feedback = text
        self.feedback_text.text = text
        self.feedback_text.color = color
        self.feedback_timer = 0.9

    def _clear_feedback_if_needed(self, dt):
        if self.feedback_timer > 0:
            self.feedback_timer -= dt
            if self.feedback_timer <= 0:
                self.feedback = ""

    def _refresh_texts(self):
        step = self.steps[self.step_idx]
        self.step_text.text = f"Langkah {self.step_idx+1}/{len(self.steps)}: {step['text']}"
        if step.get("req"):
            need = [iid for iid in step["req"] if iid not in self.current_ok]
            self.progress_text.text = f"Masukkan: {', '.join(need)}"
        elif step.get("key"):
            self.progress_text.text = f"Tekan [{step['key']}] untuk melanjutkan."
        else:
            self.progress_text.text = ""

    def _spawn_adonan_in_tray(self):
        # tempatkan adonan di slot tray berikutnya (masih dalam layar)
        idx = len(self.items)
        x, y = self._tray_pos(idx)
        self.items.append(Item("adonan", "adonan", x, y, w=110))

    def _advance_step(self):
        self.step_idx += 1
        self.current_ok.clear()

        # selesai semua langkah
        if self.step_idx >= len(self.steps):
            self.on_finish(MiniGameResult(success=True, extra={"recipe": "cireng"}))
            return

        # baru selesai langkah 4 (Bentuk adonan) -> sekarang step_idx == 4 -> spawn adonan di tray
        if self.step_idx == 4 and not any(it.iid == "adonan" for it in self.items):
            self._spawn_adonan_in_tray()

        self._refresh_texts()

    # ---------- Event ----------
    def on_update(self, dt: float):
        self._clear_feedback_if_needed(dt)

    def on_draw(self):
        self.clear()
        self.title.draw()
        self.hint.draw()

        # Objek & label
        self.ui.draw()
        self.lbl_pot_big.draw()
        self.lbl_pan_big.draw()
        self.lbl_pot.draw()
        self.lbl_pan.draw()

        # Items & labelnya
        self.items.draw()
        for it in self.items:
            arcade.draw_text(it.label, it.center_x - 65, it.center_y + 28, arcade.color.WHITE, 11, width=130, align="center")

        # Panel instruksi
        arcade.draw_lrbt_rectangle_filled(20, 1004, 430, 520, (0, 0, 0, 140))
        self.step_text.draw()
        self.progress_text.draw()

        # Feedback overlay
        if self.feedback:
            arcade.draw_lrbt_rectangle_filled(0, WINDOW_W, 0, WINDOW_H, (0, 0, 0, 100))
            self.feedback_text.x = WINDOW_W//2 - (len(self.feedback)*9)
            self.feedback_text.y = WINDOW_H//2 - 20
            self.feedback_text.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        # pick item teratas yang diklik
        for it in reversed(self.items):
            if it.collides_with_point((x, y)) and not it.used:
                self.held = it
                it.drag = True
                break

    def on_mouse_motion(self, x, y, dx, dy):
        if self.held and self.held.drag:
            self.held.center_x += dx
            self.held.center_y += dy

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.held:
            return

        step = self.steps[self.step_idx]
        accepted = False

        # cek target sprite berdasarkan step
        target_id = step.get("target")
        target_sprite = self.pot if target_id == "pot" else self.pan if target_id == "pan" else None

        if step.get("req") and target_sprite is not None:
            # hanya periksa jika step butuh bahan
            if arcade.check_for_collision(self.held, target_sprite):
                if self.held.iid in step["req"] and self.held.iid not in self.current_ok:
                    # benar
                    self.current_ok.add(self.held.iid)
                    self.held.used = True
                    # “masuk panci/wajan”: snap ke dalam area (stack rapi)
                    self.held.center_x = target_sprite.center_x
                    self.held.center_y = target_sprite.center_y + 6 + (len(self.current_ok) * 4)
                    self._show_feedback("BENAR", arcade.color.ELECTRIC_LIME)
                    accepted = True
                    # cek selesai step
                    if self.current_ok.issuperset(set(step["req"])):
                        self._advance_step()
                else:
                    # salah bahan atau dobel
                    self._show_feedback("SALAH", arcade.color.RED)

        if not accepted:
            # kembalikan ke posisi awal
            self.held.center_x, self.held.center_y = self.held.origin

        self.held.drag = False
        self.held = None
        self._refresh_texts()

    def on_key_press(self, key, modifiers):
        step = self.steps[self.step_idx]
        if key == arcade.key.ESCAPE:
            self.on_finish(MiniGameResult(success=False, extra={"recipe": None}))
            return

        # Step berbasis tombol (A / B)
        if step.get("key"):
            need_A = step["key"] == "A" and key == arcade.key.A
            need_B = step["key"] == "B" and key == arcade.key.B
            if need_A or need_B:
                self._show_feedback("OK", arcade.color.ELECTRIC_LIME)

                # Backup: kalau ini langkah B (bentuk adonan) pastikan adonan muncul
                if need_B and not any(it.iid == "adonan" for it in self.items):
                    self._spawn_adonan_in_tray()

                self._advance_step()
            else:
                # abaikan tombol navigasi umum, selain itu beri feedback salah
                if key not in (arcade.key.LSHIFT, arcade.key.RSHIFT, arcade.key.TAB):
                    self._show_feedback("SALAH", arcade.color.RED)
