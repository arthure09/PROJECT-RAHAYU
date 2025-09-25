# games/missions/mission3_angklung.py
import arcade
from games.core.state import MiniGameResult

# ====== Konfigurasi dasar ======
LANES = ["C", "D", "E", "F", "G"]                     # label nada (opsional)
KEY_LABELS = ["A", "S", "D", "J", "K"]                # label tombol yang tampil di bawah
KEY_MAP = {arcade.key.A: 0, arcade.key.S: 1, arcade.key.D: 2, arcade.key.J: 3, arcade.key.K: 4}

# Fase per-lane: menggeser waktu tiba di garis HIT agar tidak barengan
LANE_PHASE = [0.00, 0.05, 0.10, 0.15, 0.20]           # detik per-lane (silakan ubah selera)

WINDOW_W, WINDOW_H = 1024, 576
LANE_X0, LANE_GAP = 160, 160
HIT_Y = 140                                            # garis hit
START_Y = 560                                          # posisi spawn catatan
SPEED = 100.0                                          # px/detik
TRAVEL_TIME = (START_Y - HIT_Y) / SPEED

BPM = 90
SPB = 60.0 / BPM                                       # detik per ketukan
INTRO_DELAY = 1.0                                      # jeda sebelum note pertama di-hit

# Chart sederhana: (beat, lane_index)
RAW_CHART = [
    (0.0, 0), (0.5, 2), (1.0, 1), (1.5, 3), (2.0, 4),
    (3.0, 3), (3.5, 2), (4.5, 1),
    (6.0, 0), (6.5, 2), (7.0, 4), (7.5, 1),
    (8.5, 3), (9.0, 0), (9.75, 2), (10.5, 4)
]

HIT_WINDOW_PX = 28                                     # toleransi jarak dari HIT_Y (px)
SCORE_PER_HIT = 100
TARGET_SCORE = 800                                     # ambang lulus


class Note(arcade.SpriteSolidColor):
    def __init__(self, lane_idx: int, hit_time: float):
        super().__init__(36, 18, arcade.color.LIGHT_GREEN)
        self.lane_idx = lane_idx
        self.hit_time = hit_time                        # kapan seharusnya sampai HIT_Y
        self.center_x = LANE_X0 + lane_idx * LANE_GAP
        self.center_y = START_Y

    def update(self, dt: float):
        # gerak turun
        self.center_y -= SPEED * dt


