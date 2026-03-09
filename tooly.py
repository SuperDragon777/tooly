__version__ = "1.2.0"
__author__ = "SuperDragon777"
__all__ = ["ColorSystem", "measure", "spinner", "typewrite", "diff_highlight", "userinput", "recorder", "cls", "Platform", "on_platform", "menu", "confirm", "watch"]

import platform
import sys
import os
import time
from contextlib import contextmanager
from typing import Callable, Optional, Any
import difflib
from enum import Enum
import threading
import io
from datetime import datetime
import builtins
import re

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
) -> str | None:
    if not items:
        raise ValueError("menu() requires at least one item")

    colors = ColorSystem()
    idx = 0
    n = len(items)

    def _draw():
        cls()
        if title:
            print(colors.bold(title))
        for i, item in enumerate(items):
            if i == idx:
                print(colors.blue("❯ ") + colors.bold(item))
            else:
                print("  " + item)
        if show_hint:
            print(colors.grey("\n  ↑↓ navigate  Enter confirm  Esc cancel"))

    result = None
    try:
        while True:
            _draw()
            key = _read_key()
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


if __name__ == "__main__":
    cls()
    print(ColorSystem().info("Tooly v{}".format(__version__)))