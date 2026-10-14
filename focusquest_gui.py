import math, os, random, hashlib
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

SEG = "Segoe UI"
def F(sz, b="bold"): return (SEG, sz, b) if b else (SEG, sz)
def _rgb(c): c = c.lstrip("#"); return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
def blend(c1, c2, t):
    a, b = _rgb(c1), _rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def fpts(pts, cx, cy, u=1): return [v for px, py in pts for v in (cx + px * u, cy + py * u)]
def draw_gradient(cv, w, h, c1, c2, tag="grad"):
    for y in range(0, h + 3, 3):
        cv.create_rectangle(0, y, w, y + 3, fill=blend(c1, c2, min(1, y / max(h, 1))), outline="", tags=tag)
    cv.tag_lower(tag)
def star_points(cx, cy, r_out, r_in=None):
    r_in = r_in or r_out * 0.45; pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5; r = r_out if i % 2 == 0 else r_in
        pts += [cx + r * math.cos(ang), cy + r * math.sin(ang)]
    return pts
def draw_puzzle(cv, x, y, s, fill, outline="", hole=None, tags=()):
    r = s * 0.2
    cv.create_rectangle(x, y, x + s, y + s, fill=fill, outline=outline, tags=tags)
    cv.create_oval(x + s / 2 - r, y - r, x + s / 2 + r, y + r, fill=fill, outline=outline, tags=tags)
    cv.create_oval(x + s - r, y + s / 2 - r, x + s + r, y + s / 2 + r, fill=fill, outline=outline, tags=tags)
    if hole: cv.create_oval(x - r, y + s / 2 - r, x + r, y + s / 2 + r, fill=hole, outline=hole, tags=tags)
def draw_logo(cv, cx, cy, u, rings=("#FFFFFF", "#3155D9", "#FFFFFF", "#F59E0B")):
    for radius, col in zip((45, 34, 23, 12), rings):
        cv.create_oval(cx - radius * u, cy - radius * u, cx + radius * u, cy + radius * u, fill=col, outline="")
    ex, ey = cx + 52 * u, cy - 52 * u
    cv.create_line(cx, cy, ex, ey, fill="#FBBF24", width=max(2, int(4 * u)))
    cv.create_polygon(cx, cy, cx + 14 * u, cy - 4 * u, cx + 4 * u, cy - 14 * u, fill="#FBBF24", outline="")
    cv.create_line(ex, ey, ex - 12 * u, ey, fill="#FBBF24", width=max(2, int(3 * u)))
    cv.create_line(ex, ey, ex, ey + 12 * u, fill="#FBBF24", width=max(2, int(3 * u)))

def draw_category_icon(cv, cat, cx, cy, size, accent, soft=None, backdrop=True):
    u = size / 100.0
    rect = lambda a, b, c, d, **k: cv.create_rectangle(cx + a * u, cy + b * u, cx + c * u, cy + d * u, **k)
    oval = lambda a, b, c, d, **k: cv.create_oval(cx + a * u, cy + b * u, cx + c * u, cy + d * u, **k)
    line = lambda a, b, c, d, **k: cv.create_line(cx + a * u, cy + b * u, cx + c * u, cy + d * u, **k)
    poly = lambda pts, **k: cv.create_polygon(*fpts(pts, cx, cy, u), **k)
    text = lambda x, y, t, sz, **k: cv.create_text(cx + x * u, cy + y * u, text=t, font=(SEG, max(7, int(sz * u)), "bold"), **k)
    w3 = max(2, int(3 * u))
    if backdrop and soft: oval(-50, -50, 50, 50, fill=soft, outline="")
    if cat == "Kids Puzzle":
        draw_puzzle(cv, cx - 38 * u, cy - 14 * u, 46 * u, accent, hole=soft if backdrop else None)
        draw_puzzle(cv, cx + 2 * u, cy - 4 * u, 36 * u, "#3B82F6")
        cv.create_polygon(*star_points(cx + 24 * u, cy - 26 * u, 14 * u), fill="#FACC15", outline="#CA8A04")
    elif cat == "Aptitude":
        rect(-27, -38, 27, 38, fill=accent, outline=""); rect(-20, -31, 20, -12, fill="#E0F2FE", outline="")
        text(0, -21, "123", 13, fill=accent)
        for r in range(3):
            for c in range(3):
                x, y = -20 + c * 15, -5 + r * 13
                rect(x, y, x + 11, y + 9, fill="#FACC15" if (r, c) == (2, 2) else "white", outline="")
    elif cat == "Reasoning":
        for ang in range(-60, 61, 30):
            a = math.radians(ang - 90)
            line(math.cos(a) * 36, -14 + math.sin(a) * 36, math.cos(a) * 46, -14 + math.sin(a) * 46, fill=accent, width=max(2, int(4 * u)))
        oval(-26, -40, 26, 12, fill="#FDE68A", outline=accent, width=w3)
        line(-8, -4, 0, -16, fill=accent, width=w3); line(0, -16, 8, -4, fill=accent, width=w3)
        rect(-12, 12, 12, 22, fill=accent, outline=""); rect(-9, 24, 9, 31, fill=accent, outline="")
    elif cat == "Programming":
        rect(-40, -34, 40, 22, fill="#0F172A", outline=accent, width=w3); text(0, -6, "</>", 20, fill="#34D399")
        rect(-6, 22, 6, 32, fill=accent, outline=""); rect(-22, 32, 22, 39, fill=accent, outline="")
    elif cat == "Interview":
        oval(-44, -38, 12, 6, fill=accent, outline=""); poly([(-26, 3), (-34, 26), (-8, 6)], fill=accent, outline="")
        text(-16, -16, "?", 26, fill="white"); oval(-4, -6, 44, 34, fill="white", outline=accent, width=w3)
        poly([(24, 31), (34, 48), (32, 30)], fill="white", outline=accent)
        for dx in (8, 20, 32): oval(dx - 3, 11, dx + 3, 17, fill=accent, outline="")
    else:
        draw_logo(cv, cx, cy, u * 0.8)

def draw_trophy(cv, cx, cy, u):
    gold, dark = "#FBBF24", "#B45309"; w5 = max(3, int(5 * u))
    cv.create_arc(cx - 48 * u, cy - 34 * u, cx - 14 * u, cy - 2 * u, start=90, extent=180, style="arc", outline=dark, width=w5)
    cv.create_arc(cx + 14 * u, cy - 34 * u, cx + 48 * u, cy - 2 * u, start=270, extent=180, style="arc", outline=dark, width=w5)
    cv.create_polygon(*fpts([(-27, -42), (27, -42), (22, 0), (10, 16), (-10, 16), (-22, 0)], cx, cy, u), fill=gold, outline=dark, width=2)
    cv.create_rectangle(cx - 5 * u, cy + 16 * u, cx + 5 * u, cy + 30 * u, fill=dark, outline="")
    cv.create_rectangle(cx - 22 * u, cy + 30 * u, cx + 22 * u, cy + 40 * u, fill=dark, outline="")
    cv.create_polygon(*star_points(cx, cy - 18 * u, 12 * u), fill="white", outline="")

def draw_mascot(cv, cx, cy, u):
    oval = lambda a, b, c, d, **k: cv.create_oval(cx + a * u, cy + b * u, cx + c * u, cy + d * u, **k)
    poly = lambda pts, **k: cv.create_polygon(*fpts(pts, cx, cy, u), **k)
    body, dark = "#F59E0B", "#D97706"
    poly([(-32, -30), (-22, -50), (-8, -34)], fill=body, outline=""); poly([(32, -30), (22, -50), (8, -34)], fill=body, outline="")
    oval(-46, -2, -26, 34, fill=dark, outline=""); oval(26, -2, 46, 34, fill=dark, outline="")
    oval(-38, -40, 38, 44, fill=body, outline=dark, width=2); oval(-22, 2, 22, 40, fill="#FEF3C7", outline="")
    for fx in (-10, 0, 10):
        cv.create_line(cx + (fx - 4) * u, cy + 20 * u, cx + fx * u, cy + 26 * u, cx + (fx + 4) * u, cy + 20 * u, fill="#FCD34D", width=2)
    oval(-27, -28, -1, -2, fill="white", outline="#92400E", width=2); oval(1, -28, 27, -2, fill="white", outline="#92400E", width=2)
    oval(-19, -21, -7, -8, fill="#1E293B", outline=""); oval(7, -21, 19, -8, fill="#1E293B", outline="")
    oval(-15, -19, -11, -15, fill="white", outline=""); oval(11, -19, 15, -15, fill="white", outline="")
    poly([(-6, -4), (6, -4), (0, 9)], fill="#EA580C", outline="")
    oval(-22, 42, -6, 52, fill="#EA580C", outline=""); oval(6, 42, 22, 52, fill="#EA580C", outline="")
    poly([(-36, -44), (0, -58), (36, -44), (0, -32)], fill="#1E293B", outline="")
    cv.create_rectangle(cx - 16 * u, cy - 42 * u, cx + 16 * u, cy - 33 * u, fill="#334155", outline="")
    cv.create_line(cx + 30 * u, cy - 45 * u, cx + 36 * u, cy - 28 * u, fill="#FACC15", width=3)
    oval(32, -30, 40, -22, fill="#FACC15", outline="")

