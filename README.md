# tooly

**Lightweight terminal utilities for Python.**

A single-file library that covers everything you'd reach for in a CLI project — colors, spinners, progress bars, logging, input handling, system info, file ops, and more. No heavy dependencies, just `tooly.py`.

```bash
pip install tooly-dev
```

Or drop `tooly.py` directly into your project.

---

## Quick Start

```python
import tooly

# Colors
colors = tooly.ColorSystem()
print(colors.success("Done!"))
print(colors.error("Something went wrong"))
print(colors.info("Loading..."))

# Spinner
with tooly.spinner("Working", done_msg="Finished"):
    time.sleep(2)

# Progress bar
for item in tooly.progress(range(100), label="Processing"):
    ...

# Timing
with tooly.measure("database query"):
    result = db.fetch_all()
```

---

## Reference

### Output & Colors

#### `ColorSystem`

```python
colors = tooly.ColorSystem()

# Named colors
colors.red("text")
colors.green("text")
colors.yellow("text")
colors.blue("text")
colors.cyan("text")
colors.magenta("text")
colors.grey("text")

# Semantic helpers
colors.success("All done!")      # ✓ green
colors.error("Failed!")          # X red
colors.warning("Watch out!")     # ! yellow
colors.info("FYI")               # i blue
colors.debug("trace")            # ~ grey
colors.critical("ABORT")         # bold red background

# Styles
colors.bold("text")
colors.italic("text")
colors.underline("text")
colors.dim("text")
colors.strikethrough("text")

# Background colors
colors.bg_red("text")
colors.bg_green("text")
# ... and more

# RGB / 256-color
colors.rgb("text", 255, 128, 0)
colors.bg_rgb("text", 30, 30, 30)
colors.color256("text", "214")

# Gradient across characters
colors.gradient("Hello!", start=(255, 0, 0), end=(0, 0, 255))

# Syntax highlighting
colors.json({"key": "value", "count": 42})
colors.python("def hello(): return 42")

# Utilities
colors.highlight("find these keywords here", ["keywords", "these"], "yellow")
colors.indent("file.py", level=1)   # colored tree-style indent
```

#### `typewrite(text, delay=0.1, end="\n")`

Types text character-by-character with a configurable delay.

```python
tooly.typewrite(colors.info("Loading config..."), delay=0.04)
```

#### `banner(text, style="block", color="blue", align="center", width=None)`

Draws a bordered banner. Styles: `"block"`, `"thin"`, `"dots"`, or plain.

```python
tooly.banner("tooly v1.5", style="thin", color="cyan")
```

#### `sparkline(values)`

Returns a Unicode sparkline string from a list of numbers.

```python
print(tooly.sparkline([1, 3, 2, 5, 4, 7, 6]))  # ▁▃▂▅▄▇▆
```

#### `triangle(char="█", delay=0.02, color="cyan")`

Draws an animated full-screen triangle, then clears it.

---

### Timing & Control Flow

#### `measure(label, precision=3)`

Context manager that prints elapsed time.

```python
with tooly.measure("build step"):
    compile_project()
# [⏲] build step: 1.243s
```

#### `spinner(label, frames, done_msg)`

Animated spinner context manager.

```python
with tooly.spinner("Fetching data", done_msg="Got it"):
    data = api.get()
```

#### `countdown(seconds, label, done_msg)`

Counts down to zero, returns `True` if completed, `False` if interrupted.

```python
if tooly.countdown(10, label="Starting in"):
    launch()
```

#### `watch(func, interval=2.0, title, show_timestamp)`

Repeatedly calls `func()` and refreshes the terminal output, like `watch` in Linux.

```python
tooly.watch(lambda: f"Queue size: {queue.qsize()}", interval=1.0)
```

---

### Input

#### `userinput(prompt, validator, error_msg, max_attempts, strip)`

Prompts the user with optional validation loop.

```python
age = tooly.userinput("Age: ", validator=str.isdigit, error_msg="Digits only")
```

#### `password(prompt, confirm, min_length, max_length, validator, mask)`

Masked password input with optional confirmation and validation.

```python
pwd = tooly.password("Password: ", confirm=True, min_length=8)
```

#### `menu(items, title, loop, input_mode, clear)`

Interactive arrow-key or digit menu. Returns the selected item or `None`.

```python
choice = tooly.menu(["Start", "Settings", "Quit"], title="Main Menu")
```

#### `confirm(prompt, yes_values, no_values)`

Single-keypress yes/no prompt. Returns `bool`.

```python
if tooly.confirm("Delete this file?"):
    os.remove(path)
```

---

### Progress

#### `progress(iterable=None, total=None, label, width)`

Progress bar that wraps an iterable or works as a manual counter.

