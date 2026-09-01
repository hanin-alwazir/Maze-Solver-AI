import tkinter as tk
from tkinter import ttk
from collections import deque
import heapq
import random
import time
import sys

# =======================
# صوت (Windows winsound)
# =======================
try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False


def beep_ok(root=None):
    if HAS_WINSOUND and sys.platform.startswith("win"):
        winsound.Beep(880, 120)
        winsound.Beep(988, 120)
    else:
        if root:
            try:
                root.bell()
            except Exception:
                pass


def beep_win(root=None):
    if HAS_WINSOUND and sys.platform.startswith("win"):
        winsound.Beep(784, 140)
        winsound.Beep(880, 140)
        winsound.Beep(1047, 180)
    else:
        if root:
            try:
                root.bell()
            except Exception:
                pass


def beep_tie(root=None):
    if HAS_WINSOUND and sys.platform.startswith("win"):
        winsound.Beep(660, 120)
        winsound.Beep(660, 120)
    else:
        if root:
            try:
                root.bell()
            except Exception:
                pass


# =======================
# خوارزميات
# =======================
def in_bounds(r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols


def neighbors(maze, pos):
    rows, cols = len(maze), len(maze[0])
    r, c = pos
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    out = []
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc, rows, cols) and maze[nr][nc] == 0:
            out.append((nr, nc))
    return out


def reconstruct_path(parent, goal):
    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path


def bfs(maze, start, goal):
    q = deque([start])
    parent = {start: None}
    visited = 0

    while q:
        cur = q.popleft()
        visited += 1
        if cur == goal:
            break
        for nb in neighbors(maze, cur):
            if nb not in parent:
                parent[nb] = cur
                q.append(nb)

    if goal not in parent:
        return None, visited

    return reconstruct_path(parent, goal), visited


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(maze, start, goal):
    pq = [(manhattan(start, goal), 0, start)]  # (f,g,node)
    parent = {start: None}
    gscore = {start: 0}
    visited = 0

    while pq:
        f, g, cur = heapq.heappop(pq)
        visited += 1
        if cur == goal:
            break

        for nb in neighbors(maze, cur):
            ng = g + 1
            if nb not in gscore or ng < gscore[nb]:
                gscore[nb] = ng
                parent[nb] = cur
                heapq.heappush(pq, (ng + manhattan(nb, goal), ng, nb))

    if goal not in parent:
        return None, visited

    return reconstruct_path(parent, goal), visited


