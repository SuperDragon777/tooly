__version__ = "1.4.0"
__author__ = "SuperDragon777"
__all__ = ["ColorSystem", "measure", "spinner", "typewrite", "diff_highlight", "userinput", "recorder", "cls", "Platform", "on_platform", "menu", "confirm", "watch", "notify", "log", "retry", "countdown", "sparkline", "calendar", "progress", "banner", "password", "env", "run", "humanize", "tempdir"]

import platform
import sys
import os
import time
from contextlib import contextmanager
from typing import Callable, Optional, Any, Iterable, TypeVar, Iterator, Union
import difflib
from enum import Enum
import threading
import io
from datetime import datetime, timedelta
import builtins
import re
import subprocess
import functools
import random
from dataclasses import dataclass, field
import tempfile
import shutil

try:
    import tty as _tty
    import termios as _termios
except ImportError:
    _tty = None
    _termios = None

try:
    import msvcrt as _msvcrt
except ImportError:
    _msvcrt = None

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

def _strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)

class ColorSystem:
    def __init__(self):
        self.support_colors = self._check_color_support()
    
    def _check_color_support(self):
        if platform.system() == 'Windows':
            if sys.platform == 'win32':
                os.system('color')
                return True
        
        if 'TERM' in os.environ and os.environ['TERM'] != 'dumb':
            return True
        
        return sys.stdout.isatty()
    
    def _colorize(self, text, color_code):
        if not self.support_colors:
            return text
        return f"\033[{color_code}m{text}\033[0m"
    
    def red(self, text):
        return self._colorize(text, "91")
    
    def green(self, text):
        return self._colorize(text, "92")
    
    def yellow(self, text):
        return self._colorize(text, "93")
    
    def blue(self, text):
        return self._colorize(text, "94")
    
    def grey(self, text):
        return self._colorize(text, "90")
    
    def bold(self, text):
        return self._colorize(text, "1")
    
    def dim(self, text):
        return self._colorize(text, "2")
    
    def bg_blue(self, text):
        return self._colorize(text, "44")
    
    def bg_color(self, text, bg_code: str, fg_code: str = "97"):
        if not self.support_colors:
            return text
        return f"\033[{bg_code};{fg_code}m{text}\033[0m"
    
    def success(self, text):
        return self.green(f"[✓] {text}")
    
    def error(self, text):
        return self.red(f"[X] {text}")
    
    def warning(self, text):
        return self.yellow(f"[!] {text}")
    
    def info(self, text):
        return self.blue(f"[i] {text}")
        
    def highlight(self, text: str, keywords: list[str], color: str = "yellow") -> str:
        colorize = getattr(self, color, self.yellow)
        for kw in keywords:
            text = text.replace(kw, colorize(kw))
        return text
        
    def indent(self, text: str, level: int = 1) -> str:
        palette = ["94", "92", "93", "91", "95"]
        code = palette[level % len(palette)]
        prefix = "  " * level + "│ "
        return self._colorize(prefix, code) + text

    def color256(self, text: str, code: str) -> str:
        if not self.support_colors:
            return text
        return f"\033[38;5;{code}m{text}\033[0m"

def typewrite(
    text: str,
    delay: float = 0.1,
    stream=sys.stdout,
    end: str = "\n",
) -> None:
    write = stream.write
    for char in text:
        write(char)
        stream.flush()
        time.sleep(delay)
    write(end)
    stream.flush()

@contextmanager
def measure(label: str = "runtime", stream=sys.stdout, precision: int = 3):
    colors = ColorSystem()
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        formatted = _format_duration(elapsed, precision)
        stream.write(colors.grey(f"[⏲] {label}: {formatted}\n"))
        stream.flush()


def _format_duration(seconds: float, precision: int = 3) -> str:
    if seconds < 1e-3:
        return f"{seconds * 1_000_000:.{precision}f}µs"
    elif seconds < 1:
        return f"{seconds * 1_000:.{precision}f}ms"
    elif seconds < 60:
        return f"{seconds:.{precision}f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.{precision}f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.{precision}f}s"

@contextmanager
def spinner(label: str = "Loading", frames="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", done_msg: str = "Done"):
    colors = ColorSystem()
    stop_event = threading.Event()

    def _spin():
        i = 0
        while not stop_event.is_set():
            sys.stdout.write(f"\r{frames[i % len(frames)]} {label}...")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)

    t = threading.Thread(target=_spin, daemon=True)
    t.start()
    try:
        yield
    finally:
        stop_event.set()
        t.join()
        sys.stdout.write("\r" + " " * (len(label) + 10) + "\r")
        if done_msg:
            sys.stdout.write(colors.success(done_msg) + "\n")
        sys.stdout.flush()

class DiffMode(Enum):
    CHAR = "char"
    WORD = "word"
    LINE = "line"


def diff_highlight(
    a: str,
    b: str,
    mode: DiffMode | str = DiffMode.WORD,
    *,
    label_a: str = "A",
    label_b: str = "B",
    context_lines: int = 2,
    show_legend: bool = True,
) -> str:
    if isinstance(mode, str):
        mode = DiffMode(mode)

    if mode == DiffMode.LINE:
        return _diff_line(a, b, label_a, label_b, context_lines, show_legend)
    elif mode == DiffMode.WORD:
        return _diff_inline(a, b, label_a, label_b, show_legend, split_fn=str.split)
    else:
        return _diff_inline(a, b, label_a, label_b, show_legend, split_fn=list)