```python
# Wrap an iterable
for item in tooly.progress(files, label="Uploading"):
    upload(item)

# Manual control
with tooly.progress(total=100) as p:
    for i in range(100):
        do_work()
        p.update()
```

---

### Logging

#### `log`

A global logger instance with leveled output and optional file sink.

```python
tooly.log.info("Server started")
tooly.log.success("Job completed")
tooly.log.warn("Disk space low")
tooly.log.error("Connection failed")
tooly.log.debug("x =", x)

# Custom tag
tooly.log("SRV", "Listening on :8080", color="cyan")

# File output
tooly.log.set_file("app.log")
tooly.log.unset_file()

# Silence/restore
tooly.log.mute()
tooly.log.unmute()

# Toggle timestamps
tooly.log.timestamps(False)
```

---

### Retry

#### `retry(attempts=3, delay=1.0, backoff=1.0, exceptions, on_fail, label)`

Decorator or context manager for automatic retries with optional backoff.

```python
# Decorator
@tooly.retry(attempts=3, delay=0.5, backoff=2.0)
def fetch():
    return requests.get(url).json()

# Context manager
with tooly.retry(attempts=5, delay=1.0) as r:
    result = risky_operation()
```

---

### Scheduling

#### `every(seconds, func=None, start_immediately=True)`

Runs a function on a background thread at a fixed interval. Returns a handle.

```python
@tooly.every(seconds=5)
def heartbeat():
    print("ping")

# Later:
heartbeat.pause()
heartbeat.resume()
heartbeat.stop()
```

---

### System

#### `Platform` / `on_platform(...)`

Detect the current platform and dispatch platform-specific callbacks.

```python
name = tooly.on_platform(
    windows=lambda: "Windows",
    linux=lambda: "Linux",
    macos=lambda: "macOS",
    android=lambda: "Android",
    default=lambda: "Unknown",
)
```

Platforms: `windows`, `linux`, `macos`, `android`, `ios`, `freebsd`.

#### `ram()`

Returns a `RamInfo(total, used, free, percent)` namedtuple (bytes).

```python
r = tooly.ram()
print(f"RAM: {tooly.humanize(r.used, 'bytes')} / {tooly.humanize(r.total, 'bytes')} ({r.percent}%)")
```

#### `cpu(interval=0.1)`

Returns a `CpuInfo(count, percent, freq_mhz, model)` namedtuple.

```python
c = tooly.cpu()
print(f"CPU: {c.model} × {c.count} cores @ {c.freq_mhz} MHz — {c.percent}% used")
```

#### `hwid(stable=True)`

Returns a SHA-256 hardware fingerprint as a hex string.

```python
print(tooly.hwid())  # e.g. "A3F9C2..."
```

#### `is_admin()`

Returns `True` if the current process has admin/root privileges.

#### `uptime()`

Returns system uptime in seconds as a `float`.

#### `pkill(name=None, pid=None, force=False, signal=15)`

Kill a process by name or PID.

```python
tooly.pkill("chrome")
tooly.pkill(pid=1234, force=True)
```

#### `plist(name=None, pid=None)`

List running processes, optionally filtered.

```python
procs = tooly.plist(name="python")
for p in procs:
    print(p["pid"], p["name"])
```

#### `notify(title, message, urgency)`

Send a desktop notification (uses `notify-send` / `osascript` / `MessageBox`).

```python
tooly.notify("Build done", "All tests passed ✓")
```

#### Power / Session

```python
tooly.shutdown(delay=30)        # shutdown in 30 seconds
tooly.reboot(force=True)        # force reboot
tooly.hibernate()
tooly.lock_device()
tooly.cancel_shutdown()
```

---

### Environment

#### `env(name, default=None, required=False, dotenv=None)`

Read an environment variable, with auto `.env` loading.

```python
db_url = tooly.env("DATABASE_URL", required=True)
debug  = tooly.env("DEBUG", default="false")
```

---

### File & Data

#### `run(cmd, live=False, timeout=None, spinner=True, cwd=None)`

Run a shell command and return a `RunResult(returncode, stdout, stderr, success)`.

```python
result = tooly.run("git status")
if result.success:
    print(result.stdout)

# Stream output live
tooly.run("npm install", live=True)
```

#### `download(url, dest=None, filename=None, overwrite=False, retries=3, progress=True)`

Download a file with a progress bar and retry logic.

```python
result = tooly.download("https://example.com/data.csv", dest="/tmp")
if result:
    print("Saved to", result.path)
```

#### `unzip(path, dest=None, overwrite=True, password=None, members=None, progress=True)`

Extract archives: `.zip`, `.tar.*`, `.gz`, `.bz2`, `.xz`, `.rar`, `.7z`.