# =======================
# توليد متاهة قابلة للحل
# =======================
def generate_solvable_maze(rows, cols, wall_prob, start, goal, max_tries=250):
    for _ in range(max_tries):
        maze = [[0] * cols for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if (r, c) in (start, goal):
                    maze[r][c] = 0
                else:
                    maze[r][c] = 1 if random.random() < wall_prob else 0

        path, _ = bfs(maze, start, goal)
        if path:
            return maze

    # fallback: أخف جدران
    maze = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if (r, c) not in (start, goal) and random.random() < wall_prob * 0.4:
                maze[r][c] = 1
    return maze


# =======================
# GUI
# =======================
class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver – BFS vs A* (Competition + Sound + Random Maze)")

        # إعدادات
        self.rows = 10
        self.cols = 10
        self.cell = 45

        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)

        self.wall_prob = 0.28
        self.maze = generate_solvable_maze(self.rows, self.cols, self.wall_prob, self.start, self.goal)

        # حالة عرض/أنيميشن
        self.running = False
        self.show_path = set()
        self.show_color = {}  # pos -> color

        # --------- واجهة: منطقة المتاهة (Scroll) ----------
        # إطار علوي ثابت للكانفاس + Scrollbars
        self.maze_area = ttk.Frame(root, padding=(10, 10, 10, 0))
        self.maze_area.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.maze_area, bg="#111111", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.vbar = ttk.Scrollbar(self.maze_area, orient="vertical", command=self.canvas.yview)
        self.vbar.grid(row=0, column=1, sticky="ns")

        self.hbar = ttk.Scrollbar(self.maze_area, orient="horizontal", command=self.canvas.xview)
        self.hbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

        self.maze_area.rowconfigure(0, weight=1)
        self.maze_area.columnconfigure(0, weight=1)

        # رسم يتم داخل canvas نفسه
        self.canvas.bind("<Button-1>", self.on_click_cell)

        # دعم عجلة الماوس للسكرول
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)       # ويندوز
        self.canvas.bind_all("<Shift-MouseWheel>", self.on_shiftwheel) # سكرول أفقي

        # --------- شريط معلومات ----------
        info_frame = ttk.Frame(root, padding=10)
        info_frame.pack(fill="x")

        self.info = tk.StringVar()
        self.info.set("جاهز. Generate لتوليد متاهة | Compare للتنافس | (كليك على خلية = جدار/فتح)")
        ttk.Label(info_frame, textvariable=self.info, font=("Segoe UI", 11)).pack(side="left")

        # --------- أزرار ثابتة تحت ----------
        controls = ttk.Frame(root, padding=(10, 0, 10, 10))
        controls.pack(fill="x")

        ttk.Button(controls, text="Generate Maze", command=self.generate_maze).pack(side="left", padx=5)
        ttk.Button(controls, text="Solve BFS", command=self.solve_bfs).pack(side="left", padx=5)
        ttk.Button(controls, text="Solve A*", command=self.solve_astar).pack(side="left", padx=5)
        ttk.Button(controls, text="Compare (BFS vs A*)", command=self.compare).pack(side="left", padx=5)
        ttk.Button(controls, text="Clear", command=self.clear).pack(side="left", padx=5)

        # --------- إعدادات (ثابتة تحت) ----------
        settings = ttk.Frame(root, padding=(10, 0, 10, 10))
        settings.pack(fill="x")

        ttk.Label(settings, text="Size:").pack(side="left")
        self.size_var = tk.StringVar(value="10")
        ttk.Combobox(settings, textvariable=self.size_var, values=["10", "15", "20"], width=4, state="readonly").pack(side="left", padx=6)

        ttk.Label(settings, text="Walls:").pack(side="left")
        self.wall_var = tk.DoubleVar(value=self.wall_prob)
        ttk.Scale(settings, from_=0.15, to=0.45, variable=self.wall_var).pack(side="left", padx=6, fill="x", expand=True)

        ttk.Label(settings, text="Speed:").pack(side="left", padx=(10, 0))
        self.speed_ms = tk.IntVar(value=50)
        ttk.Scale(settings, from_=10, to=140, variable=self.speed_ms).pack(side="left", padx=6)

        self.sound_on = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings, text="Sound", variable=self.sound_on).pack(side="left", padx=8)

        # أول رسم
        self.draw_grid()

    # -------------------------
    # أدوات
    # -------------------------
    def set_info(self, text):
        self.info.set(text)

    def play(self, kind):
        if not self.sound_on.get():
            return
        if kind == "ok":
            beep_ok(self.root)
        elif kind == "win":
            beep_win(self.root)
        elif kind == "tie":
            beep_tie(self.root)

    def clear(self, redraw=True):
        self.show_path = set()
        self.show_color = {}
        if redraw:
            self.draw_grid()
        self.set_info("تم المسح. جاهز.")

    # -------------------------
    # Scroll بالماوس
    # -------------------------
    def on_mousewheel(self, event):
        # سكرول عمودي
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_shiftwheel(self, event):
        # سكرول أفقي
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    # -------------------------
    # تفاعل: كليك لتبديل جدار
    # -------------------------
    def on_click_cell(self, event):
        if self.running:
            return

        # تحويل إحداثيات الكليك إلى إحداثيات داخل الكانفاس (مع السكرول)
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        c = int(x // self.cell)
        r = int(y // self.cell)

        if not in_bounds(r, c, self.rows, self.cols):
            return
        if (r, c) in (self.start, self.goal):
            return

        self.maze[r][c] = 0 if self.maze[r][c] == 1 else 1
        self.clear(redraw=False)
        self.draw_grid()

    # -------------------------
    # رسم المتاهة (على canvas)
    # -------------------------
    def draw_grid(self):
        self.canvas.delete("all")

        # حجم الكانفاس الفعلي (للscroll)
        width = self.cols * self.cell
        height = self.rows * self.cell
        self.canvas.config(scrollregion=(0, 0, width, height))

        for r in range(self.rows):
            for c in range(self.cols):
                x1 = c * self.cell
                y1 = r * self.cell
                x2 = x1 + self.cell
                y2 = y1 + self.cell
                pos = (r, c)

                if self.maze[r][c] == 1:
                    color = "#2c3e50"
                else:
                    color = "#ecf0f1"

                if pos in self.show_path:
                    color = self.show_color.get(pos, "#3498db")

                if pos == self.start:
                    color = "#2ecc71"
                if pos == self.goal:
                    color = "#e74c3c"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#111111")

        # كتابة S و G
        sr, sc = self.start
        gr, gc = self.goal
        self.canvas.create_text(sc * self.cell + self.cell / 2, sr * self.cell + self.cell / 2,
                                text="S", fill="black", font=("Segoe UI", 14, "bold"))
        self.canvas.create_text(gc * self.cell + self.cell / 2, gr * self.cell + self.cell / 2,
                                text="G", fill="white", font=("Segoe UI", 14, "bold"))

    # -------------------------
    # توليد متاهة
    # -------------------------
    def generate_maze(self):
        if self.running:
            return

        size = int(self.size_var.get())
        self.rows = size
        self.cols = size
        self.start = (0, 0)
        self.goal = (self.rows - 1, self.cols - 1)

        self.wall_prob = float(self.wall_var.get())
        self.maze = generate_solvable_maze(self.rows, self.cols, self.wall_prob, self.start, self.goal)

        self.clear(redraw=False)
        self.draw_grid()
        self.play("ok")
        self.set_info(f"تم توليد متاهة {size}x{size} | Walls={round(self.wall_prob, 2)} | (كليك لتعديل الجدران)")

    # -------------------------
    # تشغيل BFS/A*
    # -------------------------
    def solve_bfs(self):
        if self.running:
            return
        self.run_one("BFS")

    def solve_astar(self):
        if self.running:
            return
        self.run_one("A*")

    def run_one(self, algo_name):
        self.clear(redraw=False)

        t0 = time.perf_counter()
        if algo_name == "BFS":
            path, visited = bfs(self.maze, self.start, self.goal)
            color = "#3498db"  # أزرق
        else:
            path, visited = astar(self.maze, self.start, self.goal)
            color = "#9b59b6"  # بنفسجي
        t1 = time.perf_counter()

        if not path:
            self.draw_grid()
            self.play("tie")
            self.set_info(f"{algo_name}: لا يوجد حل (جرّبي Generate أو عدّلي الجدران)")
            return

        ms = round((t1 - t0) * 1000, 3)
        self.set_info(f"{algo_name} | visited={visited} | path_len={len(path)-1} | time_ms={ms}")
        self.play("ok")
        self.animate_path(path, color, on_done=None)

    # -------------------------
    # مقارنة (تنافس)
    # -------------------------
    def compare(self):
        if self.running:
            return

        t0 = time.perf_counter()
        bfs_path, bfs_vis = bfs(self.maze, self.start, self.goal)
        t1 = time.perf_counter()

        t2 = time.perf_counter()
        a_path, a_vis = astar(self.maze, self.start, self.goal)
        t3 = time.perf_counter()

        if not bfs_path or not a_path:
            self.play("tie")
            self.set_info("لا يوجد حل في هذه المتاهة. اضغطي Generate أو عدّلي الجدران.")
            return

        bfs_ms = round((t1 - t0) * 1000, 3)
        a_ms = round((t3 - t2) * 1000, 3)

        # الفائز: visited أقل، ثم time أقل
        if a_vis < bfs_vis:
            winner = "A*"
        elif a_vis > bfs_vis:
            winner = "BFS"
        else:
            if a_ms < bfs_ms:
                winner = "A*"
            elif bfs_ms < a_ms:
                winner = "BFS"
            else:
                winner = "TIE"

        self.clear(redraw=False)
        self.set_info("Competition: عرض BFS ثم A* ...")
        self.play("ok")

        def announce():
            if winner == "TIE":
                self.play("tie")
                self.set_info(f"RESULT: TIE 😄 | BFS: visited={bfs_vis}, ms={bfs_ms} | A*: visited={a_vis}, ms={a_ms}")
            else:
                self.play("win")
                self.set_info(f"WINNER: {winner} 🏆 | BFS: visited={bfs_vis}, ms={bfs_ms} | A*: visited={a_vis}, ms={a_ms}")

        # أنيميشن BFS ثم A* ثم إعلان
        def after_bfs():
            self.clear(redraw=False)
            self.draw_grid()
            self.set_info("Competition: الآن عرض A* ...")
            self.play("ok")
            self.animate_path(a_path, "#9b59b6", on_done=announce)

        self.animate_path(bfs_path, "#3498db", on_done=after_bfs)

    # -------------------------
    # أنيميشن مسار
    # -------------------------
    def animate_path(self, path, color, on_done):
        self.running = True
        self.show_path = set()
        self.show_color = {}

        speed = int(self.speed_ms.get())

        anim = [p for p in path if p not in (self.start, self.goal)]
        idx = 0

        def step():
            nonlocal idx
            if idx < len(anim):
                pos = anim[idx]
                self.show_path.add(pos)
                self.show_color[pos] = color
                self.draw_grid()
                idx += 1
                self.root.after(speed, step)
            else:
                self.running = False
                self.draw_grid()
                if on_done:
                    on_done()

        step()


def main():
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()