class Mission3View(arcade.View):
    def __init__(self, on_finish):
        super().__init__()
        self.on_finish = on_finish

    def on_show_view(self):
        arcade.set_background_color(arcade.color.DARK_GREEN)
        self.time = 0.0

        # siapkan chart: hit_time dan spawn_time (dengan fase per-lane)
        self.chart = []
        for beat, lane in RAW_CHART:
            hit_t = INTRO_DELAY + beat * SPB + LANE_PHASE[lane]  # <-- fase diterapkan di sini
            spawn_t = hit_t - TRAVEL_TIME
            self.chart.append({"lane": lane, "hit_time": hit_t, "spawn_time": spawn_t})
        self.chart.sort(key=lambda x: x["spawn_time"])
        self.next_index = 0

        # notes aktif
        self.notes = arcade.SpriteList()

        # skor & combo
        self.score = 0
        self.combo = 0
        self.judgement = ""       # "HIT" / "MISS"
        self.judg_timer = 0.0

        # teks statis
        self.title = arcade.Text("MISI 3 — Rhythm Angklung (A S D  J K)", 20, 540, arcade.color.WHITE, 16)
        self.hint  = arcade.Text("Tekan tombol saat not menyentuh garis. [ESC] untuk batal.",
                                 20, 510, arcade.color.WHITE, 12)
        self.score_text = arcade.Text("", 20, 20, arcade.color.AQUA, 14)

        # garis lane (precompute x)
        self.lane_xs = [LANE_X0 + i * LANE_GAP for i in range(len(LANES))]

        # --- LABELS: tombol & nada ---
        self.key_labels = []
        self.note_labels = []
        for i, x in enumerate(self.lane_xs):
            # huruf tombol keyboard di bawah garis HIT
            self.key_labels.append(
                arcade.Text(KEY_LABELS[i], x - 8, HIT_Y - 30, arcade.color.WHITE, 18, bold=True)
            )
            # nama nada di atas (opsional)
            self.note_labels.append(
                arcade.Text(LANES[i], x - 6, 525, arcade.color.LIGHT_GRAY, 12)
            )

    def on_update(self, dt: float):
        self.time += dt

        # spawn note sesuai waktunya
        while self.next_index < len(self.chart) and self.time >= self.chart[self.next_index]["spawn_time"]:
            item = self.chart[self.next_index]
            self.notes.append(Note(item["lane"], item["hit_time"]))
            self.next_index += 1

        # update posisi note
        self.notes.update(dt)

        # cek miss (note lewat dari HIT_Y + toleransi)
        for note in list(self.notes):
            if note.center_y < HIT_Y - HIT_WINDOW_PX:
                self.notes.remove(note)
                self.combo = 0
                self._show_judgement("MISS")

        # update timer judgement text
        if self.judg_timer > 0:
            self.judg_timer -= dt
            if self.judg_timer <= 0:
                self.judgement = ""

        # kondisi selesai: chart habis & tidak ada note aktif
        last_hit_time = INTRO_DELAY + RAW_CHART[-1][0] * SPB if RAW_CHART else 0
        # perhatikan: ada fase, tapi ini hanya untuk tombol terakhir; jeda 0.5s masih aman
        if self.next_index >= len(self.chart) and len(self.notes) == 0 and self.time > (last_hit_time + max(LANE_PHASE) + 0.5):
            success = self.score >= TARGET_SCORE
            self.on_finish(MiniGameResult(success=success, score=self.score))

    def on_draw(self):
        self.clear()
        self.title.draw()
        self.hint.draw()

        # gambar garis lane
        for x in self.lane_xs:
            arcade.draw_line(x, 80, x, 520, arcade.color.LIGHT_GRAY, 2)
        # garis HIT
        arcade.draw_line(self.lane_xs[0] - 50, HIT_Y, self.lane_xs[-1] + 50, HIT_Y, arcade.color.YELLOW, 3)

        # gambar not
        self.notes.draw()

        # --- draw labels (tombol & nada) ---
        for lbl in self.key_labels:
            lbl.draw()
        for lbl in self.note_labels:
            lbl.draw()

        # HUD skor
        self.score_text.text = f"Score: {self.score}   Combo: {self.combo}"
        self.score_text.draw()

        # judgement overlay
        if self.judgement:
            arcade.draw_lrbt_rectangle_filled(0, self.window.width, 0, self.window.height, (0, 0, 0, 90))
            jtxt = arcade.Text(
                self.judgement,
                self.window.width // 2 - 40,
                self.window.height // 2 - 20,
                arcade.color.WHITE if self.judgement == "HIT" else arcade.color.RED,
                30,
                bold=True
            )
            jtxt.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.on_finish(MiniGameResult(success=False, score=self.score))
            return
        if key not in KEY_MAP:
            return

        lane = KEY_MAP[key]
        # cari note terdekat di lane tsb
        candidate = None
        best_dist = 1e9
        for note in self.notes:
            if note.lane_idx != lane:
                continue
            dist = abs(note.center_y - HIT_Y)
            if dist < best_dist:
                best_dist = dist
                candidate = note

        if candidate and best_dist <= HIT_WINDOW_PX:
            # HIT
            self.notes.remove(candidate)
            self.score += SCORE_PER_HIT
            self.combo += 1
            self._show_judgement("HIT")
        else:
            # salah timing / lane
            self.combo = 0
            self._show_judgement("MISS")

    def _show_judgement(self, text: str):
        self.judgement = text
        self.judg_timer = 0.35