def draw_confetti(cv, w, h, seed=3, count=70):
    rnd = random.Random(seed); colors = ["#F59E0B", "#EF4444", "#22C55E", "#3B82F6", "#A855F7", "#FFFFFF", "#FACC15"]
    for _ in range(count):
        x, y = rnd.randint(0, w), rnd.randint(0, h); s = rnd.randint(4, 9)
        if rnd.random() < 0.5: cv.create_rectangle(x, y, x + s, y + s * 0.6, fill=rnd.choice(colors), outline="")
        else: cv.create_oval(x, y, x + s, y + s, fill=rnd.choice(colors), outline="")

def draw_podium(cv, w, h, top3, me=None):
    cv.delete("all")
    if w < 150 or h < 200: return
    draw_confetti(cv, w, h, seed=5, count=45)
    cv.create_text(w / 2, 24, text="Hall of Fame", fill="#92400E", font=F(18))
    if not top3: cv.create_text(w / 2, 52, text="No champions yet - be the first!", fill="#64748B", font=F(11, "italic"))
    base = h - 14; unit = max(0.8, min(1.0, (h - 150) / 170)); gap = min(150, w * 0.28); bw = min(62, gap / 2 - 4)
    spots = [(1, w / 2, 165 * unit, "#FBBF24", "#B45309", "#F472B6"), (2, w / 2 - gap, 130 * unit, "#94A3B8", "#475569", "#60A5FA"),
             (3, w / 2 + gap, 100 * unit, "#D97706", "#92400E", "#34D399")]
    for rank, cx, bh, col, dark, avatar in spots:
        entry = top3[rank - 1] if rank - 1 < len(top3) else None; yt = base - bh
        cv.create_rectangle(cx - bw, yt, cx + bw, base, fill=col, outline=dark, width=2)
        cv.create_rectangle(cx - bw, yt, cx + bw, yt + 9, fill=blend(col, "#FFFFFF", 0.4), outline="")
        cv.create_text(cx, yt + 26, text=str(rank), fill="white", font=F(24)); ay = yt - 38
        if entry:
            name, pct = entry; is_me = name == me
            cv.create_oval(cx - 27, ay - 27, cx + 27, ay + 27, fill=avatar, outline="#22C55E" if is_me else "white", width=4)
            cv.create_text(cx, ay, text=name[:1].upper(), fill="white", font=F(22))
            shown = name if len(name) <= 11 else name[:10] + "…"
            cv.create_text(cx, yt + 51, text=shown + (" (you)" if is_me else ""), fill="white", font=F(10))
            cv.create_text(cx, yt + 71, text=f"{pct:.0f}%", fill="white", font=F(11))
            if rank == 1:
                cv.create_polygon(*fpts([(-18, -24), (-18, -42), (-9, -33), (0, -48), (9, -33), (18, -42), (18, -24)], cx, ay),
                                  fill="#FACC15", outline="#CA8A04", width=2)
        else:
            cv.create_oval(cx - 27, ay - 27, cx + 27, ay + 27, fill="#E2E8F0", outline="white", width=4)
            cv.create_text(cx, ay, text="?", fill="#94A3B8", font=F(22)); cv.create_text(cx, yt + 51, text="waiting...", fill="white", font=F(9, "italic"))

def draw_badge(cv, cx, cy, r, kind, unlocked):
    colors = {"first": "#F59E0B", "five": "#3B82F6", "eighty": "#10B981", "perfect": "#A855F7"}
    col = colors[kind] if unlocked else "#CBD5E1"; dark = blend(col, "#000000", 0.25)
    cv.create_polygon(cx - r * .6, cy + r * .4, cx - r * .1, cy + r * .4, cx - r * .35, cy + r * 1.35, fill=dark, outline="")
    cv.create_polygon(cx + r * .6, cy + r * .4, cx + r * .1, cy + r * .4, cx + r * .35, cy + r * 1.35, fill=dark, outline="")
    cv.create_oval(cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4, fill=blend(col, "#FFFFFF", 0.6), outline="")
    cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline="white", width=3)
    if kind == "first": cv.create_polygon(*star_points(cx, cy, r * .6), fill="white", outline="")
    elif kind == "five": cv.create_text(cx, cy, text="5", fill="white", font=F(int(r * .9)))
    elif kind == "eighty": cv.create_text(cx, cy, text="80%", fill="white", font=F(int(r * .5)))
    else: cv.create_polygon(*fpts([(-.5, .3), (-.55, -.35), (-.25, -.05), (0, -.5), (.25, -.05), (.55, -.35), (.5, .3)], cx, cy, r), fill="white", outline="")

def draw_score_chart(cv, w, h, results, themes):
    cv.delete("all")
    if w < 150 or h < 140: return
    left, right, top, bottom = 46, w - 18, 20, h - 42
    for val in (0, 50, 100):
        y = bottom - (bottom - top) * val / 100
        if val: cv.create_line(left, y, right, y, fill="#E2E8F0", dash=(4, 3))
        else: cv.create_line(left, y, right, y, fill="#CBD5E1", width=2)
        cv.create_text(left - 8, y, text=f"{val}%", anchor="e", fill="#94A3B8", font=F(8, None))
    if not results:
        cv.create_text((left + right) / 2, (top + bottom) / 2, fill="#64748B", font=F(11, "italic"), text="Play a game to see your colourful chart!")
        return
    slot = (right - left) / len(results); bw = min(46, slot * 0.6)
    for i, (cat, diff, score, pct) in enumerate(results):
        th = themes.get(cat, themes["Kids Puzzle"]); cx = left + slot * (i + .5); y = bottom - (bottom - top) * min(pct, 100) / 100
        cv.create_rectangle(cx - bw / 2, y, cx + bw / 2, bottom, fill=th["accent"], outline="")
        if bottom - y > 8: cv.create_rectangle(cx - bw / 2, y, cx + bw / 2, y + 5, fill=blend(th["accent"], "#FFFFFF", 0.4), outline="")
        cv.create_text(cx, y - 9, text=f"{pct:.0f}%", fill=th["accent"], font=F(9))
        draw_category_icon(cv, cat, cx, bottom + 21, 28, th["accent"], th["soft"])

def draw_cloud(cv, x, y, s=1.0):
    for dx, dy, r in [(0, 0, 18), (22, -10, 24), (48, 0, 18), (24, 8, 20)]:
        cv.create_oval(x + (dx - r) * s, y + (dy - r) * s, x + (dx + r) * s, y + (dy + r) * s, fill="white", outline="")
def draw_balloon(cv, x, y, r, color):
    cv.create_line(x, y + r * 1.3, x + 7, y + r * 1.3 + 20, x - 7, y + r * 1.3 + 42, x, y + r * 1.3 + 64, fill="#94A3B8", width=2, smooth=True)
    cv.create_polygon(x - 5, y + r * 1.3, x + 5, y + r * 1.3, x, y + r * 1.5, fill=color, outline="")
    cv.create_oval(x - r, y - r * 1.2, x + r, y + r * 1.3, fill=color, outline="")
    cv.create_oval(x - r * .55, y - r * .95, x - r * .15, y - r * .45, fill=blend(color, "#FFFFFF", 0.55), outline="")
def draw_block(cv, x, y, s, letter, color):
    cv.create_rectangle(x - s / 2 + 3, y - s / 2 + 3, x + s / 2 + 3, y + s / 2 + 3, fill=blend(color, "#000000", 0.25), outline="")
    cv.create_rectangle(x - s / 2, y - s / 2, x + s / 2, y + s / 2, fill=color, outline="white", width=2)
    cv.create_text(x, y, text=letter, fill="white", font=F(int(s * .5)))
def draw_pencil(cv, cx, cy, L, angle_deg):
    a = math.radians(angle_deg); ca, sa = math.cos(a), math.sin(a); hw = L * 0.07
    def poly(pts, fill): cv.create_polygon(*[v for px, py in pts for v in (cx + px * ca - py * sa, cy + px * sa + py * ca)], fill=fill, outline="")
    poly([(-L / 2 - hw, -hw), (-L / 2, -hw), (-L / 2, hw), (-L / 2 - hw, hw)], "#F9A8D4")
    poly([(-L / 2, -hw), (-L / 2 + hw, -hw), (-L / 2 + hw, hw), (-L / 2, hw)], "#CBD5E1")
    poly([(-L / 2 + hw, -hw), (L / 2 - hw * 2, -hw), (L / 2 - hw * 2, hw), (-L / 2 + hw, hw)], "#FACC15")
    poly([(L / 2 - hw * 2, -hw), (L / 2, 0), (L / 2 - hw * 2, hw)], "#FDE68A")
    poly([(L / 2 - hw * .7, -hw * .3), (L / 2, 0), (L / 2 - hw * .7, hw * .3)], "#334155")