```python
result = tooly.unzip("archive.tar.gz", dest="./out")
print(f"Extracted {result.count} files")
```

#### `remove(path, recursive=False, missing_ok=True, trash=False)`

Delete a file or directory, optionally sending it to the system trash.

```python
tooly.remove("temp/", recursive=True)
tooly.remove("old_file.txt", trash=True)
```

#### `md5(data)`

Return the MD5 hex digest of a string, bytes, or file path.

```python
tooly.md5("hello")                  # hash of string
tooly.md5(b"\x00\x01")             # hash of bytes
tooly.md5("/path/to/file.bin")      # hash of file
```

#### `tempdir(suffix, prefix, dir)`

Context manager that creates and auto-deletes a temporary directory.

```python
with tooly.tempdir() as tmp:
    open(f"{tmp}/scratch.txt", "w").write("data")
# directory is deleted here
```

#### `humanize(value, kind="num")`

Format numbers, bytes, or durations as human-readable strings.

```python
tooly.humanize(1_500_000)               # "1.5M"
tooly.humanize(2_048, kind="bytes")     # "2.0 KB"
tooly.humanize(3661, kind="seconds")    # "1h 1m 1s"
```

#### `ensure_package(name, version=None, upgrade=False, quiet=False)`

Install a PyPI package at runtime if not already present.

```python
tooly.ensure_package("rich")
tooly.ensure_package("requests", version="2.31.0")
```

#### `package_version(name)`

Return the installed version of a package, or `None`.

---

### Persistence

#### `saves`

A simple key-value save manager backed by JSON or pickle files.

```python
tooly.saves.save("config", {"theme": "dark", "lang": "en"})
config = tooly.saves.load("config")

tooly.saves.exists("config")       # True
tooly.saves.list()                 # [{"key": "config", "fmt": "json", ...}]
tooly.saves.delete("config")
tooly.saves.clear()                # delete all saves
```

Default save location: `~/.tooly/saves/`. Pass `folder=` to customize.

---

### Debugging

#### `patch(obj, label=None, show_types=False, on_change=None)`

Context manager that logs attribute changes on any object in real time.

```python
class Config:
    debug = False
    workers = 4

cfg = Config()
with tooly.patch(cfg, label="Config") as p:
    p.debug = True
    p.workers = 8
# prints timestamped diffs of every assignment
```

#### `recorder(log_file="session.log")`

Record all terminal input/output to a log file.

```python
with tooly.recorder("session.log"):
    name = input("Name: ")
    print(f"Hello, {name}!")
```

---

### Fake Data

#### `lorem`

Generate placeholder text, names, emails, addresses, and more.

```python
tooly.lorem.words(10)
tooly.lorem.sentences(3)
tooly.lorem.paragraph()
tooly.lorem.name()                          # "Jordan Smith"
tooly.lorem.name(gender="female", locale="ru")
tooly.lorem.email()
tooly.lorem.phone("+44")
tooly.lorem.address()
tooly.lorem.company()
tooly.lorem.job_title()
tooly.lorem.uuid()
tooly.lorem.ip(version=4)
tooly.lorem.url()
tooly.lorem.date(past=365)
tooly.lorem.datetime()
```

Locales: `"en"`, `"ru"`. Genders: `"male"`, `"female"`.

---

### Diff

#### `diff_highlight(a, b, mode, label_a, label_b)`

Show colored diffs between two strings.

```python
tooly.diff_highlight(
    "SELECT id, name FROM users",
    "SELECT id, email FROM users LIMIT 100",
    tooly.DiffMode.WORD,
)
```

Modes: `DiffMode.WORD`, `DiffMode.CHAR`, `DiffMode.LINE`.

---

### Activity Calendar

#### `calendar(data, title, color_mode, show_legend, show_stats, max_weeks)`

Render a GitHub-style contribution heatmap.

```python
data = {"2026-06-01": 5, "2026-06-02": 2, "2026-06-03": 8}
tooly.calendar(data, title="Commits", color_mode="blue")
```

Color modes: `"green"`, `"blue"`, `"purple"`, `"orange"`.

---

## Audio

#### `music`

Play audio files in a background thread (requires `ffplay`, `mpv`, `mplayer`, `afplay`, or `cvlc`).

```python
tooly.music.play("track.mp3", loop=True)
tooly.music.pause()
tooly.music.resume()
tooly.music.volume(0.5)
tooly.music.stop()

info = tooly.music.info()  # {"current", "is_playing", "is_paused", "volume"}
```

---

## Misc

```python
tooly.cls()           # clear the terminal
tooly.is_admin()      # True if running as root/admin
```

---

## License

MIT © 2026 SuperDragon777
