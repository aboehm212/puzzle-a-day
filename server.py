"""Puzzle-A-Day: serves the game and a small leaderboard API (no dependencies)."""
import json, os, re, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DATA_DIR = os.environ.get("DATA_DIR", "/data")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
PORT = int(os.environ.get("PORT", "8080"))
KEEP_DAYS = int(os.environ.get("KEEP_DAYS", "60"))
DB_FILE = os.path.join(DATA_DIR, "scores.json")

DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[A-Za-z0-9-]{8,64}$")
lock = threading.Lock()


def load():
    try:
        with open(DB_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"players": {}, "days": {}}


def store(db):
    days = sorted(db["days"])
    for d in days[:-KEEP_DAYS]:
        del db["days"][d]
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False)
    os.replace(tmp, DB_FILE)


def clean_name(n):
    return " ".join(str(n or "").split())[:24]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=STATIC_DIR, **kw)

    def log_message(self, fmt, *args):
        pass

    def send_json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n <= 0 or n > 4096:
            return None
        try:
            return json.loads(self.rfile.read(n))
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/health":
            return self.send_json(200, {"ok": True})
        if u.path == "/api/scores":
            day = (parse_qs(u.query).get("day") or [""])[0]
            if not DAY_RE.match(day):
                return self.send_json(400, {"error": "day"})
            with lock:
                db = load()
            entries = db["days"].get(day, {})
            rows = [{"id": pid, "name": db["players"].get(pid, ""), "pts": e["pts"], "secs": e["secs"]}
                    for pid, e in entries.items()]
            rows.sort(key=lambda r: (-r["pts"], r["secs"]))
            return self.send_json(200, {"rows": rows[:50]})
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        data = self.read_json()
        if not isinstance(data, dict) or not ID_RE.match(str(data.get("id", ""))):
            return self.send_json(400, {"error": "bad request"})
        pid = data["id"]
        if u.path == "/api/name":
            with lock:
                db = load()
                name = clean_name(data.get("name"))
                if name:
                    db["players"][pid] = name
                else:
                    db["players"].pop(pid, None)
                store(db)
            return self.send_json(200, {"ok": True})
        if u.path == "/api/scores":
            day = str(data.get("day", ""))
            try:
                pts, secs = int(data.get("pts")), int(data.get("secs"))
            except (TypeError, ValueError):
                return self.send_json(400, {"error": "numbers"})
            if not DAY_RE.match(day) or not (0 <= pts <= 100000) or not (0 <= secs <= 86400):
                return self.send_json(400, {"error": "range"})
            with lock:
                db = load()
                bucket = db["days"].setdefault(day, {})
                first = pid not in bucket
                if first:
                    bucket[pid] = {"pts": pts, "secs": secs, "at": int(time.time())}
                name = clean_name(data.get("name"))
                if name:
                    db["players"][pid] = name
                store(db)
            return self.send_json(200, {"ok": True, "counted": first})
        return self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Puzzle-A-Day läuft auf Port {PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