def _apply_opcodes(tokens_a, tokens_b, sep):
    colors = ColorSystem()
    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)
    out_a, out_b = [], []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        chunk_a = sep.join(tokens_a[i1:i2])
        chunk_b = sep.join(tokens_b[j1:j2])

        if tag == "equal":
            out_a.append(chunk_a)
            out_b.append(chunk_b)
        elif tag == "delete":
            out_a.append(colors.red(chunk_a))
        elif tag == "insert":
            out_b.append(colors.green(chunk_b))
        elif tag == "replace":
            out_a.append(colors.red(chunk_a))
            out_b.append(colors.green(chunk_b))

    return sep.join(out_a), sep.join(out_b)


def _diff_inline(a, b, label_a, label_b, show_legend, split_fn):
    colors = ColorSystem()
    tokens_a = split_fn(a)
    tokens_b = split_fn(b)
    sep = "" if split_fn is list else " "

    line_a, line_b = _apply_opcodes(tokens_a, tokens_b, sep)

    legend = ""
    if show_legend:
        legend = (
            colors.grey("  legend: ")
            + colors.red("removed")
            + colors.grey(" / ")
            + colors.green("added")
            + "\n"
        )

    label_width = max(len(label_a), len(label_b)) + 2
    return (
        legend
        + colors.bold(f"{label_a:<{label_width}}") + line_a + "\n"
        + colors.bold(f"{label_b:<{label_width}}") + line_b
    )


def _diff_line(a, b, label_a, label_b, context_lines, show_legend):
    colors = ColorSystem()
    lines_a = a.splitlines(keepends=True)
    lines_b = b.splitlines(keepends=True)

    legend = ""
    if show_legend:
        legend = (
            colors.grey(f"--- {label_a}\n")
            + colors.grey(f"+++ {label_b}\n")
        )

    parts = [legend]
    matcher = difflib.SequenceMatcher(None, lines_a, lines_b, autojunk=False)
    groups = list(matcher.get_grouped_opcodes(context_lines))

    if not groups:
        parts.append(colors.grey("(no differences)\n"))
        return "".join(parts)

    for group in groups:
        first, last = group[0], group[-1]
        i1 = first[1]
        i2 = last[2]
        j1 = first[3]
        j2 = last[4]
        parts.append(colors.grey(f"@@ -{i1+1},{i2-i1} +{j1+1},{j2-j1} @@\n"))

        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for line in lines_a[i1:i2]:
                    parts.append(colors.grey(" " + line.rstrip("\n")) + "\n")
            elif tag in ("delete", "replace"):
                for line in lines_a[i1:i2]:
                    parts.append(colors.red("-" + line.rstrip("\n")) + "\n")
                if tag == "replace":
                    for line in lines_b[j1:j2]:
                        parts.append(colors.green("+" + line.rstrip("\n")) + "\n")
            elif tag == "insert":
                for line in lines_b[j1:j2]:
                    parts.append(colors.green("+" + line.rstrip("\n")) + "\n")
    return "".join(parts)

def userinput(
    prompt: str = "",
    validator: Optional[Callable[[str], bool]] = None,
    error_msg: str = "Invalid input. Please try again.",
    max_attempts: Optional[int] = None,
    strip: bool = True,
) -> str:
    colors = ColorSystem()
    attempts = 0
    
    while True:
        try:
            value = input(colors.bold(prompt))
        except (EOFError, KeyboardInterrupt):
            print()
            raise
        
        if strip:
            value = value.strip()
        
        if validator is not None:
            try:
                if not validator(value):
                    print(colors.error(error_msg))
                    attempts += 1
                    if max_attempts is not None and attempts >= max_attempts:
                        raise ValueError(f"Max attempts ({max_attempts}) exceeded")
                    continue
            except Exception as e:
                print(colors.error(str(e)))
                attempts += 1
                if max_attempts is not None and attempts >= max_attempts:
                    raise
                continue
        
        return value

class _RecorderStream(io.TextIOBase):
    def __init__(self, original_stream, log_file, stream_name, colors):
        self._original = original_stream
        self._log_file = log_file
        self._stream_name = stream_name
        self._colors = colors
        self._buffer = ""

    def write(self, text: str) -> int:
        if text:
            self._original.write(text)
            self._original.flush()
            self._buffer += text
            if text.endswith("\n"):
                self._flush_buffer()
        return len(text)

    def _flush_buffer(self):
        if self._buffer:
            content = _strip_ansi(self._buffer.rstrip("\n"))
            if content:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                if self._stream_name == "input":
                    line = f"[{timestamp}] [INPUT] {content}\n"
                else:
                    line = f"[{timestamp}] [OUTPUT] {content}\n"
                self._log_file.write(line)
                self._log_file.flush()
            self._buffer = ""

    def flush(self):
        self._original.flush()
        self._flush_buffer()

    def readline(self, size=-1):
        if self._stream_name == "input":
            line = self._original.readline(size)
            self._buffer += line
            if line.endswith("\n"):
                self._flush_buffer()
            return line
        return ""

    def isatty(self):
        return self._original.isatty()


@contextmanager
def recorder(
    log_file: str = "session.log",
    timestamp_format: str = "%Y-%m-%d %H:%M:%S",
    include_header: bool = True,
):
    colors = ColorSystem()
    log_path = log_file

    with open(log_path, "w", encoding="utf-8") as f:
        if include_header:
            start_time = datetime.now().strftime(timestamp_format)
            header = f"=== CLI Session Started: {start_time} ===\n"
            f.write(header)
            f.flush()

        input_wrapper = _RecorderStream(sys.stdin, f, "input", colors)
        output_wrapper = _RecorderStream(sys.stdout, f, "output", colors)

        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_input = builtins.input

        sys.stdin = input_wrapper
        sys.stdout = output_wrapper

        def recorded_input(prompt=""):
            if prompt:
                output_wrapper.write(prompt)
            return old_input()

        builtins.input = recorded_input

        try:
            yield
        finally:
            output_wrapper._flush_buffer()
            input_wrapper._flush_buffer()
            
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            builtins.input = old_input

            end_time = datetime.now().strftime(timestamp_format)
            footer = f"=== CLI Session Ended: {end_time} ===\n"
            f.write(footer)
            f.flush()

