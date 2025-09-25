# games/hub/overworld.py
import arcade
from games.missions.mission1_board import Mission1View
from games.missions.mission2_dialogue import Mission2View
from games.missions.mission3_angklung import Mission3View
from games.missions.mission4_cooking import Mission4View

# --- Konfigurasi dunia sederhana ---
MAP_W, MAP_H = 1024, 576
PLAYER_SPEED = 240.0          # px/detik
INTERACT_DIST = 150.0          # jarak untuk prompt [E]
BLOCK_MARGIN = 4              # rollback kecil saat tabrak

class Player(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # Gambar statis karakter (ganti dengan gambar PNG)
        self.texture = arcade.load_texture("C:\\Users\\arthur ephraim\\OneDrive\\Dokumen\\game_risya\\games\\assets\\assets\\1.png")  # Ganti dengan gambar karakter

        # Posisi karakter
        self.center_x, self.center_y = x, y
        self.vx = 0
        self.vy = 0

    def update(self):
        # Update posisi karakter sesuai dengan input gerakan
        self.center_x += self.vx
        self.center_y += self.vy

class Overworld(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

        # --- Player ---
        self.player = Player(120, 140)  # Gambar karakter dari PNG
        self.actors = arcade.SpriteList()
        self.actors.append(self.player)

        # --- Bangunan/spot misi ---
        self.spots = arcade.SpriteList()

        self.papan = arcade.SpriteSolidColor(160, 100, arcade.color.ASH_GREY)
        self.papan.center_x, self.papan.center_y = 220, 360
        self.spots.append(self.papan)

        self.kampung = arcade.SpriteSolidColor(160, 100, arcade.color.ASH_GREY)
        self.kampung.center_x, self.kampung.center_y = 440, 360
        self.spots.append(self.kampung)

        self.sanggar = arcade.SpriteSolidColor(160, 100, arcade.color.ASH_GREY)
        self.sanggar.center_x, self.sanggar.center_y = 660, 360
        self.spots.append(self.sanggar)

        self.warung = arcade.SpriteSolidColor(160, 100, arcade.color.ASH_GREY)
        self.warung.center_x, self.warung.center_y = 880, 360
        self.spots.append(self.warung)

        # label-2 bangunan
        def label(text, sprite):
            return arcade.Text(text, sprite.center_x - 55, sprite.center_y - 10, arcade.color.BLACK, 12, bold=True)
        self.lbls = [
            label("PAPAN", self.papan),
            label("KAMPUNG", self.kampung),
            label("SANGGAR", self.sanggar),
            label("WARUNG", self.warung),
        ]

        # HUD
        self.title = arcade.Text("Jelajahi dengan WASD/Arrow. Dekati bangunan lalu [E] untuk masuk.",
                                 20, MAP_H - 36, arcade.color.WHITE, 14)
        self.tip = arcade.Text("TIP: [ESC] di dalam misi untuk batal dan kembali ke hub",
                               20, MAP_H - 60, arcade.color.LIGHT_GRAY, 12)

        s = self.window.save
        self.status = arcade.Text(
            f"M1:{'✔' if s.m1_done else '—'}  "
            f"M2:{s.m2_choice or '—'}  "
            f"M3:{s.m3_score}  "
            f"M4:{s.m4_recipe or '—'}",
            20, 20, arcade.color.AQUA, 14
        )

        # prompt interaksi, dinamis
        self.prompt = arcade.Text("", 0, 0, arcade.color.WHITE, 12, bold=True)

        # input state
        self.keys = set()

    # ---------- loop ----------
    def on_update(self, dt: float):
        # gerak dari input
        vx = vy = 0.0
        if arcade.key.A in self.keys or arcade.key.LEFT in self.keys:
            vx -= PLAYER_SPEED
        if arcade.key.D in self.keys or arcade.key.RIGHT in self.keys:
            vx += PLAYER_SPEED
        if arcade.key.W in self.keys or arcade.key.UP in self.keys:
            vy += PLAYER_SPEED
        if arcade.key.S in self.keys or arcade.key.DOWN in self.keys:
            vy -= PLAYER_SPEED

        old_x, old_y = self.player.center_x, self.player.center_y
        self.player.center_x += vx * dt
        self.player.center_y += vy * dt

        # batas layar
        self.player.center_x = max(16, min(MAP_W - 16, self.player.center_x))
        self.player.center_y = max(16, min(MAP_H - 16, self.player.center_y))

        # tabrakan sederhana: rollback jika nabrak spot
        if arcade.check_for_collision_with_list(self.player, self.spots):
            # rollback X
            self.player.center_x = old_x
            if arcade.check_for_collision_with_list(self.player, self.spots):
                # geser sedikit keluar di Y kalau masih nabrak
                self.player.center_y = old_y - BLOCK_MARGIN if vy > 0 else old_y + BLOCK_MARGIN
            # cek Y lagi
            if arcade.check_for_collision_with_list(self.player, self.spots):
                self.player.center_y = old_y

        # prompt interaksi
        target, dist = self._nearest_spot()
        if target and dist <= INTERACT_DIST:
            self._update_prompt_at(target, "[E] Interact")
        else:
            self.prompt.text = ""

        # refresh HUD
        s = self.window.save
        self.status.text = (
            f"M1:{'✔' if s.m1_done else '—'}  "
            f"M2:{s.m2_choice or '—'}  "
            f"M3:{s.m3_score}  "
            f"M4:{s.m4_recipe or '—'}"
        )

    def on_draw(self):
        self.clear()
        self.title.draw()
        self.tip.draw()

        # spot & label
        self.spots.draw()
        for t in self.lbls:
            t.draw()

        # player (via SpriteList)
        self.actors.draw()

        # prompt
        if self.prompt.text:
            self.prompt.draw()

        # status
        self.status.draw()

    # ---------- input ----------
    def on_key_press(self, key, modifiers):
        self.keys.add(key)
        if key == arcade.key.E:
            target, dist = self._nearest_spot()
            if target and dist <= INTERACT_DIST:
                if target is self.papan:
                    self.window.go(Mission1View(on_finish=self.after_m1))
                elif target is self.kampung:
                    self.window.go(Mission2View(on_finish=self.after_m2))
                elif target is self.sanggar:
                    self.window.go(Mission3View(on_finish=self.after_m3))
                elif target is self.warung:
                    self.window.go(Mission4View(on_finish=self.after_m4))

    def on_key_release(self, key, modifiers):
        self.keys.discard(key)

    # ---------- helpers ----------
    def _nearest_spot(self):
        nearest, best = None, 1e9
        for sp in self.spots:
            d = arcade.get_distance_between_sprites(self.player, sp)
            if d < best:
                best, nearest = d, sp
        return nearest, best

    def _update_prompt_at(self, sprite, text):
        self.prompt.text = text
        self.prompt.x = sprite.center_x - 46
        self.prompt.y = sprite.center_y + 70

    # ---------- callbacks dari misi ----------
    def after_m1(self, result):
        self.window.save.m1_done = bool(result and result.success)
        self.window.go(self)

    def after_m2(self, result):
        choice = result.extra.get("choice") if (result and result.extra) else None
        self.window.save.m2_choice = choice
        self.window.go(self)

    def after_m3(self, result):
        self.window.save.m3_score = result.score if result else 0
        self.window.go(self)

    def after_m4(self, result):
        recipe = result.extra.get("recipe") if (result and result.extra) else None
        self.window.save.m4_recipe = recipe
        self.window.go(self)