def draw_books(cv, cx, cy, s=1.0):
    for i, (col, wd) in enumerate([("#3B82F6", 54), ("#F59E0B", 46), ("#10B981", 52)]):
        yb = cy + 22 * s - i * 16 * s
        cv.create_rectangle(cx - wd / 2 * s, yb - 15 * s, cx + wd / 2 * s, yb, fill=col, outline="white", width=2)
        cv.create_line(cx - wd / 2 * s + 7, yb - 7.5 * s, cx + wd / 2 * s - 7, yb - 7.5 * s, fill="white", width=2)
def draw_grad_cap(cv, cx, cy, u=1.0):
    cv.create_polygon(*fpts([(-20, 4), (-20, 20), (0, 28), (20, 20), (20, 4), (0, 12)], cx, cy, u), fill="#334155", outline="")
    cv.create_polygon(*fpts([(-34, -4), (0, -20), (34, -4), (0, 12)], cx, cy, u), fill="#1E293B", outline="")
    cv.create_line(cx + 30 * u, cy - 3 * u, cx + 30 * u, cy + 20 * u, fill="#FACC15", width=3)
    cv.create_oval(cx + 26 * u, cy + 18 * u, cx + 34 * u, cy + 26 * u, fill="#FACC15", outline="")
def draw_stars(cv, cx, cy, filled, total=3, size=16, gap=44):
    start = cx - (total - 1) * gap / 2
    for i in range(total):
        on = i < filled
        cv.create_polygon(*star_points(start + i * gap, cy, size), fill="#FACC15" if on else "#E5E7EB", outline="#CA8A04" if on else "#CBD5E1", width=2)


