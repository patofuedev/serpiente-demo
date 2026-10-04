import math
import random
import tkinter as tk

CELL = 24
COLS = 26
ROWS = 18
DELAY = 110  # ms entre movimientos

# Geometria del televisor
SW, SH = COLS * CELL, ROWS * CELL
OX, OY = 50, 70                      # esquina superior izquierda de la pantalla
W, H = OX + SW + 140, OY + SH + 80   # tamano total de la ventana

DIRS = {
    "Up": (0, -1),
    "Down": (0, 1),
    "Left": (-1, 0),
    "Right": (1, 0),
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
}

SCREEN_A = "#0d2417"
SCREEN_B = "#0f2a1b"
HEAD_COLOR = (124, 240, 90)
TAIL_COLOR = (28, 150, 70)


def mix(c1, c2, t):
    return "#%02x%02x%02x" % tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def rounded(canvas, x1, y1, x2, y2, r, **kw):
    pts = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


class Snake:
    def __init__(self, root):
        self.root = root
        root.title("Snake TV")
        root.resizable(False, False)
        self.canvas = tk.Canvas(root, width=W, height=H, bg="#1b1410",
                                highlightthickness=0)
        self.canvas.pack()
        root.bind("<Key>", self.on_key)
        self.frame = 0
        self.draw_tv()
        self.reset()
        self.tick()

    # ---------- televisor (capa estatica) ----------
    def draw_tv(self):
        c = self.canvas
        cx = OX + SW // 2

        # patas
        for x in (60, W - 90):
            c.create_rectangle(x, H - 24, x + 30, H - 6, fill="#2a1d14", outline="")
        # antenas
        for dx, tipx, tipy in ((-10, cx - 90, 6), (10, cx + 80, 10)):
            c.create_line(cx + dx, 44, tipx, tipy, fill="#c9c9c9", width=3)
            c.create_oval(tipx - 4, tipy - 4, tipx + 4, tipy + 4,
                          fill="#e8e8e8", outline="")
        c.create_oval(cx - 22, 34, cx + 22, 56, fill="#2a1d14", outline="")

        # carcasa de madera
        rounded(c, 10, 40, W - 10, H - 20, 34, fill="#3b2616", outline="#1a0f08", width=3)
        rounded(c, 18, 46, W - 18, H - 28, 30, fill="#5a3a22", outline="")
        c.create_line(40, 50, W - 40, 50, fill="#7a5233", width=2)

        # marco de la pantalla
        rounded(c, OX - 18, OY - 18, OX + SW + 18, OY + SH + 18, 26,
                fill="#0a0a0a", outline="#2b2b2b", width=3)

        # panel derecho: altavoz, perillas y LED
        px = OX + SW + 40
        pw = W - 34 - px
        rounded(c, px - 6, OY - 18, px + pw + 6, OY + SH + 18, 16,
                fill="#3b2616", outline="#1a0f08", width=2)
        for i in range(10):
            y = OY + 4 + i * 9
            c.create_line(px + 8, y, px + pw - 8, y, fill="#1a0f08", width=3)
        for i, ky in enumerate((OY + 140, OY + 215)):
            kx = px + pw // 2
            c.create_oval(kx - 24, ky - 24, kx + 24, ky + 24,
                          fill="#d8d0c0", outline="#1a0f08", width=3)
            c.create_oval(kx - 17, ky - 17, kx + 17, ky + 17,
                          fill="#8f8776", outline="")
            a = math.radians(-50 + i * 70)
            c.create_line(kx, ky, kx + 15 * math.sin(a), ky - 15 * math.cos(a),
                          fill="#1a0f08", width=3, capstyle="round")
        c.create_oval(px + pw // 2 - 6, OY + SH - 30, px + pw // 2 + 6, OY + SH - 18,
                      fill="#ff3b30", outline="#7a0f0a", width=2)

        # marca y etiqueta
        c.create_text(px + pw // 2, OY + SH + 44, text="RETRO-VISION",
                      fill="#d8c9a8", font=("Courier", 10, "bold"))
        c.create_text(OX, OY + SH + 44, anchor="w", text="SNAKE CH.03",
                      fill="#d8c9a8", font=("Courier", 10, "bold"))

        # fondo de la pantalla (tablero de cuadros sutiles)
        for x in range(COLS):
            for y in range(ROWS):
                col = SCREEN_A if (x + y) % 2 else SCREEN_B
                c.create_rectangle(OX + x * CELL, OY + y * CELL,
                                   OX + (x + 1) * CELL, OY + (y + 1) * CELL,
                                   fill=col, outline="", tags="bg")

        # lineas de barrido, vineta y reflejo del cristal
        for y in range(OY, OY + SH, 3):
            c.create_line(OX, y, OX + SW, y, fill="#000000",
                          stipple="gray12", tags="scan")
        for width, stp in ((16, "gray12"), (10, "gray25"), (5, "gray50")):
            c.create_rectangle(OX, OY, OX + SW, OY + width, fill="black",
                               stipple=stp, outline="", tags="scan")
            c.create_rectangle(OX, OY + SH - width, OX + SW, OY + SH, fill="black",
                               stipple=stp, outline="", tags="scan")
            c.create_rectangle(OX, OY, OX + width, OY + SH, fill="black",
                               stipple=stp, outline="", tags="scan")
            c.create_rectangle(OX + SW - width, OY, OX + SW, OY + SH, fill="black",
                               stipple=stp, outline="", tags="scan")
        c.create_polygon(OX + 10, OY + 10, OX + 150, OY + 10, OX + 10, OY + 110,
                         fill="white", stipple="gray12", outline="", tags="scan")

    # ---------- logica ----------
    def reset(self):
        self.snake = [(COLS // 2 - i, ROWS // 2) for i in range(4)]
        self.direction = (1, 0)
        self.next_dir = self.direction
        self.score = 0
        self.alive = True
        self.paused = False
        self.place_food()
        self.draw()

    def place_food(self):
        free = [
            (x, y)
            for x in range(COLS)
            for y in range(ROWS)
            if (x, y) not in self.snake
        ]
        self.food = random.choice(free) if free else None

    def on_key(self, event):
        key = event.keysym if event.keysym in DIRS else event.char.lower()
        if key in DIRS:
            d = DIRS[key]
            # no permitir giro de 180 grados
            if d[0] != -self.direction[0] or d[1] != -self.direction[1]:
                self.next_dir = d
        elif key == "p" and self.alive:
            self.paused = not self.paused
            self.draw()
        elif key in ("r", " ") and not self.alive:
            self.reset()

    def tick(self):
        self.frame += 1
        if self.alive and not self.paused:
            self.step()
        self.draw()
        self.root.after(DELAY, self.tick)

    def step(self):
        self.direction = self.next_dir
        hx, hy = self.snake[0]
        head = (hx + self.direction[0], hy + self.direction[1])
        grows = head == self.food
        body = self.snake if grows else self.snake[:-1]
        if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS) or head in body:
            self.alive = False
            return
        self.snake.insert(0, head)
        if grows:
            self.score += 1
            self.place_food()
            if self.food is None:  # tablero lleno: victoria
                self.alive = False
        else:
            self.snake.pop()

    # ---------- dibujo ----------
    def center(self, pos):
        return (OX + pos[0] * CELL + CELL / 2, OY + pos[1] * CELL + CELL / 2)

    def draw_apple(self):
        c = self.canvas
        x, y = self.center(self.food)
        r = CELL / 2 - 3 + math.sin(self.frame * 0.5) * 0.8
        c.create_oval(x - r - 5, y - r - 4, x + r + 5, y + r + 6,
                      fill="#ff4040", stipple="gray25", outline="", tags="game")
        c.create_oval(x - r + 2, y + r - 2, x + r - 2, y + r + 3,
                      fill="#05100a", outline="", tags="game")
        for dx in (-r * 0.35, r * 0.35):
            c.create_oval(x + dx - r * 0.75, y - r * 0.75 + 2,
                          x + dx + r * 0.75, y + r * 0.75 + 2,
                          fill="#e0262d", outline="#8e1016", width=1, tags="game")
        c.create_oval(x - r * 0.7, y - r * 0.6 + 2, x + r * 0.7, y + r * 0.7 + 2,
                      fill="#e0262d", outline="", tags="game")
        c.create_oval(x - r * 0.6, y - r * 0.2, x - r * 0.2, y + r * 0.2,
                      fill="#ffb3b3", outline="", tags="game")
        c.create_line(x, y - r * 0.5, x + 2, y - r - 4, fill="#6b3a1a",
                      width=2, capstyle="round", tags="game")
        c.create_polygon(x + 2, y - r - 3, x + 10, y - r - 8, x + 12, y - r - 2,
                         x + 5, y - r + 1, fill="#43c34a", outline="#1f7a2a",
                         smooth=True, tags="game")

    def draw_snake(self):
        c = self.canvas
        n = len(self.snake)
        pts = [self.center(p) for p in self.snake]
        base = CELL - 4

        def width(i):
            return base - min(9, max(0, i - (n - 6)) * 1.8)

        def color(i):
            col = mix(HEAD_COLOR, TAIL_COLOR, i / max(1, n - 1))
            return col if self.alive else mix((150, 150, 150), (80, 80, 80), i / max(1, n - 1))

        # sombra / contorno
        for i in range(n - 1, 0, -1):
            c.create_line(*pts[i], *pts[i - 1], width=width(i) + 4, fill="#04170b",
                          capstyle="round", tags="game")
        # cuerpo con degradado
        for i in range(n - 1, 0, -1):
            c.create_line(*pts[i], *pts[i - 1], width=width(i), fill=color(i),
                          capstyle="round", tags="game")
        # dibujo de escamas y brillo
        for i in range(1, n):
            x, y = pts[i]
            if i % 2 == 0:
                r = width(i) / 4
                c.create_oval(x - r, y - r, x + r, y + r,
                              fill=mix(HEAD_COLOR, TAIL_COLOR, 0.75 * i / max(1, n - 1)),
                              outline="", tags="game")
            r = width(i) / 6
            c.create_oval(x - r - 3, y - r - 4, x + r - 3, y + r - 4,
                          fill="#d6ffc0", stipple="gray50", outline="", tags="game")

        # cabeza
        hx, hy = pts[0]
        fx, fy = self.direction
        px, py = -fy, fx
        hr = CELL / 2 - 0.5
        if self.alive and self.frame % 8 < 4:
            bx, by = hx + fx * (hr - 2), hy + fy * (hr - 2)
            tx, ty = hx + fx * (hr + 8), hy + fy * (hr + 8)
            c.create_line(bx, by, tx, ty, fill="#ff3b5c", width=2, tags="game")
            for s in (-1, 1):
                c.create_line(tx, ty, tx + fx * 4 + px * 4 * s, ty + fy * 4 + py * 4 * s,
                              fill="#ff3b5c", width=2, tags="game")
        c.create_oval(hx - hr - 2, hy - hr - 2, hx + hr + 2, hy + hr + 2,
                      fill="#04170b", outline="", tags="game")
        c.create_oval(hx - hr, hy - hr, hx + hr, hy + hr,
                      fill=color(0), outline="", tags="game")
        for s in (-1, 1):
            ex, ey = hx + fx * 3 + px * 5 * s, hy + fy * 3 + py * 5 * s
            if self.alive:
                c.create_oval(ex - 4, ey - 4, ex + 4, ey + 4, fill="white",
                              outline="#04170b", tags="game")
                c.create_oval(ex + fx * 1.5 - 2, ey + fy * 1.5 - 2,
                              ex + fx * 1.5 + 2, ey + fy * 1.5 + 2,
                              fill="black", outline="", tags="game")
            else:
                c.create_line(ex - 3, ey - 3, ex + 3, ey + 3, fill="black", width=2, tags="game")
                c.create_line(ex - 3, ey + 3, ex + 3, ey - 3, fill="black", width=2, tags="game")

    def draw(self):
        c = self.canvas
        c.delete("game")
        if self.food:
            self.draw_apple()
        self.draw_snake()

        # marcador tipo LED
        c.create_rectangle(OX + SW // 2 - 90, OY + SH + 28, OX + SW // 2 + 90, OY + SH + 60,
                           fill="#120a05", outline="#000", tags="game")
        c.create_text(OX + SW // 2, OY + SH + 44, text=f"PUNTOS {self.score:03d}",
                      fill="#ffb000", font=("Courier", 16, "bold"), tags="game")

        mx, my = OX + SW // 2, OY + SH // 2
        if not self.alive or self.paused:
            c.create_rectangle(OX, OY, OX + SW, OY + SH, fill="black",
                               stipple="gray50", outline="", tags="game")
            if not self.alive:
                msg = f"FIN DEL JUEGO\nPUNTOS: {self.score}\n\nR PARA REINICIAR"
            else:
                msg = "PAUSA"
            for off, col in ((2, "#052b12"), (0, "#7cf09a")):
                c.create_text(mx + off, my + off, text=msg, fill=col, justify="center",
                              font=("Courier", 26, "bold"), tags="game")
        c.tag_raise("scan")


if __name__ == "__main__":
    root = tk.Tk()
    Snake(root)
    root.mainloop()