def cls():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

class Platform(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"
    FREEBSD = "freebsd"
    OTHER = "other"

    @classmethod
    def current(cls) -> "Platform":
        system = platform.system().lower()
        release = platform.release().lower()
        
        if system == "windows":
            return cls.WINDOWS
        elif system == "linux":
            if "android" in release:
                return cls.ANDROID
            return cls.LINUX
        elif system == "darwin":
            if platform.machine().startswith("iPhone") or platform.machine().startswith("iPad"):
                return cls.IOS
            return cls.MACOS
        elif "freebsd" in system:
            return cls.FREEBSD
        else:
            return cls.OTHER


class PlatformActions:
    
    def __init__(self):
        self._actions: dict[Platform, Callable] = {}
    
    def register(self, platform: Platform, func: Callable) -> None:
        self._actions[platform] = func
    
    def get(self, platform: Platform) -> Optional[Callable]:
        return self._actions.get(platform)
    
    def execute(self, platform: Platform, *args, **kwargs) -> Any:
        func = self.get(platform)
        if func is None:
            raise ValueError(f"No action registered for platform: {platform.value}")
        return func(*args, **kwargs)


def on_platform(
    windows: Optional[Callable] = None,
    linux: Optional[Callable] = None,
    macos: Optional[Callable] = None,
    android: Optional[Callable] = None,
    ios: Optional[Callable] = None,
    freebsd: Optional[Callable] = None,
    other: Optional[Callable] = None,
    default: Optional[Callable] = None,
    *args,
    **kwargs
) -> Any:
    current = Platform.current()
    actions = PlatformActions()
    
    for plat, func in [
        (Platform.WINDOWS, windows),
        (Platform.LINUX, linux),
        (Platform.MACOS, macos),
        (Platform.ANDROID, android),
        (Platform.IOS, ios),
        (Platform.FREEBSD, freebsd),
        (Platform.OTHER, other or default),
    ]:
        if func is not None:
            actions.register(plat, func)
    
    try:
        return actions.execute(current, *args, **kwargs)
    except ValueError:
        if default is not None:
            return default(*args, **kwargs)
        raise

def get_platform_info() -> dict:
    return {
        "platform": Platform.current().value,
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }

def _read_key_unix() -> str:
    fd = sys.stdin.fileno()
    old = _termios.tcgetattr(fd)
    try:
        _tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                return f"\x1b[{ch3}"
            return ch2
        return ch
    finally:
        _termios.tcsetattr(fd, _termios.TCSADRAIN, old)


def _read_key_windows() -> str:
    ch = _msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        ch2 = _msvcrt.getwch()
        return f"\x00{ch2}"
    return ch


def _read_key() -> str:
    if platform.system() == "Windows":
        return _read_key_windows()
    return _read_key_unix()


def menu(
    items: list[str],
    *,
    title: str = "",
    loop: bool = True,
    show_hint: bool = True,
    input_mode: str = "arrows",
) -> str | None:
    if not items:
        raise ValueError("menu() requires at least one item")
    if input_mode not in ("arrows", "digits"):
        raise ValueError("input_mode must be 'arrows' or 'digits'")

    colors = ColorSystem()
    idx = 0
    n = len(items)

    def _draw():
        cls()
        if title:
            print(colors.bold(title))
        pad_width = len(str(n))
        for i, item in enumerate(items):
            if input_mode == "digits":
                prefix = f"{i + 1:>{pad_width}}. "
                if i == idx:
                    print(prefix + colors.blue(colors.bold(item)))
                else:
                    print(prefix + item)
            else:
                if i == idx:
                    print(colors.blue("❯ ") + colors.bold(item))
                else:
                    print("  " + item)
        if show_hint:
            if input_mode == "digits":
                print(colors.grey(f"\n  1-{n} select  Enter confirm  Esc cancel"))
            else:
                print(colors.grey("\n  ↑↓ navigate  Enter confirm  Esc cancel"))

    result = None
    input_buffer = ""
    try:
        while True:
            _draw()
            key = _read_key()
            
            if input_mode == "digits":
                if key.isdigit():
                    input_buffer += key
                    current_num = int(input_buffer)
                    if 1 <= current_num <= n:
                        idx = current_num - 1
                        result = items[idx]
                        break
                    else:
                        input_buffer = ""
                elif key in ("\x1b[A", "\x00H"):
                    if idx > 0:
                        idx -= 1
                    elif loop:
                        idx = n - 1
                    input_buffer = ""
                elif key in ("\x1b[B", "\x00P"):
                    if idx < n - 1:
                        idx += 1
                    elif loop:
                        idx = 0
                    input_buffer = ""
                elif key in ("\r", "\n"):
                    result = items[idx]
                    break
                elif key in ("\x03", "\x1b", "q"):
                    result = None
                    break
                else:
                    input_buffer = ""
            else:
                if key in ("\x1b[A", "\x00H"):
                    if idx > 0:
                        idx -= 1
                    elif loop:
                        idx = n - 1
                elif key in ("\x1b[B", "\x00P"):
                    if idx < n - 1:
                        idx += 1
                    elif loop:
                        idx = 0
                elif key in ("\r", "\n"):
                    result = items[idx]
                    break
                elif key in ("\x03", "\x1b", "q"):
                    result = None
                    break
    except KeyboardInterrupt:
        result = None

    cls()
    return result


def confirm(
    prompt: str = "Continue?",
    yes_values: list[str] | None = None,
    no_values: list[str] | None = None,
) -> bool:
    if yes_values is None:
        yes_values = ["y", "д"]
    if no_values is None:
        no_values = ["n", "н"]
    colors = ColorSystem()
    while True:
        sys.stdout.write(colors.bold(f"{prompt} (y/n): "))
        sys.stdout.flush()
        key = _read_key().lower()
        sys.stdout.write(key + "\n")
        sys.stdout.flush()
        if key in yes_values:
            return True
        if key in no_values:
            return False
        print(colors.error("Invalid input. Press y (yes) or n (no)."))


def watch(
    func: Callable[[], str],
    interval: float = 2.0,
    *,
    title: str = "watch",
    show_timestamp: bool = True,
) -> None:
    colors = ColorSystem()
    try:
        while True:
            cls()
            header = colors.bold(f"{title}")
            if show_timestamp:
                header += colors.grey(f"  -  {datetime.now().strftime('%H:%M:%S')}")
            print(header)
            print(colors.grey("─" * 40))
            try:
                output = func()
                print(output)
            except Exception as e:
                print(colors.error(str(e)))
            print(colors.grey(f"\nRefresh every {interval}s. Press Ctrl+C to exit."))
            time.sleep(interval)
    except KeyboardInterrupt:
        cls()


def notify(
    title: str = "Notification",
    message: str = "",
    *,
    urgency: str = "normal",
) -> bool:
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
            return True
        except Exception:
            return False
    
    elif system == "Darwin":
        try:
            escaped_title = title.replace('"', '\\"').replace("'", "'\\''")
            escaped_message = message.replace('"', '\\"').replace("'", "'\\''")
            script = f'''
            display notification "{escaped_message}" with title "{escaped_title}"
            '''
            subprocess.run(["osascript", "-e", script], check=True)
            return True
        except Exception:
            return False
    
    else:
        try:
            subprocess.run(
                ["notify-send", "-u", urgency, title, message],
                check=True,
                timeout=5
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

class _Logger:
    _LEVELS = {
        "debug":   ("DBG", "grey",   False),
        "info":    ("INF", "blue",   False),
        "success": ("OK ", "green",  False),
        "warn":    ("WRN", "yellow", False),
        "error":   ("ERR", "red",    True),
    }

    def __init__(self):
        self._colors  = ColorSystem()
        self._muted   = False
        self._file    = None
        self._show_ts = True

    def mute(self):   self._muted = True
    def unmute(self): self._muted = False

    def timestamps(self, enabled: bool = True):
        self._show_ts = enabled

    def set_file(self, path: str):
        self._file = open(path, "a", encoding="utf-8")

    def unset_file(self):
        if self._file:
            self._file.close()
            self._file = None

    def __call__(self, tag: str, *args, color: str = "blue", indent: int = 0, stderr: bool = False):
        if self._muted:
            return
        msg    = " ".join(str(a) for a in args)
        ts     = self._colors.grey(datetime.now().strftime("%H:%M:%S") + " ") if self._show_ts else ""
        pad    = "  " * indent
        label  = getattr(self._colors, color, self._colors.blue)(f"[{tag}]")
        line   = f"{ts}{pad}{label} {msg}"
        stream = sys.stderr if stderr else sys.stdout
        stream.write(line + "\n")
        stream.flush()
        if self._file:
            self._file.write(_strip_ansi(line) + "\n")
            self._file.flush()

    def _emit(self, level: str, *args, indent: int = 0):
        tag, color, use_stderr = self._LEVELS[level]
        self(tag, *args, color=color, indent=indent, stderr=use_stderr)

    def debug(self,   *args, indent: int = 0): self._emit("debug",   *args, indent=indent)
    def info(self,    *args, indent: int = 0): self._emit("info",    *args, indent=indent)
    def success(self, *args, indent: int = 0): self._emit("success", *args, indent=indent)
    def warn(self,    *args, indent: int = 0): self._emit("warn",    *args, indent=indent)
    def error(self,   *args, indent: int = 0): self._emit("error",   *args, indent=indent)


log = _Logger()


class _RetryCtx:
    def __init__(
        self,
        attempts:   int,
        delay:      float,
        backoff:    float,
        exceptions: tuple,
        on_fail:    str,
        label:      Optional[str],
    ):
        self.attempt: int             = 0
        self.failed:  list[Exception] = []
        self._done:   bool            = False
        self._wait:   float           = delay
        self._attempts   = attempts
        self._exceptions = exceptions
        self._on_fail    = on_fail
        self._label      = label
        self._backoff    = backoff

    def _report_failure(self, msg: str):
        if self._on_fail == "warn":    log.warn(msg)
        elif self._on_fail == "error": log.error(msg)

    def _report_retry(self, attempt: int, exc: Exception, wait: float):
        log("RTY",
            f"attempt {attempt}/{self._attempts} failed ({type(exc).__name__}: {exc})"
            + (f" — retrying in {wait:.1f}s" if wait > 0 else " — retrying"),
            color="yellow")

    def __enter__(self) -> "_RetryCtx":
        if self.attempt == 0:
            self.attempt = 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            if self.failed:
                log.success(f"succeeded on attempt {self.attempt}/{self._attempts}")
            self._done = True
            return False
        if not issubclass(exc_type, self._exceptions):
            return False
        self.failed.append(exc_val)
        if self.attempt >= self._attempts:
            self._report_failure(f"all {self._attempts} attempt(s) failed — {exc_val}")
            return False
        self._report_retry(self.attempt, exc_val, self._wait)
        time.sleep(self._wait)
        self._wait   *= self._backoff
        self.attempt += 1
        return True

    def __call__(self, func: Callable) -> Callable:
        name = self._label or func.__name__

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            wait, failed = self._wait, []
            for attempt in range(1, self._attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    if failed:
                        log.success(f"{name}: ok on attempt {attempt}/{self._attempts}")
                    return result
                except self._exceptions as exc:
                    failed.append(exc)
                    if attempt == self._attempts:
                        self._report_failure(f"{name}: all {self._attempts} attempt(s) failed — {exc}")
                        raise
                    self._report_retry(attempt, exc, wait)
                    time.sleep(wait)
                    wait *= self._backoff
        return _wrapper


def retry(
    attempts:   int           = 3,
    delay:      float         = 1.0,
    backoff:    float         = 1.0,
    exceptions: tuple         = (Exception,),
    on_fail:    str           = "warn",
    label:      Optional[str] = None,
) -> _RetryCtx:
    return _RetryCtx(attempts, delay, backoff, exceptions, on_fail, label)


def countdown(
    seconds: int,
    *,
    label: str = "Starting in",
    done_msg: str = "Done!",
) -> bool:
    colors = ColorSystem()
    try:
        for remaining in range(seconds, -1, -1):
            mins, secs = divmod(remaining, 60)
            time_str = f"{mins:02d}:{secs:02d}"
            sys.stdout.write(f"\r{label} {time_str}...")
            sys.stdout.flush()
            if remaining > 0:
                time.sleep(1)
        sys.stdout.write("\r" + " " * (len(label) + 12) + "\r")
        sys.stdout.write(colors.success(done_msg) + "\n")
        sys.stdout.flush()
        return True
    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * (len(label) + 12) + "\r")
        sys.stdout.write(colors.warning("Cancelled") + "\n")
        sys.stdout.flush()
        return False


def sparkline(
    values: list[float | int],
    *,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> str:
    if not values:
        return ""

    bars = "▁▂▃▄▅▆▇█"
    n_bars = len(bars)

    if min_val is None:
        min_val = min(values)
    if max_val is None:
        max_val = max(values)

    range_val = max_val - min_val

    if range_val == 0:
        return bars[-1] * len(values)

    result = []
    for v in values:
        idx = int((v - min_val) / range_val * (n_bars - 1))
        idx = max(0, min(n_bars - 1, idx))
        result.append(bars[idx])

    return "".join(result)


def calendar(
    data: Optional[dict[str, int]] = None,
    *,
    title: str = "",
    color_mode: str = "green",
    show_legend: bool = True,
    show_stats: bool = True,
    max_weeks: int = 20,
) -> None:
    colors = ColorSystem()

    palettes = {
        "green":  ["90", "22", "28", "34", "40"],
        "blue":   ["90", "17", "18", "20", "27"],
        "purple": ["90", "53", "54", "55", "93"],
        "orange": ["90", "130", "166", "202", "214"],
    }

    palette = palettes.get(color_mode, palettes["green"])

    if data is None:
        data = {}
        today = datetime.now().date()
        for i in range(365):
            date = today - timedelta(days=i)
            data[date.isoformat()] = random.choices(
                [0, 1, 2, 3, 4], weights=[50, 20, 15, 10, 5]
            )[0]

    today = datetime.now().date()
    days_to_show = max_weeks * 7
    start_date = today - timedelta(days=days_to_show - 1)

    nonzero = [v for v in data.values() if v and v > 0]
    _data_min = min(nonzero) if nonzero else 1
    _data_max = max(nonzero) if nonzero else 1

    weeks = []
    current_week = []

    first_weekday = start_date.weekday()
    for _ in range(first_weekday):
        current_week.append(None)

    for i in range(days_to_show):
        date = start_date + timedelta(days=i)
        count = data.get(date.isoformat(), 0)
        current_week.append(count)

        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []

    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    if title:
        print(colors.bold(title))
        print()

    month_positions = {}
    current_month = -1
    for i in range(days_to_show):
        date = start_date + timedelta(days=i)
        if date.month != current_month:
            week_idx = (i + first_weekday) // 7
            if week_idx not in month_positions and week_idx < len(weeks):
                month_positions[week_idx] = date.strftime("%b")
            current_month = date.month

    print("  ", end="")
    for week_idx in range(len(weeks)):
        if week_idx in month_positions:
            print(colors.grey(month_positions[week_idx]), end=" ")
        else:
            print("  ", end=" ")
    print()

    for row in range(7):
        if row == 0:
            print(colors.grey("Mon"), end=" ")
        elif row == 2:
            print(colors.grey("Wed"), end=" ")
        elif row == 4:
            print(colors.grey("Fri"), end=" ")
        else:
            print("   ", end="")

        for week in weeks:
            count = week[row] if row < len(week) else None
            if count is None:
                print("  ", end=" ")
            else:
                if count <= 0:
                    level = 0
                elif _data_max == _data_min:
                    level = 4
                else:
                    level = 1 + round((count - _data_min) / (_data_max - _data_min) * 3)
                fg_code = palette[level]
                
                if level == 0:
                    cell = colors.grey("░░")
                elif level == 1:
                    cell = colors.color256("▒▒", fg_code)
                elif level == 2:
                    cell = colors.color256("▓▓", fg_code)
                else:
                    cell = colors.color256("██", fg_code)
                print(cell, end=" ")
        print()

    if show_legend or show_stats:
        print()

    if show_legend:
        print(colors.grey("  Less "), end="")
        for i in range(5):
            fg_code = palette[i]
            if i == 0:
                cell = colors.grey("░░")
            elif i == 1:
                cell = colors.color256("▒▒", fg_code)
            elif i == 2:
                cell = colors.color256("▓▓", fg_code)
            else:
                cell = colors.color256("██", fg_code)
            print(cell, end="")
        print(colors.grey(" More"))

    if show_stats:
        displayed_dates = set()
        for i in range(days_to_show):
            date = start_date + timedelta(days=i)
            displayed_dates.add(date.isoformat())
        
        total = sum(v for k, v in data.items() if k in displayed_dates and v is not None)
        active_days = sum(1 for k, v in data.items() if k in displayed_dates and v and v > 0)
        max_streak = _calc_max_streak({k: v for k, v in data.items() if k in displayed_dates})
        print(colors.grey(f"  Total: {total} | Active days: {active_days} | Max streak: {max_streak} days"))


def _calc_max_streak(data: dict[str, int]) -> int:

    if not data:
        return 0

    dates = sorted(data.keys())
    max_streak = 0
    current_streak = 0
    prev_date = None

    for date_str in dates:
        if data.get(date_str, 0) == 0:
            if prev_date is not None:
                max_streak = max(max_streak, current_streak)
                current_streak = 0
            prev_date = None
            continue

        current_date = datetime.fromisoformat(date_str).date()
        if prev_date is None:
            current_streak = 1
        elif (current_date - prev_date).days == 1:
            current_streak += 1
        else:
            max_streak = max(max_streak, current_streak)
            current_streak = 1

        prev_date = current_date
        max_streak = max(max_streak, current_streak)

    return max_streak


T = TypeVar("T")


class _ProgressIterator:

    def __init__(
        self,
        iterable: Iterable[T],
        total: Optional[int] = None,
        label: str = "Progress",
        width: int = 30,
    ):
        self._iterable = iterable
        self._total = total
        self._label = label
        self._width = width
        self._index = 0
        self._iterator: Optional[Iterator[T]] = None
        self._started = False

    def __iter__(self) -> "_ProgressIterator":
        self._iterator = iter(self._iterable)
        if self._total is None:
            try:
                self._total = len(self._iterable)
            except TypeError:
                pass
        self._started = True
        return self

    def __enter__(self) -> "_ProgressIterator":
        self._started = True
        if self._total is None:
            try:
                self._total = len(self._iterable)
            except TypeError:
                pass
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._finish()

    def __next__(self) -> T:
        if self._iterator is None:
            self._iterator = iter(self._iterable)
            if self._total is None:
                try:
                    self._total = len(self._iterable)
                except TypeError:
                    pass
            self._started = True

        try:
            item = next(self._iterator)
            self._index += 1
            self._render()
            return item
        except StopIteration:
            self._finish()
            raise

    def update(self, n: int = 1) -> None:
        self._index += n
        self._render()

    def set(self, n: int) -> None:
        self._index = n
        self._render()

    def _render(self):
        if not self._started:
            return
        if self._total is None or self._total == 0:
            percent = 0
            bar = " " * self._width
        else:
            percent = self._index / self._total
            filled = max(1, int(self._width * percent)) if percent > 0 else 0
            bar = "█" * filled + "░" * (self._width - filled)

        if self._total:
            info = f"{self._index}/{self._total}"
        else:
            info = str(self._index)

        line = f"{self._label}: |{bar}| {percent*100:5.1f}% ({info})"
        if sys.stdout.isatty():
            sys.stdout.write("\r" + line + "\033[K")
        else:
            sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def _finish(self):
        if sys.stdout.isatty():
            sys.stdout.write("\n")
            sys.stdout.flush()


class _ProgressManual:

    def __init__(
        self,
        total: int,
        label: str = "Progress",
        width: int = 30,
    ):
        self._total = total
        self._label = label
        self._width = width
        self._index = 0

    def __iter__(self) -> "_ProgressManual":
        return self

    def __next__(self) -> int:
        if self._index >= self._total:
            self.close()
            raise StopIteration
        self._index += 1
        self._render()
        return self._index - 1

    def __enter__(self) -> "_ProgressManual":
        self._render()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def update(self, n: int = 1) -> None:
        self._index += n
        if self._index > self._total:
            self._index = self._total
        self._render()

    def set(self, n: int) -> None:
        self._index = n
        if self._index > self._total:
            self._index = self._total
        self._render()

    def _render(self):
        if self._total == 0:
            percent = 0
            bar = " " * self._width
            info = "0/0"
        else:
            percent = self._index / self._total
            filled = max(1, int(self._width * percent)) if percent > 0 else 0
            bar = "█" * filled + "░" * (self._width - filled)
            info = f"{self._index}/{self._total}"

        line = f"{self._label}: |{bar}| {percent*100:5.1f}% ({info})"
        if sys.stdout.isatty():
            sys.stdout.write("\r" + line + "\033[K")
        else:
            sys.stdout.write(line + "\n")
        sys.stdout.flush()

    def close(self) -> None:
        if sys.stdout.isatty():
            sys.stdout.write("\n")
            sys.stdout.flush()


def progress(
    iterable: Optional[Iterable[T]] = None,
    total: Optional[int] = None,
    label: str = "Progress",
    width: int = 30,
) -> Union[_ProgressIterator, _ProgressManual]:
    if iterable is not None:
        return _ProgressIterator(iterable, total=total, label=label, width=width)
    else:
        if total is None:
            raise ValueError("progress() requires either 'iterable' or 'total' argument")
        return _ProgressManual(total=total, label=label, width=width)

def banner(
    text: str,
    style: str = "block",
    color: str = "blue",
    align: str = "center",
    width: Optional[int] = None,
) -> None:
    colors = ColorSystem()
    colorize = getattr(colors, color, colors.blue)

    lines = text.splitlines() if "\n" in text else [text]
    max_len = max(len(l) for l in lines)
    w = max(width or 0, max_len + 4)

    def _align(s: str) -> str:
        pad = w - 2 - len(s)
        if align == "center":
            l, r = pad // 2, pad - pad // 2
            return " " * l + s + " " * r
        elif align == "right":
            return " " * pad + s
        else:
            return s + " " * pad

    if style == "block":
        tl, tr, bl, br, h, v = "╔", "╗", "╚", "╝", "═", "║"
    elif style == "thin":
        tl, tr, bl, br, h, v = "┌", "┐", "└", "┘", "─", "│"
    elif style == "dots":
        tl, tr, bl, br, h, v = "·", "·", "·", "·", "·", ":"
    else:
        for l in lines:
            sys.stdout.write(colorize(colors.bold("  " + _align(l) + "  ")) + "\n")
        sys.stdout.flush()
        return

    top    = tl + h * (w - 2) + tr
    bottom = bl + h * (w - 2) + br
    empty  = v + " " * (w - 2) + v

    sys.stdout.write(colorize(top) + "\n")
    sys.stdout.write(colorize(empty) + "\n")
    for l in lines:
        sys.stdout.write(colorize(v + _align(l) + v) + "\n")
    sys.stdout.write(colorize(empty) + "\n")
    sys.stdout.write(colorize(bottom) + "\n")
    sys.stdout.flush()

def password(
    prompt: str = "Password: ",
    *,
    confirm: bool = False,
    confirm_prompt: str = "Confirm password: ",
    min_length: int = 0,
    max_length: Optional[int] = None,
    validator: Optional[Callable[[str], bool]] = None,
    error_msg: str = "Invalid password. Try again.",
    mask: str = "*",
) -> str:
    colors = ColorSystem()

    def _read_masked(display_prompt: str) -> str:
        sys.stdout.write(colors.bold(display_prompt))
        sys.stdout.flush()

        if platform.system() == "Windows" or _msvcrt is not None:
            chars: list[str] = []
            while True:
                ch = _msvcrt.getwch()
                if ch in ("\r", "\n"):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    break
                elif ch in ("\x03",):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt
                elif ch in ("\x08", "\x7f"):
                    if chars:
                        chars.pop()
                        if mask:
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                elif ch == "\x00" or ch == "\xe0":
                    _msvcrt.getwch()
                else:
                    chars.append(ch)
                    if mask:
                        sys.stdout.write(mask)
                        sys.stdout.flush()
            return "".join(chars)

        if _tty is None or _termios is None:
            import getpass as _getpass
            return _getpass.getpass("")

        fd = sys.stdin.fileno()
        old = _termios.tcgetattr(fd)
        chars: list[str] = []
        try:
            _tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    break
                elif ch == "\x03":
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    raise KeyboardInterrupt
                elif ch == "\x1b":
                    sys.stdin.read(2)
                elif ch in ("\x08", "\x7f"):
                    if chars:
                        chars.pop()
                        if mask:
                            sys.stdout.write("\b \b")
                            sys.stdout.flush()
                else:
                    chars.append(ch)
                    if mask:
                        sys.stdout.write(mask)
                        sys.stdout.flush()
        finally:
            _termios.tcsetattr(fd, _termios.TCSADRAIN, old)
        return "".join(chars)

    while True:
        try:
            value = _read_masked(prompt)
        except (EOFError, KeyboardInterrupt):
            print()
            raise

        if min_length and len(value) < min_length:
            print(colors.error(f"Password must be at least {min_length} characters."))
            continue

        if max_length is not None and len(value) > max_length:
            print(colors.error(f"Password must be at most {max_length} characters."))
            continue

        if validator is not None:
            try:
                if not validator(value):
                    print(colors.error(error_msg))
                    continue
            except Exception as e:
                print(colors.error(str(e)))
                continue


        if confirm:
            try:
                confirm_value = _read_masked(confirm_prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                raise

            if value != confirm_value:
                print(colors.error("Passwords do not match. Try again."))
                continue

        return value

def env(
    name: str,
    default: Optional[str] = None,
    *,
    required: bool = False,
    dotenv: Optional[str] = None,
) -> Optional[str]:
    colors = ColorSystem()
    
    if dotenv is not None:
        _load_dotenv(dotenv)
    else:
        _load_dotenv_auto()
    
    value = os.environ.get(name)
    
    if value is not None:
        return value
    
    if required:
        msg = f"Required environment variable '{name}' is not set"
        log.error(msg)
        raise EnvironmentError(msg)
    
    if default is not None:
        return default
    
    return None


_dotenv_loaded: set = set()


def _load_dotenv(path: str) -> None:
    global _dotenv_loaded
    
    abs_path = os.path.abspath(path)
    if abs_path in _dotenv_loaded:
        return
    
    if not os.path.isfile(abs_path):
        return
    
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if (value.startswith('"') and value.endswith('"')) or \
                    (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                if key and value:
                    os.environ.setdefault(key, value)
        _dotenv_loaded.add(abs_path)
    except (IOError, OSError):
        pass


def _load_dotenv_auto() -> None:
    global _dotenv_loaded
    
    cwd = os.getcwd()
    dirs = [cwd]
    
    parent = cwd
    while True:
        new_parent = os.path.dirname(parent)
        if new_parent == parent:
            break
        parent = new_parent
        dirs.append(parent)
    
    for d in dirs:
        env_file = os.path.join(d, ".env")
        if os.path.isfile(env_file):
            _load_dotenv(env_file)

@dataclass
class RunResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    success: bool = field(init=False)

    def __post_init__(self):
        self.success = self.returncode == 0

_spinner = spinner


def run(
    cmd: Union[str, list[str]],
    *,
    live: bool = False,
    timeout: Optional[float] = None,
    spinner: bool = True,
    spinner_label: Optional[str] = None,
    cwd: Optional[str] = None,
    env: Optional[dict] = None,
    shell: Optional[bool] = None,
    capture: bool = True,
) -> RunResult:
    colors = ColorSystem()

    if shell is None:
        shell = isinstance(cmd, str)

    if isinstance(cmd, str) and not shell:
        import shlex
        cmd = shlex.split(cmd)

    if spinner_label is None:
        if isinstance(cmd, str):
            spinner_label = cmd.split()[0] if cmd else "Running"
        else:
            spinner_label = cmd[0] if cmd else "Running"

    stdout_buf, stderr_buf = io.StringIO(), io.StringIO()

    def _stream_output(pipe, buffer, color_fn=None):
        try:
            for line in iter(pipe.readline, ""):
                if line:
                    if color_fn:
                        sys.stdout.write(color_fn(line))
                    else:
                        sys.stdout.write(line)
                    sys.stdout.flush()
                    if capture:
                        buffer.write(line)
        finally:
            pipe.close()

    def _run_proc():
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE if (capture or live) else subprocess.DEVNULL,
            stderr=subprocess.PIPE if (capture or live) else subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            shell=shell,
            cwd=cwd,
            env=env,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )

        if live:
            stdout_thread, stderr_thread = None, None

            if proc.stdout:
                stdout_thread = threading.Thread(
                    target=_stream_output,
                    args=(proc.stdout, stdout_buf),
                    daemon=True
                )
                stdout_thread.start()

            if proc.stderr:
                stderr_thread = threading.Thread(
                    target=_stream_output,
                    args=(proc.stderr, stderr_buf, colors.yellow),
                    daemon=True
                )
                stderr_thread.start()

            try:
                proc.wait(timeout=timeout)
                if stdout_thread:
                    stdout_thread.join(timeout=1)
                if stderr_thread:
                    stderr_thread.join(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                sys.stdout.write(colors.error(f"Timeout after {timeout}s") + "\n")
                sys.stdout.flush()
                return RunResult(
                    returncode=-1,
                    stdout=stdout_buf.getvalue(),
                    stderr=stderr_buf.getvalue() + f"\n[TIMEOUT] Process killed after {timeout}s"
                )
        else:
            try:
                out, err = proc.communicate(timeout=timeout)
                if capture:
                    stdout_buf.write(out or "")
                    stderr_buf.write(err or "")
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                sys.stdout.write(colors.error(f"Timeout after {timeout}s") + "\n")
                sys.stdout.flush()
                return RunResult(
                    returncode=-1,
                    stdout=stdout_buf.getvalue(),
                    stderr=stderr_buf.getvalue() + f"\n[TIMEOUT] Process killed after {timeout}s"
                )

        return RunResult(
            returncode=proc.returncode,
            stdout=stdout_buf.getvalue(),
            stderr=stderr_buf.getvalue(),
        )

    try:
        if spinner and not live:
            with _spinner(spinner_label, done_msg=""):
                result = _run_proc()
        else:
            result = _run_proc()

        if not live and spinner:
            if result.success:
                sys.stdout.write(colors.success(f"{spinner_label} completed") + "\n")
            else:
                sys.stdout.write(colors.error(f"{spinner_label} failed (exit {result.returncode})") + "\n")
            sys.stdout.flush()

        return result

    except FileNotFoundError as e:
        sys.stdout.write(colors.error(f"Command not found: {cmd}") + "\n")
        sys.stdout.flush()
        return RunResult(returncode=-1, stderr=str(e))
    except Exception as e:
        sys.stdout.write(colors.error(f"Error: {e}") + "\n")
        sys.stdout.flush()
        return RunResult(returncode=-1, stderr=str(e))

def humanize(value: Union[int, float], kind: str = "num") -> str:
    if kind == "bytes":
        return _humanize_bytes(value)
    elif kind == "seconds":
        return _humanize_seconds(value)
    else:
        return _humanize_number(value)


def _humanize_bytes(value: Union[int, float]) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(value) < 1024.0:
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} EB"


def _humanize_seconds(value: Union[int, float]) -> str:
    value = int(value)
    if value < 60:
        return f"{value}s"
    
    parts = []
    hours, remainder = divmod(value, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
    
    return " ".join(parts)


def _humanize_number(value: Union[int, float]) -> str:
    value = float(value)
    abs_val = abs(value)
    
    if abs_val >= 1_000_000_000_000:
        return f"{value / 1_000_000_000_000:.1f}T"
    elif abs_val >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif abs_val >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif abs_val >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return str(int(value)) if value == int(value) else f"{value:.1f}"

@contextmanager
def tempdir(suffix: str = "", prefix: str = "tmp", dir: str = None):
    colors = ColorSystem()
    path = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    log.debug(f"[tempdir] created: {path}")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
        log.debug(f"[tempdir] removed: {path}")

if __name__ == "__main__":
    cls()
    print(ColorSystem().info("Tooly v{}".format(__version__)))