class FocusQuestApp(tk.Tk):
    """FocusQuest: interactive puzzle and learning platform (Python + Tkinter + MySQL)."""
    BG, CARD, TEXT, MUTED = "#F5F7FB", "#FFFFFF", "#172033", "#667085"
    PRIMARY, SUCCESS, DANGER, BORDER = "#3155D9", "#159570", "#D64545", "#D9DFEA"
    THEMES = {
        "Kids Puzzle": {"bg": "#FFF7E8", "accent": "#F59E0B", "soft": "#FFF0C7", "symbol": "◆"},
        "Aptitude": {"bg": "#EEF6FF", "accent": "#2563EB", "soft": "#DCEBFF", "symbol": "∑"},
        "Reasoning": {"bg": "#F3EEFF", "accent": "#7C3AED", "soft": "#E8DFFF", "symbol": "◇"},
        "Programming": {"bg": "#ECFDF5", "accent": "#059669", "soft": "#D5F8EA", "symbol": "</>"},
        "Interview": {"bg": "#FFF1F2", "accent": "#E11D48", "soft": "#FFE0E5", "symbol": "?"},
    }
    DESCRIPTIONS = {"Kids Puzzle": "Number, pattern, memory, logic", "Aptitude": "Numbers & speed maths",
                    "Reasoning": "Logical & analytical thinking", "Programming": "Coding & CS basics", "Interview": "Basic interview questions"}
    QUESTIONS_PER_GAME = 10
    CHEERS = ["Ready for today's challenge?", "Sharpen your logic and problem-solving skills!", "Kids play puzzles - students practise and improve!",
              "Pick a category and let's begin!", "Every question makes you smarter!"]
    STUDENT_SYMBOLS = {"Aptitude": ["+", "−", "×", "÷", "π", "√", "%", "="], "Reasoning": ["?", "∞", "△", "□", "≠", "◇", "∴", "!"],
                       "Programming": ["{ }", "</>", "01", "( )", "[ ]", "#", "&&", ";"], "Interview": ["?", "Q&A", "✓", "CV", "HR", "!", "★", "?"]}

    def __init__(self):
        super().__init__()
        self.title("FocusQuest - Learning Challenge Platform"); self.geometry("1200x720"); self.minsize(1050, 650); self.configure(bg=self.BG)
        self.current_user_id = self.current_username = self.timer_id = self.anim_id = None
        self.questions, self.answers = [], {}
        self.current_index = self.score = self.correct = self.incorrect = self.unattempted = self.max_points = 0
        self.time_left, self.submitted, self.category, self.difficulty = 10, False, "Kids Puzzle", "Easy"
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("TButton", font=F(11), padding=(14, 9)); style.configure("TLabel", font=F(11, None), background=self.CARD, foreground=self.TEXT)
        style.configure("TEntry", font=F(12, None), padding=8); style.configure("TCombobox", font=F(11, None))
        style.configure("Accent.TButton", background=self.PRIMARY, foreground="white")
        style.map("Accent.TButton", background=[("active", "#2644B5"), ("pressed", "#2644B5")], foreground=[("active", "white")])
        style.configure("Horizontal.TProgressbar", troughcolor="#E2E8F0", background=self.PRIMARY, thickness=12)
        self.show_login()

    # ---------------- Database ----------------
    def db_connect(self): return mysql.connector.connect(host="localhost", user="root", password="", database="focusquest")
    @staticmethod
    def hash_password(p): return hashlib.sha256(p.encode("utf-8")).hexdigest()

    def _query(self, sql, params, many=True):
        db = self.db_connect(); cur = db.cursor(); cur.execute(sql, params)
        rows = cur.fetchall() if many else cur.fetchone(); cur.close(); db.close(); return rows

    def fetch_user_stats(self):
        try:
            g, b, a = self._query("SELECT COUNT(*), COALESCE(MAX(percentage),0), COALESCE(AVG(percentage),0) FROM results WHERE user_id=%s",
                                  (self.current_user_id,), many=False)
            return int(g), float(b), float(a)
        except Exception: return 0, 0.0, 0.0

    def fetch_leaderboard(self, limit=5):
        try:
            return [(n, float(b)) for n, b in self._query("""SELECT u.username, MAX(r.percentage) AS best FROM results r
                    JOIN users u ON u.user_id = r.user_id GROUP BY u.user_id, u.username ORDER BY best DESC LIMIT %s""", (int(limit),))]
        except Exception: return []

    def fetch_recent(self, limit=3):
        sql = "SELECT category, difficulty, score, percentage FROM results WHERE user_id=%s {} LIMIT {}"
        for order in ("ORDER BY result_id DESC", ""):
            try: return [(c, d, int(s), float(p)) for c, d, s, p in self._query(sql.format(order, int(limit)), (self.current_user_id,))]
            except Exception: continue
        return []

    # ---------------- Common UI ----------------
    def _cancel(self, attr):
        if getattr(self, attr):
            try: self.after_cancel(getattr(self, attr))
            except Exception: pass
            setattr(self, attr, None)

    def clear_window(self):
        self._cancel("anim_id"); self._cancel("timer_id")
        for widget in self.winfo_children(): widget.destroy()

    def card(self, parent, **kw): return tk.Frame(parent, bg=self.CARD, bd=0, highlightthickness=1, highlightbackground=self.BORDER, **kw)
    def lbl(self, parent, text, sz=11, b="bold", bg=None, fg=None, **kw):
        return tk.Label(parent, text=text, font=F(sz, b), bg=bg or self.CARD, fg=fg or self.TEXT, **kw)
    def logo_rings(self): return (self.PRIMARY, "#FFFFFF", self.PRIMARY, "#F59E0B")

    def header(self, parent, subtitle="Interactive Puzzle & Learning Challenge", logout=False):
        frame = tk.Frame(parent, bg=self.CARD, height=72); frame.pack(fill="x"); frame.pack_propagate(False)
        logo = tk.Canvas(frame, width=48, height=48, bg=self.CARD, highlightthickness=0); logo.pack(side="left", padx=(26, 0))
        draw_logo(logo, 22, 26, 0.42, rings=self.logo_rings())
        self.lbl(frame, "FocusQuest", 25, fg=self.PRIMARY).pack(side="left", padx=(8, 0))
        self.lbl(frame, subtitle, 10, None, fg=self.MUTED).pack(side="left", padx=14)
        if logout: ttk.Button(frame, text="Logout", command=self.show_login).pack(side="right", padx=26)
        tk.Frame(parent, bg=self.BORDER, height=1).pack(fill="x")
        return frame

    # ---------------- Animated backgrounds ----------------
    def _group(self, cv, draw):
        before = set(cv.find_all()); draw(); tag = f"fl{self._float_n}"
        for item in set(cv.find_all()) - before: cv.addtag_withtag(tag, item)
        self._float_n += 1

    def _background_photo(self, w, h):
        base = os.path.dirname(os.path.abspath(__file__))
        for name in ("login_bg.jpg", "login_bg.jpeg", "login_bg.png"):
            path = os.path.join(base, "assets", name)
            if not os.path.exists(path): continue
            try:
                from PIL import Image, ImageTk
                img = Image.open(path).convert("RGB"); scale = max(w / img.width, h / img.height)
                img = img.resize((int(img.width * scale) + 1, int(img.height * scale) + 1))
                left, top = (img.width - w) // 2, (img.height - h) // 2
                return ImageTk.PhotoImage(img.crop((left, top, left + w, top + h)))
            except Exception:
                if name.endswith(".png"):
                    try: return tk.PhotoImage(file=path)
                    except tk.TclError: pass
        return None

    def draw_auth_background(self, cv):
        cv.delete("all"); w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50 or h < 50: return
        self._float_n = 0; photo = self._background_photo(w, h)
        if photo:
            self._bg_photo = photo; cv.create_image(0, 0, image=photo, anchor="nw")
        else:
            draw_gradient(cv, w, h, "#E3EAFF", "#FFEFE0")
            for fx, fy, r, col in [(0.04, 0.08, 230, "#C7D2FE"), (0.97, 0.95, 260, "#FBCFE8"), (0.93, 0.04, 170, "#FDE68A"), (0.08, 0.97, 190, "#A7F3D0")]:
                cx, cy = fx * w, fy * h
                cv.create_oval(cx - r, cy - r, cx + r, cy + r, fill=blend(col, "#FFFFFF", 0.45), outline="")
            for x in range(20, w, 40):
                for y in range(20, h, 40): cv.create_oval(x - 1, y - 1, x + 1, y + 1, fill="#C9D3F0", outline="")
            for cat, fx, fy, size in [("Kids Puzzle", .11, .20, 150), ("Aptitude", .89, .20, 140), ("Reasoning", .11, .80, 140),
                                      ("Programming", .89, .80, 150), ("Interview", .22, .48, 76), ("Aptitude", .78, .50, 76)]:
                th = self.THEMES[cat]
                self._group(cv, lambda c=cat, x=fx * w, y=fy * h, sz=size, t=th: draw_category_icon(cv, c, x, y, sz, t["accent"], t["soft"]))
            for fx, fy, s, col in [(.33, .05, 36, "#FDE68A"), (.68, .06, 40, "#A7F3D0"), (.36, .93, 40, "#C7D2FE"),
                                   (.66, .92, 36, "#FBCFE8"), (.035, .50, 46, "#C7D2FE"), (.955, .50, 46, "#FBCFE8")]:
                self._group(cv, lambda x=fx * w, y=fy * h, sz=s, c=col: draw_puzzle(cv, x, y, sz, c))
            for fx, fy in [(.2, .36), (.8, .34), (.18, .66), (.82, .64), (.5, .04)]:
                self._group(cv, lambda x=fx * w, y=fy * h: cv.create_polygon(*star_points(x, y, 13), fill="#FACC15", outline="#CA8A04"))
            for txt, fx, fy, sz, col in [("?", .26, .20, 34, "#A5B4FC"), ("∑", .74, .18, 34, "#93C5FD"), ("</>", .27, .80, 24, "#6EE7B7"),
                                         ("÷", .73, .82, 34, "#FDA4AF"), ("{ }", .17, .62, 26, "#C4B5FD"), ("+", .84, .62, 34, "#FCD34D")]:
                self._group(cv, lambda t=txt, x=fx * w, y=fy * h, z=sz, c=col: cv.create_text(x, y, text=t, fill=c, font=F(z)))
        cv.create_rectangle(20, 16, 236, 72, fill="white", outline=self.BORDER)
        draw_logo(cv, 46, 45, 0.42, rings=self.logo_rings())
        cv.create_text(70, 44, text="FocusQuest", anchor="w", fill=self.PRIMARY, font=F(18))
        cv.create_rectangle(w / 2 - 290, h - 46, w / 2 + 290, h - 14, fill="white", outline=self.BORDER)
        cv.create_text(w / 2, h - 30, fill=self.MUTED, font=F(10, None), text="Puzzles for Kids  •  Practice for Students     |     Python + Tkinter + MySQL")

    def animate_auth(self):
        cv = getattr(self, "auth_canvas", None)
        try:
            if cv is not None and cv.winfo_exists():
                self._t += 0.05
                for i in range(self._float_n):
                    a = self._t + i * 0.9; cv.move(f"fl{i}", 0, 14 * (math.sin(a) - math.sin(a - 0.05)))
                self.anim_id = self.after(50, self.animate_auth)
        except tk.TclError: pass

    def _bg_canvas(self, color, painter):
        cv = tk.Canvas(self, highlightthickness=0, bg=color); cv.place(x=0, y=0, relwidth=1, relheight=1)
        cv.bind("<Configure>", lambda e: painter(cv)); self.auth_canvas = cv
        self._t = 0.0; self._float_n = 0; self.animate_auth(); return cv

    def auth_layout(self):
        self.clear_window(); self.configure(bg=self.BG); self._bg_canvas("#E3EAFF", self.draw_auth_background)

    def sky_background(self): self._bg_canvas("#CFEBFF", self.draw_dash_background)

    def auth_card(self, w, h):
        shadow = tk.Frame(self, bg="#B8C2E0"); shadow.place(relx=0.5, rely=0.5, anchor="center", x=7, y=9, width=w, height=h)
        form = self.card(self, width=w, height=h); form.place(relx=0.5, rely=0.5, anchor="center"); form.pack_propagate(False)
        return form

    # ---------------- Login / Registration ----------------
    def show_login(self):
        self.auth_layout(); form = self.auth_card(440, 440)
        self.lbl(form, "Welcome Back", 25).pack(pady=(40, 5))
        self.lbl(form, "Login to continue your challenge", 11, None, fg=self.MUTED).pack(pady=(0, 26))
        self.lbl(form, "Username").pack(anchor="w", padx=55)
        username = ttk.Entry(form, width=36); username.pack(padx=55, pady=(5, 16))
        self.lbl(form, "Password").pack(anchor="w", padx=55)
        password = ttk.Entry(form, width=36, show="•"); password.pack(padx=55, pady=(5, 20))

        def login():
            u, p = username.get().strip(), password.get()
            if not u or not p: return messagebox.showwarning("Required", "Please enter username and password.")
            try:
                row = self._query("SELECT user_id, username FROM users WHERE username=%s AND password=%s", (u, self.hash_password(p)), many=False)
                if row: self.current_user_id, self.current_username = row; self.show_dashboard()
                else: messagebox.showerror("Login Failed", "Invalid username or password.")
            except Error as e: messagebox.showerror("Database Error", str(e))

        ttk.Button(form, text="LOGIN", style="Accent.TButton", command=login).pack(fill="x", padx=55, pady=5)
        ttk.Button(form, text="CREATE NEW ACCOUNT", command=self.show_register).pack(fill="x", padx=55, pady=10)
        self.lbl(form, "Demo: admin / admin123", 9, None, fg=self.MUTED).pack(pady=8)
        username.focus_set(); password.bind("<Return>", lambda e: login())

    def show_register(self):
        self.auth_layout(); form = self.auth_card(480, 575)
        self.lbl(form, "Create Account", 26, fg=self.PRIMARY).pack(pady=(32, 5))
        self.lbl(form, "Start your FocusQuest journey", 11, None, fg=self.MUTED).pack(pady=(0, 22))
        fields = []
        for label in ["Full Name", "Username", "Password", "Confirm Password"]:
            self.lbl(form, label).pack(anchor="w", padx=55)
            ent = ttk.Entry(form, width=38, show="•" if "Password" in label else ""); ent.pack(padx=55, pady=(4, 13)); fields.append(ent)

        def register():
            full_name, username, password, confirm = [x.get().strip() for x in fields]
            if not all([full_name, username, password, confirm]): return messagebox.showwarning("Required", "Please fill all fields.")
            if password != confirm: return messagebox.showerror("Password", "Passwords do not match.")
            try:
                db = self.db_connect(); cur = db.cursor()
                cur.execute("INSERT INTO users (username,password,full_name) VALUES (%s,%s,%s)", (username, self.hash_password(password), full_name))
                db.commit(); cur.close(); db.close()
                messagebox.showinfo("Success", "Account created successfully."); self.show_login()
            except Error as e:
                messagebox.showerror("Registration Error", "This username is already taken." if getattr(e, "errno", None) == 1062 else str(e))

        ttk.Button(form, text="REGISTER", style="Accent.TButton", command=register).pack(fill="x", padx=55, pady=8)
        ttk.Button(form, text="BACK TO LOGIN", command=self.show_login).pack(fill="x", padx=55)

    # ---------------- Dashboard ----------------
    def stat_box(self, parent, value, title, color):
        box = self.card(parent, width=118, height=66); box.pack(side="left", padx=(10, 0)); box.pack_propagate(False)
        tk.Frame(box, bg=color, width=5).pack(side="left", fill="y")
        inner = tk.Frame(box, bg=self.CARD); inner.pack(side="left", fill="both", expand=True)
        self.lbl(inner, value, 18, fg=color).pack(pady=(8, 0)); self.lbl(inner, title, 9, None, fg=self.MUTED).pack()

    def draw_dash_background(self, cv):
        cv.delete("all"); w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50 or h < 50: return
        self._float_n = 0; draw_gradient(cv, w, h, "#BFE6FF", "#FFF6D6"); sx, sy = w - 170, 42
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            cv.create_line(sx + math.cos(a) * 36, sy + math.sin(a) * 36, sx + math.cos(a) * 50, sy + math.sin(a) * 50, fill="#FBBF24", width=4)
        cv.create_oval(sx - 28, sy - 28, sx + 28, sy + 28, fill="#FDE047", outline="#FACC15", width=3)
        cv.create_oval(-w * 0.1, h - 250, w * 0.65, h + 260, fill="#BDE5A8", outline="")
        cv.create_oval(w * 0.35, h - 220, w * 1.1, h + 260, fill="#CDEEBB", outline="")
        for fx, fy, sc in [(.36, 34, .9), (.58, 22, .7), (.80, 60, .6), (.02, 150, .8), (.93, 160, .8)]:
            self._group(cv, lambda x=fx * w, y=fy, s=sc: draw_cloud(cv, x, y, s))
        for txt, fx, col in [("A", .27, "#F87171"), ("1", .45, "#60A5FA"), ("B", .68, "#34D399"), ("2", .74, "#FBBF24")]:
            def bubble(t=txt, x=fx * w, c=col):
                cv.create_oval(x - 17, 22, x + 17, 56, fill=c, outline="white", width=3); cv.create_text(x, 39, text=t, fill="white", font=F(15))
            self._group(cv, bubble)
        for fx in (.33, .52, .63):
            self._group(cv, lambda x=fx * w: cv.create_polygon(*star_points(x, 62, 9), fill="#FACC15", outline="#CA8A04"))
        draw_logo(cv, 44, 38, 0.5, rings=self.logo_rings())
        cv.create_text(80, 32, text="FocusQuest", anchor="w", fill=self.PRIMARY, font=F(24))
        cv.create_text(82, 60, text="For Kids & Students", anchor="w", fill="#1E3A8A", font=F(10))

    def build_tile(self, parent, cat, var, on_select):
        th = self.THEMES[cat]
        cv = tk.Canvas(parent, width=110, height=150, bg=th["bg"], highlightthickness=4, cursor="hand2"); state = {"hover": False}

        def paint(event=None):
            w, h = cv.winfo_width(), cv.winfo_height()
            if w < 40 or h < 40: w, h = 110, 150
            sel = var.get() == cat; cv.delete("all")
            cv.config(bg=th["accent"] if sel else th["bg"],
                      highlightbackground=th["accent"] if (sel or state["hover"]) else blend(th["accent"], "#FFFFFF", 0.55))
            size = min(w * 0.78, h * 0.5); cy = h * 0.32
            cv.create_oval(w / 2 - size / 2 - 6, cy - size / 2 - 6, w / 2 + size / 2 + 6, cy + size / 2 + 6, fill="white" if sel else th["soft"], outline="")
            draw_category_icon(cv, cat, w / 2, cy, size * 0.92, th["accent"], th["soft"], backdrop=False)
            cv.create_text(w / 2, h * 0.67, text=cat, fill="white" if sel else th["accent"], font=F(int(max(11, min(16, w / 9)))))
            cv.create_text(w / 2, h * 0.84, text=self.DESCRIPTIONS[cat], width=max(60, w - 22), fill="white" if sel else self.MUTED, font=F(9, None), justify="center")
            if sel:
                cv.create_oval(w - 38, 8, w - 8, 38, fill="#FACC15", outline="white", width=2)
                cv.create_text(w - 23, 23, text="✓", fill="#7C2D12", font=F(13))

        def hover(flag): state["hover"] = flag; paint()
        cv.paint = paint
        cv.bind("<Configure>", paint); cv.bind("<Button-1>", lambda e: on_select(cat))
        cv.bind("<Enter>", lambda e: hover(True)); cv.bind("<Leave>", lambda e: hover(False))
        return cv

    def nav_card(self, parent, title, sub, bg, accent, icon, command, width=250):
        cv = tk.Canvas(parent, width=width, height=195, bg=bg, highlightthickness=3, highlightbackground=accent, cursor="hand2")
        icon(cv, width / 2)
        cv.create_text(width / 2, 122, text=title, font=F(17), fill=accent); cv.create_text(width / 2, 144, text=sub, font=F(10, None), fill=self.MUTED)
        cv.create_rectangle(width / 2 - 50, 158, width / 2 + 50, 182, fill=accent, outline="")
        cv.create_text(width / 2, 170, text="Open  ➜", fill="white", font=F(10))
        cv.bind("<Button-1>", lambda e: command()); cv.bind("<Enter>", lambda e: cv.config(bg=blend(bg, "#FFFFFF", 0.7)))
        cv.bind("<Leave>", lambda e: cv.config(bg=bg))
        return cv

    def show_dashboard(self):
        self.clear_window(); self.configure(bg=self.BG); self.sky_background()
        ttk.Button(self, text="Logout", command=self.show_login).place(relx=1.0, x=-28, y=16, anchor="ne")
        games, best, avg = self.fetch_user_stats()
        rank = "Super Master" if games >= 10 else "Champion" if games >= 5 else "Explorer" if games >= 1 else "Beginner"
        banner = self.card(self); banner.pack(fill="x", padx=30, pady=(80, 8))
        mas = tk.Canvas(banner, width=110, height=104, bg=self.CARD, highlightthickness=0); mas.pack(side="left", padx=(16, 6), pady=6)
        draw_mascot(mas, 55, 58, 0.92)
        txt = tk.Frame(banner, bg=self.CARD); txt.pack(side="left", padx=8)
        row = tk.Frame(txt, bg=self.CARD); row.pack(anchor="w")
        self.lbl(row, f"Hello, {self.current_username}! 👋", 22).pack(side="left")
        self.lbl(row, f"  ★ {rank}  ", 10, bg="#FEF3C7", fg="#B45309").pack(side="left", padx=12)
        self.lbl(txt, "🦉 " + random.choice(self.CHEERS), 12, None, bg="#E0F2FE", fg="#075985", padx=12, pady=5).pack(anchor="w", pady=(6, 0))
        stats = tk.Frame(banner, bg=self.CARD); stats.pack(side="right", padx=16)
        self.stat_box(stats, str(games), "Games Played", self.PRIMARY); self.stat_box(stats, f"{best:.0f}%", "Best Score", self.SUCCESS)
        self.stat_box(stats, f"{avg:.0f}%", "Average", "#F59E0B")

        PANEL = "#FFFBEA"
        panel = tk.Frame(self, bg=PANEL, highlightthickness=2, highlightbackground="#F5D77A"); panel.pack(fill="both", expand=True, padx=30, pady=(0, 8))
        head = tk.Frame(panel, bg=PANEL); head.pack(fill="x", padx=16, pady=(10, 6))
        self.lbl(head, "  🎯 Choose your challenge!  ", 15, bg="#FDE68A", fg="#92400E").pack(side="left")
        self.lbl(head, "Puzzles for kids   •   Practice for students", 10, "italic", bg=PANEL, fg=self.MUTED).pack(side="left", padx=12)
        category_var, difficulty_var = tk.StringVar(value=self.category), tk.StringVar(value="Easy"); tiles, start_btn = [], {}

        def select(cat):
            category_var.set(cat)
            for t in tiles: t.paint()
            if "w" in start_btn:
                start_btn["w"].config(text=f"▶  PLAY {cat.upper()}!", bg=self.THEMES[cat]["accent"], activebackground=self.THEMES[cat]["accent"])

        grid = tk.Frame(panel, bg=PANEL); grid.pack(fill="both", expand=True, padx=14, pady=(0, 12)); grid.rowconfigure(1, weight=1)
        for i, cat in enumerate(self.THEMES):
            grid.columnconfigure(i, weight=1, uniform="tile")
            t = self.build_tile(grid, cat, category_var, select); t.grid(row=1, column=i, sticky="nsew", padx=6); tiles.append(t)
        self.lbl(grid, "🧒  KIDS ZONE", 10, bg="#F59E0B", fg="white", pady=3).grid(row=0, column=0, sticky="ew", padx=6, pady=(0, 6))
        self.lbl(grid, "🎓  STUDENT ZONE", 10, bg="#2563EB", fg="white", pady=3).grid(row=0, column=1, columnspan=4, sticky="ew", padx=6, pady=(0, 6))

        bottom = tk.Frame(self, bg="#C3E8AE"); bottom.pack(fill="x", padx=30, pady=(0, 14))
        lvl = self.card(bottom, width=400, height=195); lvl.pack(side="left", fill="both", expand=True, padx=(0, 10)); lvl.pack_propagate(False)
        self.lbl(lvl, "How tough should it be?", 15).pack(anchor="w", padx=20, pady=(14, 6))
        pills = tk.Frame(lvl, bg=self.CARD); pills.pack(anchor="w", padx=20)
        for level, label, col in (("Easy", "★  Easy", "#A7F3D0"), ("Medium", "★★  Medium", "#FDE68A")):
            tk.Radiobutton(pills, text=f"  {label}  ", variable=difficulty_var, value=level, indicatoron=False, font=F(12), bg="#F1F5F9", fg=self.TEXT,
                           selectcolor=col, activebackground="#E2E8F0", activeforeground=self.TEXT, relief="flat", bd=0, padx=16, pady=8,
                           cursor="hand2").pack(side="left", padx=(0, 10))
        self.lbl(lvl, f"⏱ 10 sec per question  •  📝 {self.QUESTIONS_PER_GAME} questions  •  ⭐ 10 points each", 10, None, fg=self.MUTED).pack(anchor="w", padx=20, pady=(8, 0))
        accent = self.THEMES[self.category]["accent"]
        btn = tk.Button(lvl, text=f"▶  PLAY {self.category.upper()}!", font=F(15), bg=accent, fg="white", activebackground=accent, activeforeground="white",
                        relief="flat", bd=0, pady=9, cursor="hand2", command=lambda: self.start_quiz(category_var.get(), difficulty_var.get()))
        btn.pack(fill="x", padx=20, pady=(0, 14), side="bottom"); start_btn["w"] = btn

        def progress_icon(cv, cx):
            for x1, x2, hgt, col in [(-40, -16, 34, "#60A5FA"), (-12, 12, 54, "#34D399"), (16, 40, 70, "#F59E0B")]:
                cv.create_rectangle(cx + x1, 100 - hgt, cx + x2, 100, fill=col, outline="")
            cv.create_line(cx - 48, 100, cx + 48, 100, fill="#475569", width=3)
            cv.create_polygon(*star_points(cx + 28, 20, 13), fill="#FACC15", outline="#CA8A04")

        self.nav_card(bottom, "Top Players", "See who is the champion!", "#FFF4D6", "#D97706", lambda cv, cx: draw_trophy(cv, cx, 58, 0.95),
                      self.show_leaderboard).pack(side="left", padx=(0, 10))
        self.nav_card(bottom, "My Games", "Your scores & badges", "#E4F3FF", "#2563EB", progress_icon, self.show_history).pack(side="left")

    # ---------------- Extra pages ----------------
    def page_header(self, title):
        ttk.Button(self, text="← Back to Home", command=self.show_dashboard).place(relx=1.0, x=-28, y=16, anchor="ne")
        self.lbl(self, f"  {title}  ", 20, bg="#FDE68A", fg="#92400E").pack(anchor="w", padx=30, pady=(80, 10))

    def show_leaderboard(self):
        self.clear_window(); self.configure(bg=self.BG); self.sky_background(); self.page_header("🏆 Top Players")
        rows = self.fetch_leaderboard(limit=8); _, my_best, _ = self.fetch_user_stats()
        podium = tk.Frame(self, bg="#FFFBEA", highlightthickness=2, highlightbackground="#F5D77A")
        podium.pack(side="left", fill="both", expand=True, padx=(30, 10), pady=(0, 22))
        cv = tk.Canvas(podium, bg="#FFFBEA", highlightthickness=0); cv.pack(fill="both", expand=True)
        cv.bind("<Configure>", lambda e: draw_podium(cv, cv.winfo_width(), cv.winfo_height(), rows[:3], self.current_username))
        side = self.card(self, width=380); side.pack(side="left", fill="y", padx=(0, 30), pady=(0, 22)); side.pack_propagate(False)
        self.lbl(side, "⭐ More Champions", 16).pack(anchor="w", padx=20, pady=(16, 8))
        self.lbl(side, f"Your best score: {my_best:.0f}%", 13, bg="#E0F2FE", fg="#075985", padx=14, pady=8).pack(side="bottom", pady=16)
        rest = rows[3:8]
        for i, (name, best) in enumerate(rest, start=4):
            row = tk.Frame(side, bg=self.CARD); row.pack(fill="x", padx=20, pady=5)
            badge = tk.Canvas(row, width=32, height=32, bg=self.CARD, highlightthickness=0); badge.pack(side="left")
            badge.create_oval(2, 2, 30, 30, fill="#CBD5E1", outline=""); badge.create_text(16, 16, text=str(i), fill="white", font=F(11))
            me = name == self.current_username
            self.lbl(row, name + ("  (you)" if me else ""), 12, "bold" if me else None, fg=self.PRIMARY if me else self.TEXT).pack(side="left", padx=10)
            self.lbl(row, f"{best:.0f}%", 12, fg=self.SUCCESS).pack(side="right")
        if not rest:
            self.lbl(side, "Ranks 4 to 8 will show up here.\nKeep playing to join the list!", 10, None, fg=self.MUTED, justify="left").pack(anchor="w", padx=20, pady=6)

    def paint_badges(self, cv, games, best):
        cv.delete("all"); w = cv.winfo_width()
        if w < 100: return
        items = [("first", "First Game", "Play 1 game", games >= 1), ("five", "Game Lover", "Play 5 games", games >= 5),
                 ("eighty", "Smart Star", "Score 80% or more", best >= 80), ("perfect", "Perfect!", "Score 100%", best >= 100)]
        for i, (kind, name, hint, ok) in enumerate(items):
            x = w * (i + .5) / 4; draw_badge(cv, x, 36, 26, kind, ok)
            cv.create_text(x, 86, text=name, font=F(10), fill=self.TEXT if ok else "#94A3B8")
            cv.create_text(x, 103, text="Unlocked!" if ok else hint, font=F(8, None), fill=self.SUCCESS if ok else self.MUTED)

    def show_history(self):
        self.clear_window(); self.configure(bg=self.BG); self.sky_background(); self.page_header("📜 My Games")
        games, best, avg = self.fetch_user_stats(); results = self.fetch_recent(limit=8)
        left = self.card(self); left.pack(side="left", fill="both", expand=True, padx=(30, 10), pady=(0, 22))
        self.lbl(left, "📈 My Scores", 16).pack(anchor="w", padx=20, pady=(14, 0))
        self.lbl(left, f"{games} games played   •   best {best:.0f}%   •   average {avg:.0f}%", 10, None, fg=self.MUTED).pack(anchor="w", padx=20)
        chart = tk.Canvas(left, bg=self.CARD, highlightthickness=0, height=200); chart.pack(fill="both", expand=True, padx=10, pady=(6, 0))
        chart.bind("<Configure>", lambda e: draw_score_chart(chart, chart.winfo_width(), chart.winfo_height(), list(reversed(results)), self.THEMES))
        tk.Frame(left, bg=self.BORDER, height=1).pack(fill="x", padx=20, pady=(4, 0))
        self.lbl(left, "🏅 My Badges", 16).pack(anchor="w", padx=20, pady=(10, 0))
        badges = tk.Canvas(left, bg=self.CARD, highlightthickness=0, height=122); badges.pack(fill="x", padx=10, pady=(0, 10))
        badges.bind("<Configure>", lambda e: self.paint_badges(badges, games, best))
        right = self.card(self, width=400); right.pack(side="left", fill="y", padx=(0, 30), pady=(0, 22)); right.pack_propagate(False)
        self.lbl(right, "🕒 Recent Games", 16).pack(anchor="w", padx=20, pady=(14, 6))
        if not results:
            mas = tk.Canvas(right, width=130, height=120, bg=self.CARD, highlightthickness=0); mas.pack(pady=(30, 4)); draw_mascot(mas, 65, 66, 1.0)
            self.lbl(right, "No games yet!\nPick a puzzle and start playing.", 12, None, fg=self.MUTED).pack()
        for cat, diff, score, pct in results:
            th = self.THEMES.get(cat, self.THEMES["Kids Puzzle"]); stars = 3 if pct >= 80 else 2 if pct >= 50 else 1 if pct > 0 else 0
            r = tk.Frame(right, bg=self.CARD); r.pack(fill="x", padx=20, pady=3)
            ic = tk.Canvas(r, width=40, height=40, bg=self.CARD, highlightthickness=0); ic.pack(side="left")
            draw_category_icon(ic, cat, 20, 20, 38, th["accent"], th["soft"])
            mid = tk.Frame(r, bg=self.CARD); mid.pack(side="left", padx=10)
            self.lbl(mid, cat).pack(anchor="w"); self.lbl(mid, f"{diff}  •  {score} points", 9, None, fg=self.MUTED).pack(anchor="w")
            end = tk.Frame(r, bg=self.CARD); end.pack(side="right")
            self.lbl(end, f"{pct:.0f}%", 12, fg=self.SUCCESS if pct >= 50 else self.DANGER).pack(anchor="e")
            self.lbl(end, "★" * stars + "☆" * (3 - stars), 10, None, fg="#F59E0B").pack(anchor="e")

    # ---------------- Quiz ----------------
    def start_quiz(self, category, difficulty):
        try:
            self.questions = self._query("""SELECT question_id, question_text, option1, option2, option3, option4, correct_answer, points
                           FROM questions WHERE category=%s AND difficulty=%s ORDER BY RAND() LIMIT %s""", (category, difficulty, self.QUESTIONS_PER_GAME))
        except Error as e: return messagebox.showerror("Database Error", str(e))
        if not self.questions: return messagebox.showwarning("No Questions", f"No {difficulty} questions found for {category}.")
        random.shuffle(self.questions)
        self.category, self.difficulty, self.current_index, self.answers = category, difficulty, 0, {}
        self.score = self.correct = self.incorrect = self.unattempted = 0
        self.max_points = sum(q[7] for q in self.questions); self.show_quiz()

    def draw_quiz_background(self, cv):
        cv.delete("all"); w, h = cv.winfo_width(), cv.winfo_height()
        if w < 100 or h < 100: return
        self._float_n = 0
        if self.category == "Kids Puzzle": self._kids_scene(cv, w, h)
        else: self._student_scene(cv, w, h)

    def _kids_scene(self, cv, w, h):
        draw_gradient(cv, w, h, "#BDE4FF", "#FFF4CC")
        cv.create_oval(-w * 0.1, h - 90, w * 0.6, h + 200, fill="#BDE5A8", outline=""); cv.create_oval(w * 0.4, h - 70, w * 1.1, h + 200, fill="#CDEEBB", outline="")
        sx, sy = w - 8, h * 0.2
        for ang in range(0, 360, 30):
            a = math.radians(ang)
            cv.create_line(sx + math.cos(a) * 44, sy + math.sin(a) * 44, sx + math.cos(a) * 62, sy + math.sin(a) * 62, fill="#FBBF24", width=4)
        cv.create_oval(sx - 38, sy - 38, sx + 38, sy + 38, fill="#FDE047", outline="#FACC15", width=3)
        for fx, fy, sc in [(-.01, .12, .9), (.02, .55, .8), (.5, .06, .7), (.97, .60, .8)]:
            self._group(cv, lambda x=fx * w, y=fy * h, k=sc: draw_cloud(cv, x, y, k))
        left = [("balloon", .26, "#EF4444"), ("balloon", .44, "#3B82F6"), ("block", .66, ("A", "#F59E0B")), ("star", .82, None)]
        right = [("balloon", .36, "#FACC15"), ("balloon", .52, "#10B981"), ("block", .70, ("1", "#8B5CF6")), ("piece", .84, "#F472B6")]
        for items, cx in ((left, 35), (right, w - 35)):
            for kind, fy, extra in items:
                y = fy * h
                if kind == "balloon": self._group(cv, lambda x=cx, yy=y, c=extra: draw_balloon(cv, x, yy, 19, c))
                elif kind == "block": self._group(cv, lambda x=cx, yy=y, e=extra: draw_block(cv, x, yy, 40, e[0], e[1]))
                elif kind == "star": self._group(cv, lambda x=cx, yy=y: cv.create_polygon(*star_points(x, yy, 18), fill="#FACC15", outline="#CA8A04", width=2))
                else: self._group(cv, lambda x=cx, yy=y, c=extra: draw_puzzle(cv, x - 16, yy - 16, 32, c))

    def _student_scene(self, cv, w, h):
        acc = self.THEMES[self.category]["accent"]
        draw_gradient(cv, w, h, blend(acc, "#FFFFFF", 0.90), blend(acc, "#FFFFFF", 0.96)); grid = blend(acc, "#FFFFFF", 0.82)
        for x in range(0, w, 28): cv.create_line(x, 0, x, h, fill=grid)
        for y in range(0, h, 28): cv.create_line(0, y, w, y, fill=grid)
        cv.create_line(64, 0, 64, h, fill="#FCA5A5", width=2)
        symbols = self.STUDENT_SYMBOLS.get(self.category, ["?"]); sym_color = blend(acc, "#FFFFFF", 0.35)
        for i, fy in enumerate((.20, .33, .46, .59, .72, .85)):
            self._group(cv, lambda t=symbols[i % len(symbols)], y=fy * h: cv.create_text(32, y, text=t, fill=sym_color, font=F(22)))
        rx = w - 35
        self._group(cv, lambda: draw_grad_cap(cv, rx, h * 0.17, 0.95)); self._group(cv, lambda: draw_pencil(cv, rx, h * 0.43, 120, 90))
        self._group(cv, lambda t=symbols[-1]: cv.create_text(rx, h * 0.62, text=t, fill=sym_color, font=F(24)))
        self._group(cv, lambda: draw_books(cv, rx, h * 0.80, 0.95))

    def show_quiz(self):
        self.clear_window(); theme = self.THEMES.get(self.category, self.THEMES["Kids Puzzle"])
        self.quiz_bg = theme["bg"]; self.configure(bg=self.quiz_bg); self._bg_canvas(self.quiz_bg, self.draw_quiz_background)
        kids = self.category == "Kids Puzzle"
        top = tk.Frame(self, bg=self.TEXT, height=82); top.pack(fill="x"); top.pack_propagate(False)
        mini = tk.Canvas(top, width=56, height=56, bg=self.TEXT, highlightthickness=0); mini.pack(side="left", padx=(24, 6))
        draw_category_icon(mini, self.category, 28, 28, 52, theme["accent"], theme["soft"])
        self.lbl(top, self.category, 20, bg=self.TEXT, fg="white").pack(side="left", padx=(6, 12))
        self.lbl(top, self.difficulty, 11, bg=theme["accent"], fg="white", padx=14, pady=6).pack(side="left")
        self.lbl(top, "🧒 Kids Zone" if kids else "🎓 Student Zone", 11, bg="#334155", fg="white", padx=12, pady=6).pack(side="left", padx=10)
        self.timer_canvas = tk.Canvas(top, width=64, height=64, bg=self.TEXT, highlightthickness=0); self.timer_canvas.pack(side="right", padx=(10, 26))
        self.score_label = self.lbl(top, "⭐ Score: 0", 14, bg=self.TEXT, fg="white"); self.score_label.pack(side="right", padx=10)

        status = self.card(self); status.pack(fill="x", padx=70, pady=(14, 8))
        info = tk.Frame(status, bg=self.CARD); info.pack(fill="x", padx=16, pady=(8, 0))
        self.progress_label = self.lbl(info, "", 10, fg=self.MUTED); self.progress_label.pack(side="left")
        self.dots = tk.Canvas(info, height=20, width=max(60, len(self.questions) * 24), bg=self.CARD, highlightthickness=0); self.dots.pack(side="right")
        self.progress = ttk.Progressbar(status, length=1000, mode="determinate"); self.progress.pack(fill="x", padx=16, pady=(4, 10))

        qcard = tk.Frame(self, bg=self.CARD, highlightthickness=1, highlightbackground=self.BORDER); qcard.pack(fill="both", expand=True, padx=70)
        self.icon_canvas = tk.Canvas(qcard, width=170, height=170, bg=self.CARD, highlightthickness=0); self.icon_canvas.pack(side="left", padx=(28, 10), pady=30, anchor="n")
        draw_category_icon(self.icon_canvas, self.category, 85, 85, 150, theme["accent"], theme["soft"])
        qa = tk.Frame(qcard, bg=self.CARD); qa.pack(side="left", fill="both", expand=True, padx=(5, 30), pady=22)
        self.question_label = self.lbl(qa, "", 20, wraplength=640, justify="left", anchor="w"); self.question_label.pack(fill="x", pady=(5, 18))
        qa.bind("<Configure>", lambda e: self.question_label.config(wraplength=max(300, e.width - 10)))
        self.option_var = tk.StringVar(value=""); self.option_buttons = []
        for value in ["option1", "option2", "option3", "option4"]:
            btn = tk.Radiobutton(qa, text="", variable=self.option_var, value=value, indicatoron=False, anchor="w", wraplength=620, justify="left",
                                 font=F(12, None), bg="#F8FAFC", fg=self.TEXT, activebackground="#EEF2FF", selectcolor=theme["soft"], padx=15, pady=9,
                                 relief="flat", bd=0, highlightthickness=1, highlightbackground=self.BORDER, cursor="hand2")
            btn.pack(fill="x", pady=4); self.option_buttons.append(btn)
        self.result_label = self.lbl(qa, "", 11, fg=self.MUTED, wraplength=640, justify="left"); self.result_label.pack(anchor="w", pady=(8, 2))

        nav = self.card(self, height=66); nav.pack(fill="x", padx=70, pady=(8, 14)); nav.pack_propagate(False)
        ttk.Button(nav, text="← Back", command=self.previous_question).pack(side="left", padx=5)
        self.submit_button = tk.Button(nav, text="SUBMIT", command=self.submit_answer, font=F(11), bg=theme["accent"], fg="white",
                                       activebackground=theme["accent"], activeforeground="white", relief="flat", padx=32, pady=10, cursor="hand2")
        self.submit_button.pack(side="left", padx=5)
        self.next_button = ttk.Button(nav, text="Next →", command=self.next_question); self.next_button.pack(side="right", padx=5)
        ttk.Button(nav, text="Exit Quiz", command=self.exit_quiz).pack(side="right", padx=5)
        self.load_question()

    def exit_quiz(self):
        if messagebox.askyesno("Exit Quiz", "Exit now? Your progress in this quiz will not be saved."): self.show_dashboard()

    def update_timer_ring(self):
        cv = self.timer_canvas; cv.delete("all"); frac = max(self.time_left, 0) / 10.0
        color = "#34D399" if self.time_left > 5 else ("#FBBF24" if self.time_left > 3 else "#EF4444")
        cv.create_oval(6, 6, 58, 58, outline="#334155", width=6)
        if frac > 0: cv.create_arc(6, 6, 58, 58, start=90, extent=359.9 * frac, style="arc", outline=color, width=6)
        cv.create_text(32, 32, text=str(max(self.time_left, 0)), fill=color, font=F(16))

    def draw_dots(self):
        cv = self.dots; cv.delete("all"); palette = {"correct": self.SUCCESS, "wrong": self.DANGER, "timeout": "#F59E0B"}
        for i in range(len(self.questions)):
            x = 12 + i * 24; saved = self.answers.get(i)
            cv.create_oval(x - 7, 3, x + 7, 17, fill=palette[saved["status"]] if saved else "#CBD5E1", outline="")
            if i == self.current_index: cv.create_oval(x - 10, 0, x + 10, 20, outline=self.TEXT, width=2)

    def paint_options(self):
        theme = self.THEMES[self.category]; saved = self.answers.get(self.current_index); options = self.questions[self.current_index][2:6]
        for i, btn in enumerate(self.option_buttons):
            bg, sel, fg = "#F8FAFC", theme["soft"], self.TEXT
            if saved:
                if options[i] == self.current_correct: bg = sel = "#D1FAE5"; fg = "#065F46"
                elif saved["selected"] == f"option{i + 1}": bg = sel = "#FEE2E2"; fg = "#991B1B"
            btn.config(text=f"{chr(65 + i)}.  {options[i]}", bg=bg, selectcolor=sel, fg=fg, disabledforeground=fg,
                       activebackground=bg if saved else "#EEF2FF", state="disabled" if saved else "normal")

    def load_question(self):
        self._cancel("timer_id")
        _, question, a, b, c, d, correct, points = self.questions[self.current_index]
        self.current_correct, self.current_points = correct, points; self.submitted = self.current_index in self.answers
        self.progress_label.config(text=f"Question {self.current_index + 1} of {len(self.questions)}")
        self.progress["maximum"] = len(self.questions); self.progress["value"] = self.current_index + 1
        self.question_label.config(text=question)
        saved = self.answers.get(self.current_index, {}); self.option_var.set(saved.get("selected", "")); self.paint_options()
        self.result_label.config(text=saved.get("result", ""), fg=self.SUCCESS if saved.get("status") == "correct" else self.DANGER)
        self.submit_button.config(state="disabled" if self.submitted else "normal")
        self.next_button.config(text="Finish →" if self.current_index == len(self.questions) - 1 else "Next →")
        self.draw_dots(); self.time_left = 10; self.update_timer_ring()
        if not self.submitted: self.timer_id = self.after(1000, self.tick)

    def tick(self):
        if self.submitted: return
        self.time_left -= 1; self.update_timer_ring()
        if self.time_left <= 0: self.submit_answer(timeout=True)
        else: self.timer_id = self.after(1000, self.tick)

    def submit_answer(self, timeout=False):
        if self.submitted: return
        selected = self.option_var.get()
        if not selected and not timeout: return messagebox.showwarning("Select Answer", "Please select an option before submitting.")
        self._cancel("timer_id")
        if timeout and not selected:
            status, result_text = "timeout", f"⏰ Time's up!  Correct answer: {self.current_correct}"; self.unattempted += 1
        else:
            selected_text = self.questions[self.current_index][2:6][{"option1": 0, "option2": 1, "option3": 2, "option4": 3}[selected]]
            if selected_text == self.current_correct:
                status = "correct"; self.correct += 1; self.score += self.current_points
                result_text = f"✓ {random.choice(['Awesome!', 'Great job!', 'Brilliant!', 'You rock!'])}  +{self.current_points} points"
            else:
                status = "wrong"; self.incorrect += 1; result_text = f"✗ Oops, good try!  Correct answer: {self.current_correct}"
        self.answers[self.current_index] = {"selected": selected, "status": status, "result": result_text}
        self.submitted = True; self.score_label.config(text=f"⭐ Score: {self.score}")
        self.result_label.config(text=result_text, fg=self.SUCCESS if status == "correct" else self.DANGER)
        self.submit_button.config(state="disabled"); self.paint_options(); self.draw_dots()

    def previous_question(self):
        if self.current_index > 0: self.current_index -= 1; self.load_question()
        else: messagebox.showinfo("First Question", "You are already on the first question.")

    def next_question(self):
        if not self.submitted: return messagebox.showwarning("Submit First", "Please submit the current answer first.")
        if self.current_index < len(self.questions) - 1: self.current_index += 1; self.load_question()
        elif len(self.answers) < len(self.questions):
            messagebox.showinfo("Unfinished", "Some earlier questions are still unanswered. Use Back to complete them.")
        else: self.save_result(); self.show_result_screen()

    # ---------------- Results ----------------
    def save_result(self):
        percentage = (self.score / self.max_points * 100) if self.max_points else 0
        try:
            db = self.db_connect(); cur = db.cursor()
            cur.execute("INSERT INTO results (user_id, category, difficulty, score, total_questions, percentage) VALUES (%s,%s,%s,%s,%s,%s)",
                        (self.current_user_id, self.category, self.difficulty, self.score, len(self.questions), percentage))
            db.commit(); cur.close(); db.close()
        except Error as e: messagebox.showwarning("Result Save", f"Could not save result:\n{e}")

    def show_result_screen(self):
        self.clear_window(); self.configure(bg=self.BG); self.header(self, "Challenge completed")
        theme = self.THEMES.get(self.category, self.THEMES["Kids Puzzle"]); acc = theme["accent"]
        pct = (self.score / self.max_points * 100) if self.max_points else 0
        stars = 3 if pct >= 80 else 2 if pct >= 50 else 1 if pct > 0 else 0
        message = "Outstanding!" if stars == 3 else "Great job!" if stars == 2 else "Good effort!" if stars == 1 else "Keep practising!"
        card = self.card(self); card.place(relx=0.5, rely=0.55, anchor="center")
        banner = tk.Canvas(card, width=700, height=185, highlightthickness=0, bg=acc); banner.pack()
        draw_gradient(banner, 700, 185, blend(acc, "#FFFFFF", 0.15), blend(acc, "#000000", 0.25)); draw_confetti(banner, 700, 185)
        banner.create_oval(310, 20, 390, 100, fill=blend(acc, "#FFFFFF", 0.35), outline="")
        draw_trophy(banner, 350, 62, 0.95); draw_stars(banner, 350, 148, stars, size=17, gap=46)
        self.lbl(card, f"{message} 🎉", 24, fg=acc).pack(pady=(16, 0))
        self.lbl(card, f"{self.category}  •  {self.difficulty}", 11, None, fg=self.MUTED).pack(pady=(2, 8))
        self.lbl(card, f"{self.score}", 42, fg=self.SUCCESS).pack()
        self.lbl(card, f"points out of {self.max_points}   ({pct:.0f}%)", 11, None, fg=self.MUTED).pack()
        stats = tk.Frame(card, bg=self.CARD); stats.pack(pady=18)
        for title, value, color in [("Correct", self.correct, self.SUCCESS), ("Incorrect", self.incorrect, self.DANGER), ("Unattempted", self.unattempted, "#F59E0B")]:
            box = tk.Frame(stats, bg="#F8FAFC", width=150, height=74, highlightthickness=1, highlightbackground=self.BORDER)
            box.pack(side="left", padx=8); box.pack_propagate(False)
            self.lbl(box, str(value), 21, bg="#F8FAFC", fg=color).pack(pady=(7, 0)); self.lbl(box, title, 9, None, bg="#F8FAFC", fg=self.MUTED).pack()
        btns = tk.Frame(card, bg=self.CARD); btns.pack(fill="x", padx=60, pady=(0, 24))
        ttk.Button(btns, text="PLAY AGAIN", style="Accent.TButton", command=self.show_dashboard).pack(side="left", expand=True, fill="x", padx=(0, 8))
        ttk.Button(btns, text="LOGOUT", command=self.show_login).pack(side="left", expand=True, fill="x")


if __name__ == "__main__":
    try:
        app = FocusQuestApp(); app.mainloop()
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect to MySQL.\n\n{e}")
