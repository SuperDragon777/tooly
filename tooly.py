__version__ = "1.6.0"
__author__ = "SuperDragon777"
__all__ = ["ColorSystem", "measure", "spinner", "typewrite", "diff_highlight", "userinput", "recorder", "cls", "Platform", "on_platform", "menu", "confirm", "watch", "notify", "log", "retry", "countdown", "sparkline", "calendar", "progress", "banner", "password", "env", "run", "humanize", "tempdir", "lorem", "every", "saves", "patch", "shutdown", "reboot", "hibernate", "lock_device", "cancel_shutdown", "is_admin", "pkill", "plist", "hwid", "music", "download", "ensure_package", "package_version", "ram", "cpu", "unzip", "remove", "md5", "triangle"]

import platform
import sys
import os
import time
from contextlib import contextmanager
from typing import Callable, Optional, Any, Iterable, TypeVar, Iterator, Union, overload, List, Dict
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
import json
import hashlib
import glob
import pickle
import urllib.request
import urllib.parse
import keyword as _keyword
import tokenize as _tokenize
import io as _io
from collections import namedtuple as _namedtuple
import gzip
import bz2
import lzma
import tarfile
import zipfile

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
    
    def red(self, text):           return self._colorize(text, "91")
    def green(self, text):         return self._colorize(text, "92")
    def yellow(self, text):        return self._colorize(text, "93")
    def blue(self, text):          return self._colorize(text, "94")
    def magenta(self, text):       return self._colorize(text, "95")
    def cyan(self, text):          return self._colorize(text, "96")
    def white(self, text):         return self._colorize(text, "97")
    def grey(self, text):          return self._colorize(text, "90")
    def black(self, text):         return self._colorize(text, "30")
    
    def dark_red(self, text):      return self._colorize(text, "31")
    def dark_green(self, text):    return self._colorize(text, "32")
    def dark_yellow(self, text):   return self._colorize(text, "33")
    def dark_blue(self, text):     return self._colorize(text, "34")
    def dark_magenta(self, text):  return self._colorize(text, "35")
    def dark_cyan(self, text):     return self._colorize(text, "36")
    
    def bold(self, text):          return self._colorize(text, "1")
    def dim(self, text):           return self._colorize(text, "2")
    def italic(self, text):        return self._colorize(text, "3")
    def underline(self, text):     return self._colorize(text, "4")
    def blink(self, text):         return self._colorize(text, "5")
    def inverse(self, text):       return self._colorize(text, "7")
    def strikethrough(self, text): return self._colorize(text, "9")
    
    def bg_black(self, text):      return self._colorize(text, "40")
    def bg_red(self, text):        return self._colorize(text, "41")
    def bg_green(self, text):      return self._colorize(text, "42")
    def bg_yellow(self, text):     return self._colorize(text, "43")
    def bg_blue(self, text):       return self._colorize(text, "44")
    def bg_magenta(self, text):    return self._colorize(text, "45")
    def bg_cyan(self, text):       return self._colorize(text, "46")
    def bg_white(self, text):      return self._colorize(text, "47")
    def bg_grey(self, text):       return self._colorize(text, "100")
    
    def bg_color(self, text, bg_code: str, fg_code: str = "97"):
        if not self.support_colors:
            return text
        return f"\033[{bg_code};{fg_code}m{text}\033[0m"
    
    def color256(self, text: str, code: str) -> str:
        if not self.support_colors:
            return text
        return f"\033[38;5;{code}m{text}\033[0m"
    
    def bg_color256(self, text: str, code: str) -> str:
        if not self.support_colors:
            return text
        return f"\033[48;5;{code}m{text}\033[0m"
    
    def rgb(self, text: str, r: int, g: int, b: int) -> str:
        if not self.support_colors:
            return text
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    
    def bg_rgb(self, text: str, r: int, g: int, b: int) -> str:
        if not self.support_colors:
            return text
        return f"\033[48;2;{r};{g};{b}m{text}\033[0m"
    
    def success(self, text):   return self.green(f"[✓] {text}")
    def error(self, text):     return self.red(f"[X] {text}")
    def warning(self, text):   return self.yellow(f"[!] {text}")
    def info(self, text):      return self.blue(f"[i] {text}")
    def debug(self, text):     return self.grey(f"[~] {text}")
    def critical(self, text):  return self.bold(self.bg_red(f"[!!!] {text}"))
    
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
    
    def gradient(self, text: str, start: tuple[int, int, int], end: tuple[int, int, int]) -> str:
        if not self.support_colors or not text:
            return text
        n = max(len(text) - 1, 1)
        result = []
        for i, ch in enumerate(text):
            r = int(start[0] + (end[0] - start[0]) * i / n)
            g = int(start[1] + (end[1] - start[1]) * i / n)
            b = int(start[2] + (end[2] - start[2]) * i / n)
            result.append(self.rgb(ch, r, g, b))
        return "".join(result)
    
    def json(self, data, *, indent: int = 2) -> str:
        if not isinstance(data, str):
            text = __import__("json").dumps(data, ensure_ascii=False, indent=indent)
        else:
            try:
                parsed = __import__("json").loads(data)
                text = __import__("json").dumps(parsed, ensure_ascii=False, indent=indent)
            except Exception:
                text = data
        
        if not self.support_colors:
            return text
        
        result = []
        i = 0
        while i < len(text):
            ch = text[i]
            
            if ch == '"':
                j = i + 1
                while j < len(text):
                    if text[j] == '\\':
                        j += 2
                        continue
                    if text[j] == '"':
                        j += 1
                        break
                    j += 1
                token = text[i:j]
                after = text[j:].lstrip()
                if after.startswith(':'):
                    result.append(self.cyan(token))
                else:
                    result.append(self.green(token))
                i = j
                continue
            
            if ch in ('{', '}', '[', ']'):
                result.append(self.grey(ch))
                i += 1
                continue
            
            if ch == ':':
                result.append(self.grey(ch))
                i += 1
                continue
            
            if ch == ',':
                result.append(self.grey(ch))
                i += 1
                continue
            
            if ch in ('-', ) or ch.isdigit():
                j = i
                while j < len(text) and text[j] in '-0123456789.eE+':
                    j += 1
                result.append(self.yellow(text[i:j]))
                i = j
                continue
            
            if text[i:i+4] == 'true':
                result.append(self.magenta('true'))
                i += 4
                continue
            
            if text[i:i+5] == 'false':
                result.append(self.magenta('false'))
                i += 5
                continue
            
            if text[i:i+4] == 'null':
                result.append(self.red('null'))
                i += 4
                continue
            
            result.append(ch)
            i += 1
        
        return "".join(result)
        
    def python(self, code: str) -> str:
        if not self.support_colors:
            return code
        
        KEYWORDS = set(_keyword.kwlist)
        BUILTINS = set(dir(__import__("builtins")))
        DUNDER_RE = re.compile(r'^__\w+__$')
        
        SKIP = {
            _tokenize.ENCODING, _tokenize.ENDMARKER,
            _tokenize.NEWLINE, _tokenize.NL,
            _tokenize.INDENT, _tokenize.DEDENT,
        }
        
        def _color_for(ttype, tstr):
            if ttype == _tokenize.COMMENT:  return "grey"
            if ttype == _tokenize.STRING:   return "green"
            if ttype == _tokenize.NUMBER:   return "yellow"
            if ttype == _tokenize.OP:       return "grey"
            if ttype == _tokenize.NAME:
                if tstr in KEYWORDS:            return "magenta"
                if tstr in ("True","False","None"): return "cyan"
                if tstr in BUILTINS:            return "cyan"
                if DUNDER_RE.match(tstr):       return "dark_cyan"
            return None

        try:
            tokens = list(_tokenize.generate_tokens(_io.StringIO(code).readline))
        except _tokenize.TokenError:
            return code
        
        result = []
        prev_end = (1, 0)
        lines = code.splitlines(keepends=True)
        
        def _text_between(start, end):
            srow, scol = start
            erow, ecol = end
            if srow == erow:
                return lines[srow - 1][scol:ecol]
            out = lines[srow - 1][scol:]
            for r in range(srow, erow - 1):
                out += lines[r]
            out += lines[erow - 1][:ecol]
            return out
        
        for tok in tokens:
            ttype, tstr, tok_start, tok_end, _ = tok
            if ttype in SKIP:
                continue
        
            gap = _text_between(prev_end, tok_start)
            if gap:
                result.append(gap)
        
            color = _color_for(ttype, tstr)
            if color:
                colorize = getattr(self, color, None)
                result.append(colorize(tstr) if colorize else tstr)
            else:
                result.append(tstr)
        
            prev_end = tok_end
        
        tail = _text_between(prev_end, (len(lines), len(lines[-1]) if lines else 0))
        if tail:
            result.append(tail)
        
        return "".join(result)

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
    clear: bool = True,
) -> str | None:
    if not items:
        raise ValueError("menu() requires at least one item")
    if input_mode not in ("arrows", "digits"):
        raise ValueError("input_mode must be 'arrows' or 'digits'")
    colors = ColorSystem()
    idx = 0
    n = len(items)

    def _draw():
        if clear:
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

    if clear:
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

class Lorem:
    FIRST_NAMES_EN_MALE = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
        "Cameron", "Dakota", "Reese", "Skyler", "Emerson", "Finley", "Hayden",
        "Peyton", "River", "Sawyer", "Phoenix", "Rowan", "John", "Michael", "David",
        "James", "Robert", "William", "Christopher", "Daniel", "Matthew", "Anthony",
        "Mark", "Donald", "Steven", "Andrew", "Paul", "Joshua", "Kenneth", "Kevin",
        "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
        "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin",
        "Scott", "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Patrick",
        "Frank", "Raymond", "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam",
        "Henry", "Nathan", "Douglas", "Zachary", "Peter", "Kyle", "Walter", "Ethan",
        "Jeremy", "Harold", "Keith", "Christian", "Roger", "Noah", "Gerald", "Carl",
        "Terry", "Sean", "Austin", "Arthur", "Lawrence", "Jesse", "Dylan", "Bryan",
        "Joe", "Bruce", "Albert", "Willie", "Gabriel", "Logan", "Alan", "Juan", "Wayne",
        "Roy", "Ralph", "Randy", "Eugene", "Louis", "Philip", "Bobby", "Johnny", "Russell",
        "Caleb", "Luke", "Benjamin", "Elijah", "Isaac", "Owen", "Connor", "Evan",
        "Ian", "Cody", "Shane", "Troy", "Wesley", "Mitchell", "Vincent", "Chad",
        "Duane", "Rodney", "Curtis", "Norman", "Barry", "Leonard", "Marvin",
    ]

    FIRST_NAMES_EN_FEMALE = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
        "Cameron", "Dakota", "Reese", "Skyler", "Emerson", "Finley", "Hayden",
        "Peyton", "River", "Sawyer", "Phoenix", "Rowan", "Emma", "Olivia", "Isabella",
        "Mia", "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail", "Emily",
        "Elizabeth", "Sofia", "Ella", "Madison", "Scarlett", "Grace", "Chloe",
        "Victoria", "Layla", "Lily", "Aurora", "Zoey", "Penelope", "Hannah",
        "Lillian", "Addison", "Lucy", "Nora", "Leah", "Stella", "Hazel", "Violet",
        "Aria", "Claire", "Eleanor", "Anna", "Caroline", "Sarah", "Audrey", "Naomi",
        "Julia", "Madeline", "Katherine", "Eva", "Maya", "Natalie", "Alice", "Ruby",
        "Samantha", "Sadie", "Josephine", "Molly", "Allison", "Bella", "Kaylee",
        "Jasmine", "Morgan", "London", "Mackenzie", "Kylie", "Aubrey", "Alexis",
    ]

    FIRST_NAMES_RU_MALE = [
        "Иван", "Дмитрий", "Алексей", "Николай", "Сергей", "Владимир", "Пётр",
        "Андрей", "Михаил", "Александр", "Павел", "Денис", "Роман", "Артём",
        "Евгений", "Максим", "Владислав", "Тимофей", "Илья", "Кирилл", "Никита",
        "Георгий", "Борис", "Григорий", "Василий", "Степан", "Виктор", "Фёдор",
        "Олег", "Валерий", "Юрий", "Анатолий", "Вячеслав", "Константин", "Макар",
        "Даниил", "Матвей", "Захар", "Семён", "Арсений", "Леонид", "Эдуард",
        "Станислав", "Ярослав", "Всеволод", "Платон", "Святослав", "Ростислав",
    ]

    FIRST_NAMES_RU_FEMALE = [
        "Анна", "Елена", "Наташа", "Ольга", "Мария", "Татьяна", "Екатерина",
        "Юля", "Виктория", "София", "Анастасия", "Ирина", "Светлана", "Дарья",
        "Александра", "Валерия", "Алёна", "Вероника", "Кристина", "Полина",
        "Елизавета", "Любовь", "Надежда", "Алина", "Карина", "Лариса", "Нина",
        "Зоя", "Лидия", "Клавдия", "Галина", "Инна", "Диана", "Евгения", "Маргарита",
        "Антонина", "Оксана", "Римма", "Эльвира", "Милана", "Василиса", "Ульяна",
        "Варвара", "Агата", "Алевтина", "Раиса", "Тамара", "Жанна", "Роза",
    ]

    LAST_NAMES_EN = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
        "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
        "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
        "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
        "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
        "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
        "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
        "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
        "Ross", "Foster", "Jimenez", "Butler", "Simmons", "Romero", "Powell",
        "Jenkins", "Perry", "Russell", "Bell", "Coleman", "Henderson", "Barnes",
    ]

    LAST_NAMES_RU_MALE = [
        "Петров", "Иванов", "Смирнов", "Кузнецов", "Попов", "Соколов", "Лебедев",
        "Козлов", "Новиков", "Морозов", "Волков", "Андреев", "Алексеев", "Фёдоров",
        "Степанов", "Михайлов", "Орлов", "Николаев", "Романов", "Васильев",
        "Соловьёв", "Зайцев", "Павлов", "Баранов", "Крылов", "Сидоров", "Григорьев",
        "Макаров", "Егоров", "Абрамов", "Голубев", "Титов", "Беляев", "Кузьмин",
        "Фролов", "Дмитриев", "Калинин", "Гусев", "Комаров", "Борисов", "Куликов",
        "Быков", "Медведев", "Анисимов", "Ерёмин", "Королёв", "Сорокин", "Никитин",
    ]

    LAST_NAMES_RU_FEMALE = [
        "Петрова", "Иванова", "Смирнова", "Кузнецова", "Попова", "Соколова",
        "Лебедева", "Козлова", "Новикова", "Морозова", "Волкова", "Андреева",
        "Алексеева", "Фёдорова", "Степанова", "Михайлова", "Орлова", "Николаева",
        "Романова", "Васильева", "Соловьёва", "Зайцева", "Павлова", "Баранова",
        "Крылова", "Сидорова", "Григорьева", "Макарова", "Егорова", "Абрамова",
        "Голубева", "Титова", "Беляева", "Кузьмина", "Фролова", "Дмитриева",
        "Калинина", "Гусева", "Комарова", "Борисова", "Куликова", "Быкова",
        "Медведева", "Анисимова", "Ерёмина", "Королёва", "Сорокина", "Никитина",
    ]

    FIRST_NAMES = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
        "Cameron", "Dakota", "Reese", "Skyler", "Emerson", "Finley", "Hayden",
        "Peyton", "River", "Sawyer", "Phoenix", "Rowan", "Ivan", "Dmitri", "Alexei",
        "Nikolai", "Sergei", "Vladimir", "Peter", "Anna", "Elena", "Natasha",
        "Olga", "Maria", "Tatiana", "Ekaterina", "Julia", "Victoria", "Sophia",
        "Anastasia", "John", "Michael", "David", "James", "Robert", "William",
        "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven",
        "Andrew", "Paul", "Joshua", "Kenneth", "Kevin", "Brian", "George",
        "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan", "Jacob",
        "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin",
        "Scott", "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander",
        "Patrick", "Frank", "Raymond", "Jack", "Dennis", "Jerry", "Tyler",
        "Aaron", "Jose", "Adam", "Henry", "Nathan", "Douglas", "Zachary",
        "Peter", "Kyle", "Walter", "Ethan", "Jeremy", "Harold", "Keith",
        "Christian", "Roger", "Noah", "Gerald", "Carl", "Terry", "Sean",
        "Austin", "Arthur", "Lawrence", "Jesse", "Dylan", "Bryan", "Joe",
        "Bruce", "Albert", "Willie", "Gabriel", "Logan", "Alan", "Juan",
        "Wayne", "Roy", "Ralph", "Randy", "Eugene", "Louis", "Philip",
        "Bobby", "Johnny", "Russell", "Emma", "Olivia", "Isabella", "Mia",
        "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail", "Emily",
        "Elizabeth", "Sofia", "Avery", "Ella", "Madison", "Scarlett",
        "Grace", "Chloe", "Victoria", "Riley", "Layla", "Lily", "Aurora",
        "Zoey", "Penelope", "Hannah", "Lillian", "Addison", "Lucy", "Nora",
    ]

    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
        "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
        "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
        "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
        "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
        "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
        "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
        "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
        "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
        "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
        "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
        "Ross", "Foster", "Jimenez", "Petrov", "Ivanov", "Smirnov", "Kuznetsov",
        "Popov", "Sokolov", "Lebedev", "Kozlov", "Novikov", "Morozov",
        "Petrova", "Ivanova", "Smirnova", "Kuznetsova", "Popova", "Sokolova",
        "Lebedeva", "Kozlova", "Novikova", "Morozova", "Volkov", "Volkova",
        "Andreev", "Andreeva", "Alexeev", "Alexeeva", "Fedorov", "Fedorova",
        "Stepanov", "Stepanova", "Mikhailov", "Mikhailova", "Orlov", "Orlova",
    ]

    DOMAINS = [
        "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "mail.com",
        "protonmail.com", "icloud.com", "aol.com", "zoho.com", "example.com",
        "test.com", "demo.com", "sample.org", "fake.net", "temp.io",
    ]

    LOREM_WORDS = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing",
        "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
        "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
        "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi",
        "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure",
        "in", "reprehenderit", "voluptate", "velit", "esse", "cillum", "fugiat",
        "nulla", "pariatur", "excepteur", "sint", "occaecat", "cupidatat", "non",
        "proident", "sunt", "culpa", "qui", "officia", "deserunt", "mollit",
        "anim", "id", "est", "laborum", "curabitur", "pretium", "tincidunt",
        "lacus", "nulla", "gravida", "orci", "a", "nec", "nisi", "sagittis",
        "sed", "turpis", "torquent", "per", "conubia", "nostra", "inceptos",
        "himenaeos", "integer", "scelerisque", "massa", "vitae", "justo",
        "nec", "facilisis", "cras", "tristique", "senectus", "et", "netus",
        "fames", "malesuada", "fames", "ante", "primis", "faucibus",
    ]

    CITIES = [
        "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
        "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose",
        "Austin", "Jacksonville", "Fort Worth", "Columbus", "Charlotte",
        "San Francisco", "Indianapolis", "Seattle", "Denver", "Washington",
        "Boston", "El Paso", "Nashville", "Detroit", "Oklahoma City",
        "Portland", "Las Vegas", "Memphis", "Louisville", "Baltimore",
        "Milwaukee", "Albuquerque", "Tucson", "Fresno", "Sacramento",
        "Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan",
        "Nizhny Novgorod", "Chelyabinsk", "Samara", "Omsk", "Rostov-on-Don",
        "Ufa", "Krasnoyarsk", "Voronezh", "Perm", "Volgograd",
        "London", "Paris", "Berlin", "Madrid", "Rome", "Vienna", "Amsterdam",
        "Brussels", "Stockholm", "Copenhagen", "Oslo", "Helsinki", "Dublin",
        "Tokyo", "Beijing", "Shanghai", "Seoul", "Singapore", "Hong Kong",
        "Mumbai", "Delhi", "Bangalore", "Sydney", "Melbourne", "Toronto",
    ]

    STREETS = [
        "Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Washington", "Lake",
        "Hill", "Sunset", "High", "Park", "Mill", "Union", "Market", "Spring",
        "River", "Center", "School", "Station", "Court", "Broadway", "Church",
        "Garden", "Central", "Forest", "Walnut", "State", "South", "North",
        "Lincoln", "Jefferson", "Madison", "Jackson", "Monroe", "Adams",
    ]

    def __init__(
        self,
        seed: Optional[int] = None,
        gender: Optional[str] = None,
        locale: Optional[str] = None,
    ):
        if seed is not None:
            random.seed(seed)
        self._gender = self._normalize_gender(gender) if gender is not None else None
        self._locale = self._normalize_locale(locale) if locale is not None else None

    def _normalize_gender(self, gender: str) -> str:
        value = gender.lower()
        if value in ("m", "male", "man"):
            return "male"
        if value in ("f", "female", "woman"):
            return "female"
        raise ValueError("gender must be 'male' or 'female'")

    def _normalize_locale(self, locale: str) -> str:
        value = locale.lower()
        if value in ("en", "english", "eng"):
            return "en"
        if value in ("ru", "russian", "rus"):
            return "ru"
        raise ValueError("locale must be 'en' or 'ru'")

    def _resolve_gender(self, gender: Optional[str] = None) -> Optional[str]:
        if gender is not None:
            return self._normalize_gender(gender)
        return self._gender

    def _resolve_locale(self, locale: Optional[str] = None) -> Optional[str]:
        if locale is not None:
            return self._normalize_locale(locale)
        return self._locale

    def _pick_gender(self, gender: Optional[str] = None) -> str:
        resolved = self._resolve_gender(gender)
        if resolved is not None:
            return resolved
        return random.choice(["male", "female"])

    def _pick_locale(self, locale: Optional[str] = None) -> str:
        resolved = self._resolve_locale(locale)
        if resolved is not None:
            return resolved
        return random.choice(["en", "ru"])

    def _first_name_pool(self, gender: str, locale: str) -> list:
        if locale == "en":
            return self.FIRST_NAMES_EN_MALE if gender == "male" else self.FIRST_NAMES_EN_FEMALE
        return self.FIRST_NAMES_RU_MALE if gender == "male" else self.FIRST_NAMES_RU_FEMALE

    def _last_name_pool(self, gender: str, locale: str) -> list:
        if locale == "en":
            return self.LAST_NAMES_EN
        return self.LAST_NAMES_RU_MALE if gender == "male" else self.LAST_NAMES_RU_FEMALE

    def words(self, count: int = 10) -> str:
        return " ".join(random.choice(self.LOREM_WORDS) for _ in range(count))

    def sentences(self, count: int = 3) -> str:
        sentences = []
        for _ in range(count):
            num_words = random.randint(8, 15)
            text = self.words(num_words)
            text = text[0].upper() + text[1:] + "."
            sentences.append(text)
        return " ".join(sentences)

    def paragraph(self, sentences_count: int = 5) -> str:
        return self.sentences(sentences_count)

    def paragraphs(self, count: int = 3) -> str:
        return "\n\n".join(self.paragraph(random.randint(3, 6)) for _ in range(count))

    def name(self, gender: Optional[str] = None, locale: Optional[str] = None) -> str:
        if self._resolve_gender(gender) is None and self._resolve_locale(locale) is None:
            return f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"
        picked_gender = self._pick_gender(gender)
        picked_locale = self._pick_locale(locale)
        first = random.choice(self._first_name_pool(picked_gender, picked_locale))
        last = random.choice(self._last_name_pool(picked_gender, picked_locale))
        return f"{first} {last}"

    def first_name(self, gender: Optional[str] = None, locale: Optional[str] = None) -> str:
        if self._resolve_gender(gender) is None and self._resolve_locale(locale) is None:
            return random.choice(self.FIRST_NAMES)
        picked_gender = self._pick_gender(gender)
        picked_locale = self._pick_locale(locale)
        return random.choice(self._first_name_pool(picked_gender, picked_locale))

    def last_name(self, gender: Optional[str] = None, locale: Optional[str] = None) -> str:
        if self._resolve_gender(gender) is None and self._resolve_locale(locale) is None:
            return random.choice(self.LAST_NAMES)
        picked_gender = self._pick_gender(gender)
        picked_locale = self._pick_locale(locale)
        return random.choice(self._last_name_pool(picked_gender, picked_locale))

    def email(
        self,
        domain: Optional[str] = None,
        gender: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> str:
        if self._resolve_gender(gender) is None and self._resolve_locale(locale) is None:
            first = random.choice(self.FIRST_NAMES).lower()
            last = random.choice(self.LAST_NAMES).lower()
        else:
            picked_gender = self._pick_gender(gender)
            picked_locale = self._pick_locale(locale)
            first = random.choice(self._first_name_pool(picked_gender, picked_locale)).lower()
            last = random.choice(self._last_name_pool(picked_gender, picked_locale)).lower()
        num = random.randint(1, 999)
        email_domain = domain or random.choice(self.DOMAINS)
        variants = [
            f"{first}{num}@{email_domain}",
            f"{first}.{last}@{email_domain}",
            f"{first}_{last}{num}@{email_domain}",
            f"{first}{last}@{email_domain}",
        ]
        return random.choice(variants)

    def phone(self, country_code: str = "+1") -> str:
        area = random.randint(200, 999)
        prefix = random.randint(200, 999)
        line = random.randint(1000, 9999)
        return f"{country_code} ({area}) {prefix}-{line}"

    def date(self, past: int = 365, start_date: Optional[datetime] = None) -> str:
        if start_date is None:
            start_date = datetime.now()
        days_ago = random.randint(0, past)
        date = start_date - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")

    def datetime(self, past: int = 365, start_date: Optional[datetime] = None) -> str:
        if start_date is None:
            start_date = datetime.now()
        days_ago = random.randint(0, past)
        seconds_ago = random.randint(0, 86400)
        dt = start_date - timedelta(days=days_ago, seconds=seconds_ago)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def address(self) -> str:
        street_num = random.randint(1, 9999)
        street = random.choice(self.STREETS)
        street_type = random.choice(["St", "Ave", "Blvd", "Rd", "Dr", "Ln", "Way"])
        city = random.choice(self.CITIES)
        state = random.choice(["CA", "NY", "TX", "FL", "IL", "WA", "MA", "CO"])
        zip_code = random.randint(10000, 99999)
        return f"{street_num} {street} {street_type}, {city}, {state} {zip_code}"

    def company(self) -> str:
        prefixes = [
            "Tech", "Global", "Smart", "Digital", "Cloud", "Data", "Net",
            "Cyber", "Info", "Soft", "Web", "Auto", "Bio", "Eco", "Fin",
            "Med", "Nano", "Quantum", "Virtual", "Advanced",
        ]
        suffixes = [
            "Corp", "Inc", "LLC", "Ltd", "Group", "Systems", "Solutions",
            "Technologies", "Labs", "Works", "Soft", "ware", "net", "ix",
        ]
        return f"{random.choice(prefixes)}{random.choice(suffixes)}"

    def job_title(self) -> str:
        titles = [
            "Software Engineer", "Product Manager", "Data Scientist",
            "UX Designer", "DevOps Engineer", "QA Engineer", "Project Manager",
            "Business Analyst", "Marketing Manager", "Sales Representative",
            "HR Manager", "Financial Analyst", "Operations Manager",
            "Customer Support", "Content Writer", "Graphic Designer",
            "System Administrator", "Network Engineer", "Security Analyst",
            "Machine Learning Engineer", "Frontend Developer",
            "Backend Developer", "Full Stack Developer", "Mobile Developer",
        ]
        return random.choice(titles)

    def uuid(self) -> str:
        hex_chars = "0123456789abcdef"
        parts = [
            "".join(random.choice(hex_chars) for _ in range(8)),
            "".join(random.choice(hex_chars) for _ in range(4)),
            "".join(random.choice(hex_chars) for _ in range(4)),
            "".join(random.choice(hex_chars) for _ in range(4)),
            "".join(random.choice(hex_chars) for _ in range(12)),
        ]
        return "-".join(parts)

    def ip(self, version: int = 4) -> str:
        if version == 4:
            return ".".join(str(random.randint(0, 255)) for _ in range(4))
        elif version == 6:
            hex_chars = "0123456789abcdef"
            parts = ["".join(random.choice(hex_chars) for _ in range(4)) for _ in range(8)]
            return ":".join(parts)
        else:
            raise ValueError(f"Unsupported IP version: {version}")

    def url(self) -> str:
        protocols = ["https", "http"]
        domains = ["www", "app", "api", "dev", "test", "demo"]
        domain_name = random.choice(["example", "test", "demo", "sample", "fake"])
        tld = random.choice(["com", "org", "net", "io", "co"])
        path = "/".join(self.words(random.randint(1, 3)).split())
        return f"{random.choice(protocols)}://{random.choice(domains)}.{domain_name}.{tld}/{path}"

    def credit_card_number(self) -> str:
        prefixes = ["4", "5", "51", "52", "53", "54", "55", "34", "37", "6011"]
        prefix = random.choice(prefixes)
        remaining = 16 - len(prefix)
        number = prefix + "".join(str(random.randint(0, 9)) for _ in range(remaining - 1))
        
        check_digit = random.randint(0, 9)
        return number + str(check_digit)

    def ssn(self) -> str:
        area = random.randint(1, 899)
        group = random.randint(1, 99)
        serial = random.randint(1, 9999)
        return f"{area:03d}-{group:02d}-{serial:04d}"

    def __call__(self, words: int = 10) -> str:
        return self.words(words)

lorem = Lorem()
class _EveryHandle:
    def __init__(self, func: Callable, interval: float, args: tuple = (), kwargs: dict = None):
        self._func = func
        self._interval = interval
        self._args = args
        self._kwargs = kwargs or {}
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._paused = False
    
    def _run(self):
        while not self._stop_event.is_set():
            if self._pause_event.is_set():
                self._pause_event.wait(timeout=0.1)
                continue
            try:
                self._func(*self._args, **self._kwargs)
            except Exception as e:
                log.error(f"every() task failed: {e}")
            self._stop_event.wait(timeout=self._interval)
    
    def start(self) -> "_EveryHandle":
        if self._running:
            return self
        self._running = True
        self._pause_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self
    
    def stop(self) -> None:
        self._stop_event.set()
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
    
    def pause(self) -> None:
        self._pause_event.set()
        self._paused = True
    
    def resume(self) -> None:
        self._pause_event.clear()
        self._paused = False
    
    @property
    def is_running(self) -> bool:
        return self._running and not self._stop_event.is_set()
    
    @property
    def is_paused(self) -> bool:
        return self._paused and self._pause_event.is_set()
    
    def __call__(self) -> None:
        self._func(*self._args, **self._kwargs)


@overload
def every(
    seconds: float,
    func: Callable,
    args: tuple = ...,
    kwargs: dict = ...,
    start_immediately: bool = ...,
) -> _EveryHandle: ...

@overload
def every(
    seconds: float,
    func: None = None,
    args: tuple = ...,
    kwargs: dict = ...,
    start_immediately: bool = ...,
) -> Callable[[Callable], _EveryHandle]: ...

def every(
    seconds: Optional[float] = None,
    func: Optional[Callable] = None,
    args: tuple = (),
    kwargs: dict = None,
    start_immediately: bool = True,
) -> _EveryHandle:
    if func is None:
        if seconds is None:
            raise TypeError("every() requires 'seconds' argument when used as decorator")
        def decorator(f: Callable) -> _EveryHandle:
            handle = _EveryHandle(f, seconds, args, kwargs or {})
            if start_immediately:
                handle.start()
            return handle
        return decorator

    if callable(seconds):
        func, seconds = seconds, func

    if not isinstance(seconds, (int, float)):
        raise TypeError("First argument must be interval (number) when func is provided")

    handle = _EveryHandle(func, seconds, args, kwargs or {})
    if start_immediately:
        handle.start()
    return handle

class _SavesManager:
    def __init__(self):
        self._default_folder = os.path.join(os.path.expanduser("~"), ".tooly", "saves")
        self._known_folders: set[str] = set()
        self.verbose: bool = True
    
    def _colors(self):
        return ColorSystem()

    def _resolve_folder(self, folder: Optional[str]) -> str:
        path = folder if folder is not None else self._default_folder
        self._known_folders.add(path)
        return path

    def _resolve_path(self, key: str, fmt: str, folder: Optional[str]) -> str:
        ext = ".pkl" if fmt == "pickle" else ".json"
        return os.path.join(self._resolve_folder(folder), key + ext)

    def _ensure_folder(self, folder: str) -> None:
        os.makedirs(folder, exist_ok=True)

    def save(self, key: str, data: Any, *, fmt: str = "json", folder: Optional[str] = None) -> None:
        colors = self._colors()
        folder_path = self._resolve_folder(folder)
        self._ensure_folder(folder_path)
        file_path = self._resolve_path(key, fmt, folder)

        try:
            if fmt == "pickle":
                with open(file_path, "wb") as f:
                    pickle.dump(data, f)
            elif fmt == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"Unknown format '{fmt}'. Use 'json' or 'pickle'.")
        except TypeError as e:
            if self.verbose:
                print(colors.error(f"Cannot serialize '{key}' as JSON: {e}. Try fmt='pickle'."))
            raise
        except Exception as e:
            if self.verbose:
                log.error(f"saves.save failed for '{key}': {e}")
            raise

        if self.verbose:
            print(colors.success(f"Saved '{key}' - {file_path}"))

    def load(self, key: str, *, fmt: str = "json", folder: Optional[str] = None, default: Any = None) -> Any:
        file_path = self._resolve_path(key, fmt, folder)

        if not os.path.isfile(file_path):
            return default

        try:
            if fmt == "pickle":
                with open(file_path, "rb") as f:
                    return pickle.load(f)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            log.error(f"saves.load failed for '{key}': {e}")
            return default

    def delete(self, key: str, *, fmt: str = "json", folder: Optional[str] = None) -> bool:
        colors = self._colors()
        file_path = self._resolve_path(key, fmt, folder)

        if not os.path.isfile(file_path):
            if self.verbose:
                print(colors.warning(f"'{key}' not found, nothing to delete."))
            return False

        try:
            os.remove(file_path)
            if self.verbose:
                print(colors.success(f"Deleted '{key}'"))
            return True
        except Exception as e:
            log.error(f"saves.delete failed for '{key}': {e}")
            return False

    def exists(self, key: str, *, fmt: str = "json", folder: Optional[str] = None) -> bool:
        return os.path.isfile(self._resolve_path(key, fmt, folder))

    def list(self, folder: Optional[str] = None) -> List[dict]:
        folder_path = self._resolve_folder(folder)
        results = []

        if not os.path.isdir(folder_path):
            return results

        for fname in sorted(os.listdir(folder_path)):
            if not (fname.endswith(".json") or fname.endswith(".pkl")):
                continue
            full_path = os.path.join(folder_path, fname)
            stat = os.stat(full_path)
            fmt = "pickle" if fname.endswith(".pkl") else "json"
            key = fname[:-4] if fmt == "json" else fname[:-4]
            results.append({
                "key":      key,
                "fmt":      fmt,
                "size":     stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
            })

        return results

    def find(self, key: str) -> List[dict]:
        results = []
        search_folders = self._known_folders | {self._default_folder}

        for folder_path in search_folders:
            if not os.path.isdir(folder_path):
                continue
            for fmt, ext in [("json", ".json"), ("pickle", ".pkl")]:
                full_path = os.path.join(folder_path, key + ext)
                if os.path.isfile(full_path):
                    stat = os.stat(full_path)
                    results.append({
                        "key":      key,
                        "fmt":      fmt,
                        "folder":   folder_path,
                        "size":     stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    })

        return results

    def info(self, key: str, *, fmt: str = "json", folder: Optional[str] = None) -> Optional[dict]:
        file_path = self._resolve_path(key, fmt, folder)

        if not os.path.isfile(file_path):
            return None

        stat = os.stat(file_path)
        return {
            "key":      key,
            "fmt":      fmt,
            "path":     file_path,
            "size":     stat.st_size,
            "created":  datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        }

    def clear(self, folder: Optional[str] = None, *, confirm: bool = True) -> int:
        colors = self._colors()
        folder_path = self._resolve_folder(folder)

        if not os.path.isdir(folder_path):
            if self.verbose:
                print(colors.warning(f"Folder '{folder_path}' does not exist."))
            return 0

        files = [
            f for f in os.listdir(folder_path)
            if f.endswith(".json") or f.endswith(".pkl")
        ]

        if not files:
            if self.verbose:
                print(colors.info(f"Nothing to clear in '{folder_path}'."))
            return 0

        if confirm:
            if not globals()["confirm"](f"Delete {len(files)} save(s) in '{folder_path}'?"):
                print(colors.warning("Cancelled."))
                return 0

        deleted = 0
        for fname in files:
            try:
                os.remove(os.path.join(folder_path, fname))
                deleted += 1
            except Exception as e:
                log.error(f"Could not delete '{fname}': {e}")

        if self.verbose:
            print(colors.success(f"Cleared {deleted} save(s) from '{folder_path}'"))

        return deleted

saves = _SavesManager()
class _PatchedObject:
    __slots__ = ("_patch_target", "_patch_ctx")

    def __init__(self, target: Any, ctx: "_PatchContext"):
        object.__setattr__(self, "_patch_target", target)
        object.__setattr__(self, "_patch_ctx", ctx)

    def __getattr__(self, name: str) -> Any:
        return getattr(object.__getattribute__(self, "_patch_target"), name)

    def __setattr__(self, name: str, new_value: Any) -> None:
        target = object.__getattribute__(self, "_patch_target")
        ctx    = object.__getattribute__(self, "_patch_ctx")
        try:
            old_value = getattr(target, name)
        except AttributeError:
            old_value = _PATCH_MISSING
        setattr(target, name, new_value)
        ctx._record(name, old_value, new_value)

    def __repr__(self) -> str:
        return repr(object.__getattribute__(self, "_patch_target"))


_PATCH_MISSING = object()


class _PatchContext:
    def __init__(
        self,
        obj: Any,
        *,
        label:      Optional[str]  = None,
        stream                     = None,
        show_types: bool           = False,
        show_summary: bool         = True,
        on_change: Optional[Callable[[str, Any, Any], None]] = None,
    ):
        self._obj          = obj
        self._label        = label or type(obj).__name__
        self._stream       = stream or sys.stdout
        self._show_types   = show_types
        self._show_summary = show_summary
        self._on_change    = on_change
        self._changes: list[tuple[str, Any, Any]] = []
        self._colors       = ColorSystem()
        self._proxy: Optional[_PatchedObject] = None

    def _fmt_val(self, v: Any) -> str:
        if v is _PATCH_MISSING:
            return self._colors.grey("<new>")
        r = repr(v)
        
        if len(r) > 60:
            r = r[:57] + "..."
        if self._show_types:
            r = f"{r} ({type(v).__name__})"
        return r

    def _record(self, name: str, old: Any, new: Any) -> None:
        colors = self._colors
        ts     = colors.grey(datetime.now().strftime("%H:%M:%S.%f")[:-3])
        label  = colors.yellow(f"[~] {self._label}")
        key    = colors.bold(f"{name:<18}")
        arrow  = colors.grey("-")

        if old is _PATCH_MISSING:
            
            line = f"{ts} {label} {key} {colors.green(self._fmt_val(new))} {colors.grey('(added)')}"
        elif old == new:
            
            line = f"{ts} {label} {key} {self._fmt_val(old)} {arrow} {colors.grey('(no change)')}"
        else:
            line = (
                f"{ts} {label} {key}"
                f" {colors.red(self._fmt_val(old))}"
                f" {arrow}"
                f" {colors.green(self._fmt_val(new))}"
            )

        self._stream.write(line + "\n")
        self._stream.flush()
        self._changes.append((name, old, new))

        if self._on_change is not None:
            try:
                self._on_change(name, old, new)
            except Exception as exc:
                self._stream.write(
                    self._colors.error(f"on_change callback raised: {exc}") + "\n"
                )

    def _print_summary(self) -> None:
        colors  = self._colors
        changed = [(n, o, v) for n, o, v in self._changes if o != v and o is not _PATCH_MISSING]
        added   = [(n, o, v) for n, o, v in self._changes if o is _PATCH_MISSING]
        no_op   = [(n, o, v) for n, o, v in self._changes if o == v]

        parts = []
        if changed:
            parts.append(colors.yellow(f"{len(changed)} changed"))
        if added:
            parts.append(colors.green(f"{len(added)} added"))
        if no_op:
            parts.append(colors.grey(f"{len(no_op)} no-op"))

        summary = ", ".join(parts) if parts else colors.grey("no changes")
        self._stream.write(
            colors.grey(f"[patch] {self._label}: ") + summary + "\n"
        )
        self._stream.flush()

    @property
    def changes(self) -> list[tuple[str, Any, Any]]:
        return list(self._changes)

    def reset(self) -> None:
        self._changes.clear()

    def revert(self, names: Optional[list[str]] = None) -> None:
        colors = self._colors
        for name, old, _ in self._changes:
            if names is not None and name not in names:
                continue
            if old is _PATCH_MISSING:
                try:
                    delattr(self._obj, name)
                except AttributeError:
                    pass
            else:
                setattr(self._obj, name, old)
            self._stream.write(
                colors.grey("[patch] reverted ") + colors.bold(name) + "\n"
            )
        self._stream.flush()

    def __enter__(self) -> "_PatchedObject":
        self._proxy = _PatchedObject(self._obj, self)
        return self._proxy

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._show_summary:
            self._print_summary()
        return False


def patch(
    obj: Any,
    *,
    label:        Optional[str]  = None,
    stream                       = None,
    show_types:   bool           = False,
    show_summary: bool           = True,
    on_change:    Optional[Callable[[str, Any, Any], None]] = None,
) -> _PatchContext:
    
    return _PatchContext(
        obj,
        label=label,
        stream=stream,
        show_types=show_types,
        show_summary=show_summary,
        on_change=on_change,
    )

def _power_delay_seconds(delay: Optional[float]) -> int:
    if delay is None or delay <= 0:
        return 0
    return max(0, int(delay))


def _power_run(cmd: list[str], *, shell: bool = False) -> bool:
    try:
        subprocess.run(
            cmd,
            check=False,
            shell=shell,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def _power_shutdown_reboot(action: str, *, delay: Optional[float], force: bool) -> bool:
    seconds = _power_delay_seconds(delay)
    
    def _windows() -> bool:
        flag = "/s" if action == "shutdown" else "/r"
        cmd: list[str] = ["shutdown", flag, "/t", str(seconds)]
        if force:
            cmd.append("/f")
        return _power_run(cmd)
    
    def _unix_shutdown_cmd(reboot: bool) -> list[str]:
        if shutil.which("systemctl"):
            base = ["systemctl", "reboot" if reboot else "poweroff"]
            if force:
                base.append("--force")
            if seconds > 0:
                base = ["systemd-run", f"--on-active={seconds}s", "--timer-property=AccuracySec=1s"] + base
            return base
        when = "now" if seconds <= 0 else f"+{max(1, (seconds + 59) // 60)}"
        cmd = ["shutdown", "-r" if reboot else "-h", when]
        if force:
            cmd.insert(1, "-f")
        return cmd
    
    def _linux() -> bool:
        return _power_run(_unix_shutdown_cmd(action == "reboot"))
    
    def _macos() -> bool:
        if shutil.which("osascript") and seconds <= 0 and not force:
            verb = "restart" if action == "reboot" else "shut down"
            script = f'tell application "System Events" to {verb}'
            return _power_run(["osascript", "-e", script])
        return _power_run(_unix_shutdown_cmd(action == "reboot"))
    
    def _freebsd() -> bool:
        when = "now" if seconds <= 0 else f"+{max(1, (seconds + 59) // 60)}"
        cmd = ["shutdown", "-r" if action == "reboot" else "-p", when]
        if force:
            cmd.insert(1, "-f")
        return _power_run(cmd)
    
    def _unsupported() -> bool:
        return False
    
    return on_platform(
        windows=_windows,
        linux=_linux,
        macos=_macos,
        freebsd=_freebsd,
        android=_unsupported,
        ios=_unsupported,
        default=_unsupported,
    )


def shutdown(*, delay: Optional[float] = None, force: bool = False) -> bool:
    return _power_shutdown_reboot("shutdown", delay=delay, force=force)


def reboot(*, delay: Optional[float] = None, force: bool = False) -> bool:
    return _power_shutdown_reboot("reboot", delay=delay, force=force)


def hibernate(*, force: bool = False) -> bool:
    def _windows() -> bool:
        cmd = ["shutdown", "/h"]
        if force:
            cmd.append("/f")
        return _power_run(cmd)
    
    def _linux() -> bool:
        if shutil.which("systemctl"):
            cmd = ["systemctl", "hibernate"]
            if force:
                cmd.append("--force")
            return _power_run(cmd)
        for candidate in (["pm-hibernate"], ["systemctl", "hibernate"]):
            if shutil.which(candidate[0]):
                return _power_run(candidate)
        return False
    
    def _macos() -> bool:
        if shutil.which("pmset"):
            return _power_run(["pmset", "sleepnow"])
        return False
    
    def _freebsd() -> bool:
        return _power_run(["zzz"])
    
    def _unsupported() -> bool:
        return False
    
    return on_platform(
        windows=_windows,
        linux=_linux,
        macos=_macos,
        freebsd=_freebsd,
        android=_unsupported,
        ios=_unsupported,
        default=_unsupported,
    )


def lock_device() -> bool:
    def _windows() -> bool:
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception:
            return _power_run(["rundll32.exe", "user32.dll,LockWorkStation"])
        
    def _linux() -> bool:
        for cmd in (
            ["loginctl", "lock-session"],
            ["xdg-screensaver", "lock"],
            ["gnome-screensaver-command", "-l"],
            ["dm-tool", "lock"],
            ["cinnamon-screensaver-command", "-l"],
            ["mate-screensaver-command", "-l"],
            ["i3lock"],
            ["swaylock"],
        ):
            if shutil.which(cmd[0]):
                return _power_run(cmd)
        return False
    
    def _macos() -> bool:
        cg = "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession"
        if os.path.isfile(cg):
            return _power_run([cg, "-suspend"])
        return _power_run(["/usr/bin/open", "-a", "ScreenSaverEngine"])
    
    def _freebsd() -> bool:
        if shutil.which("xdg-screensaver"):
            return _power_run(["xdg-screensaver", "lock"])
        return False
    
    def _unsupported() -> bool:
        return False
    
    return on_platform(
        windows=_windows,
        linux=_linux,
        macos=_macos,
        freebsd=_freebsd,
        android=_unsupported,
        ios=_unsupported,
        default=_unsupported,
    )


def cancel_shutdown() -> bool:
    def _windows() -> bool:
        return _power_run(["shutdown", "/a"])
    
    def _unix() -> bool:
        return _power_run(["shutdown", "-c"])
    
    def _unsupported() -> bool:
        return False
    
    return on_platform(
        windows=_windows,
        linux=_unix,
        macos=_unix,
        freebsd=_unix,
        android=_unsupported,
        ios=_unsupported,
        default=_unsupported,
    )

def is_admin() -> bool:
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        try:
            return os.geteuid() == 0
        except AttributeError:
            return False

def pkill(
    name: Optional[str] = None,
    pid: Optional[int] = None,
    *,
    force: bool = False,
    signal: int = 15,
) -> bool:
    if name is None and pid is None:
        raise ValueError("Either 'name' or 'pid' must be provided")
    
    system = platform.system()
    
    if pid is not None:
        try:
            os.kill(pid, signal if not force else 9)
            return True
        except (ProcessLookupError, PermissionError, OSError):
            return False
    
    if system == "Windows":
        if force:
            return _power_run(["taskkill", "/F", "/IM", name])
        return _power_run(["taskkill", "/IM", name])
    else:
        sig = "-9" if force else f"-{signal}"
        return _power_run(["pkill", sig, name])

def plist(
    name: Optional[str] = None,
    pid: Optional[int] = None,
) -> List[Dict[str, Union[str, int]]]:
    result: List[Dict[str, Union[str, int]]] = []
    system = platform.system()
    
    if system == "Windows":
        try:
            output = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            for line in output.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.strip('"').split('","')
                if len(parts) >= 2:
                    proc_name = parts[0]
                    proc_pid = int(parts[1])
                    if pid is not None and proc_pid != pid:
                        continue
                    if name is not None and name.lower() not in proc_name.lower():
                        continue
                    result.append({"name": proc_name, "pid": proc_pid})
        except (subprocess.SubprocessError, ValueError, IndexError):
            pass
    else:
        try:
            for pid_path in glob.glob("/proc/[0-9]*/comm"):
                try:
                    proc_pid = int(pid_path.split("/")[2])
                    with open(pid_path, "r") as f:
                        proc_name = f.read().strip()
                    if pid is not None and proc_pid != pid:
                        continue
                    if name is not None and name != proc_name:
                        continue
                    result.append({"name": proc_name, "pid": proc_pid})
                except (OSError, ValueError, IOError):
                    continue
        except Exception:
            try:
                output = subprocess.check_output(
                    ["ps", "-e", "-o", "pid=,comm="],
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                for line in output.strip().split("\n"):
                    if not line.strip():
                        continue
                    parts = line.strip().split(None, 1)
                    if len(parts) == 2:
                        proc_pid = int(parts[0])
                        proc_name = parts[1]
                        if pid is not None and proc_pid != pid:
                            continue
                        if name is not None and name != proc_name:
                            continue
                        result.append({"name": proc_name, "pid": proc_pid})
            except (subprocess.SubprocessError, ValueError):
                pass
    
    return result

def uptime() -> float:
    system = platform.system()
    
    if system == "Windows":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            GetTickCount64 = kernel32.GetTickCount64
            GetTickCount64.restype = ctypes.c_ulonglong
            return GetTickCount64() / 1000.0
        except Exception:
            try:
                output = subprocess.check_output(
                    ["wmic", "os", "get", "lastbootuptime"],
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                lines = output.strip().split("\n")
                if len(lines) >= 2:
                    boot_str = lines[1].strip().split(".")[0]
                    boot_time = datetime.strptime(boot_str, "%Y%m%d%H%M%S")
                    return (datetime.now() - boot_time).total_seconds()
            except Exception:
                pass
            return -1
    else:
        try:
            with open("/proc/uptime", "r") as f:
                return float(f.read().split()[0])
        except Exception:
            try:
                output = subprocess.check_output(
                    ["sysctl", "-n", "kern.boottime"],
                    text=True,
                    encoding="utf-8",
                    errors="replace"
                )
                match = re.search(r"sec = (\d+)", output)
                if match:
                    boot_time = int(match.group(1))
                    return time.time() - boot_time
            except Exception:
                pass
            return -1

def hwid(*, stable: bool = True) -> str:
    def _get_windows() -> list[str]:
        parts = []
        queries = [
            ("wmic", "csproduct", "get", "uuid"),
            ("wmic", "cpu", "get", "processorid"),
            ("wmic", "diskdrive", "get", "serialnumber"),
            ("wmic", "baseboard", "get", "serialnumber"),
        ]
        for cmd in queries:
            try:
                out = subprocess.check_output(
                    cmd, text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                lines = [l.strip() for l in out.strip().split("\n")
                        if l.strip() and not l.strip().lower().startswith(cmd[-1].split("get")[-1].strip().lower())]
                if lines:
                    parts.append(lines[0])
            except Exception:
                pass
        return parts
    
    def _get_linux() -> list[str]:
        parts = []
        files = [
            "/etc/machine-id",
            "/var/lib/dbus/machine-id",
            "/sys/class/dmi/id/product_uuid",
            "/sys/class/dmi/id/board_serial",
            "/sys/class/dmi/id/product_serial",
        ]
        for path in files:
            try:
                with open(path, "r") as f:
                    val = f.read().strip()
                    if val:
                        parts.append(val)
            except Exception:
                pass
        try:
            out = subprocess.check_output(
                ["blkid", "-s", "UUID", "-o", "value"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            uuids = [l.strip() for l in out.strip().split("\n") if l.strip()]
            parts.extend(sorted(uuids)[:3])
        except Exception:
            pass
        return parts
    
    def _get_macos() -> list[str]:
        parts = []
        try:
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            for key in ("IOPlatformUUID", "IOPlatformSerialNumber"):
                match = re.search(rf'"{key}"\s*=\s*"([^"]+)"', out)
                if match:
                    parts.append(match.group(1))
        except Exception:
            pass
        try:
            out = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            for pattern in (r"Serial Number[^:]*:\s*(\S+)", r"Hardware UUID[^:]*:\s*(\S+)"):
                match = re.search(pattern, out)
                if match:
                    parts.append(match.group(1))
        except Exception:
            pass
        return parts
    
    def _get_freebsd() -> list[str]:
        parts = []
        for key in ("smbios.system.uuid", "smbios.system.serial", "smbios.baseboard.serial"):
            try:
                out = subprocess.check_output(
                    ["kenv", key], text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                val = out.strip()
                if val:
                    parts.append(val)
            except Exception:
                pass
        return parts
    
    def _default() -> list[str]:
        return []
    
    raw_parts: list[str] = on_platform(
        windows=_get_windows,
        linux=_get_linux,
        macos=_get_macos,
        freebsd=_get_freebsd,
        default=_default,
    )
    
    raw_parts = [p for p in raw_parts if p]
    
    if stable and not raw_parts:
        seed = platform.node() + platform.machine() + platform.processor()
        raw_parts = [seed]
    
    combined = "|".join(sorted(raw_parts) if not stable else raw_parts)
    return hashlib.sha256(combined.encode()).hexdigest().upper()

class _MusicManager:
    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._lock = threading.Lock()
        self._current: Optional[str] = None
        self._volume: float = 1.0
        self._player_proc: Optional[subprocess.Popen] = None
        self._on_end: Optional[Callable] = None
    
    def _resolve_backend(self) -> Optional[str]:
        for cmd in ("ffplay", "mpv", "mplayer", "afplay", "cvlc"):
            if shutil.which(cmd):
                return cmd
        return None

    def _build_cmd(self, backend: str, track: str) -> list[str]:
        vol = int(self._volume * 100)
        if backend == "ffplay":
            return ["ffplay", "-nodisp", "-autoexit", "-volume", str(vol), track]
        elif backend == "mpv":
            return ["mpv", "--no-video", f"--volume={vol}", track]
        elif backend == "mplayer":
            return ["mplayer", "-vo", "null", "-volume", str(vol), track]
        elif backend == "afplay":
            return ["afplay", "-v", str(self._volume), track]
        elif backend == "cvlc":
            return ["cvlc", "--intf", "dummy", "--gain", str(self._volume), track, "vlc://quit"]
        return []
    
    def _run(self, track: str, loop: bool):
        backend = self._resolve_backend()
        if backend is None:
            log.error("music: no supported backend found (ffplay, mpv, mplayer, afplay, cvlc)")
            return
        
        self._stop_event.clear()
        self._pause_event.clear()
        
        while True:
            cmd = self._build_cmd(backend, track)
            try:
                with self._lock:
                    self._player_proc = subprocess.Popen(
                        cmd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                while True:
                    if self._stop_event.is_set():
                        with self._lock:
                            if self._player_proc:
                                self._player_proc.terminate()
                                self._player_proc = None
                        return
                    if self._pause_event.is_set():
                        with self._lock:
                            if self._player_proc:
                                self._player_proc.terminate()
                        while self._pause_event.is_set():
                            if self._stop_event.is_set():
                                return
                            time.sleep(0.1)
                        if self._stop_event.is_set():
                            return
                        with self._lock:
                            self._player_proc = subprocess.Popen(
                                cmd,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                        continue
                    ret = self._player_proc.poll()
                    if ret is not None:
                        break
                    time.sleep(0.1)
            except Exception as e:
                log.error(f"music: playback error: {e}")
                return
            
            if self._stop_event.is_set():
                return
            if not loop:
                break
            
        if self._on_end:
            try:
                self._on_end()
            except Exception:
                pass
    
    def play(
        self,
        track: str,
        *,
        loop: bool = False,
        on_end: Optional[Callable] = None,
    ) -> None:
        self.stop()
        self._current = track
        self._on_end = on_end
        self._thread = threading.Thread(target=self._run, args=(track, loop), daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        self._stop_event.set()
        with self._lock:
            if self._player_proc:
                try:
                    self._player_proc.terminate()
                except Exception:
                    pass
                self._player_proc = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._current = None
    
    def pause(self) -> None:
        if not self.is_playing:
            return
        self._pause_event.set()
    
    def resume(self) -> None:
        if not self.is_paused:
            return
        self._pause_event.clear()
    
    def toggle(self) -> None:
        if self.is_paused:
            self.resume()
        else:
            self.pause()
    
    def volume(self, level: float) -> None:
        if not 0.0 <= level <= 1.0:
            raise ValueError("volume must be between 0.0 and 1.0")
        self._volume = level
        if self.is_playing and self._current:
            track = self._current
            self.play(track)
    
    @property
    def is_playing(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
            and not self._pause_event.is_set()
            and not self._stop_event.is_set()
        )
    
    @property
    def is_paused(self) -> bool:
        return (
            self._thread is not None
            and self._thread.is_alive()
            and self._pause_event.is_set()
        )
    
    @property
    def current(self) -> Optional[str]:
        return self._current
    
    def info(self) -> dict:
        return {
            "current": self._current,
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "volume": self._volume,
        }
    
    def wait(self) -> None:
        if self._thread and self._thread.is_alive():
            self._thread.join()

music = _MusicManager()
@dataclass
class DownloadResult:
    success: bool
    path: Optional[str] = None
    url: str = ""
    size: int = 0
    elapsed: float = 0.0
    error: Optional[str] = None
    
    def __bool__(self):
        return self.success

def download(
    url: str,
    dest: Optional[str] = None,
    *,
    filename: Optional[str] = None,
    overwrite: bool = False,
    timeout: float = 30.0,
    retries: int = 3,
    progress: bool = True,
    chunk_size: int = 1024 * 8,
    headers: Optional[dict] = None,
    on_progress: Optional[Callable[[int, int], None]] = None,
) -> DownloadResult:
    colors = ColorSystem()
    start = time.perf_counter()
    
    if dest is None:
        dest = os.getcwd()
    
    if filename is None:
        parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed.path) or "download"
    
    os.makedirs(dest, exist_ok=True)
    out_path = os.path.join(dest, filename)
    
    if not overwrite and os.path.isfile(out_path):
        log.warn(f"download: file already exists: {out_path}")
        return DownloadResult(
            success=False,
            path=out_path,
            url=url,
            error="File already exists. Use overwrite=True.",
        )
    
    last_error: Optional[str] = None
    
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                total = int(resp.headers.get("Content-Length", 0))
                downloaded = 0
                
                label = filename if len(filename) <= 30 else filename[:27] + "..."
                
                with open(out_path, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if on_progress:
                            try:
                                on_progress(downloaded, total)
                            except Exception:
                                pass
                        
                        if progress and sys.stdout.isatty():
                            if total:
                                pct = downloaded / total
                                width = 28
                                filled = int(width * pct)
                                bar = "█" * filled + "░" * (width - filled)
                                speed_label = _humanize_bytes(
                                    downloaded / max(time.perf_counter() - start, 0.001)
                                ) + "/s"
                                sys.stdout.write(
                                    f"\r{colors.blue(label)} |{bar}| "
                                    f"{pct*100:5.1f}% "
                                    f"{_humanize_bytes(downloaded)}/{_humanize_bytes(total)} "
                                    f"{colors.grey(speed_label)}\033[K"
                                )
                            else:
                                sys.stdout.write(
                                    f"\r{colors.blue(label)} "
                                    f"{_humanize_bytes(downloaded)} "
                                    f"{colors.grey('...')}\033[K"
                                )
                            sys.stdout.flush()
            
            if progress and sys.stdout.isatty():
                sys.stdout.write("\n")
                sys.stdout.flush()
            
            elapsed = time.perf_counter() - start
            size = os.path.getsize(out_path)
            
            log.success(
                f"downloaded '{filename}' -> {out_path} "
                f"({_humanize_bytes(size)}, {_format_duration(elapsed)})"
            )
            
            return DownloadResult(
                success=True,
                path=out_path,
                url=url,
                size=size,
                elapsed=elapsed,
            )
        
        except Exception as e:
            last_error = str(e)
            if progress and sys.stdout.isatty():
                sys.stdout.write("\n")
                sys.stdout.flush()
            if attempt < retries:
                log("RTY", f"download attempt {attempt}/{retries} failed: {e} - retrying", color="yellow")
                time.sleep(1.5 * attempt)
            else:
                log.error(f"download failed after {retries} attempt(s): {e}")
    
    if os.path.isfile(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass
    
    return DownloadResult(
        success=False,
        url=url,
        error=last_error,
    )

@dataclass
class PackageInfo:
    name: str
    installed: bool
    version: Optional[str] = None
    error: Optional[str] = None
    
    def __bool__(self):
        return self.installed

def package_version(name: str) -> Optional[str]:
    try:
        import importlib.metadata
        return importlib.metadata.version(name)
    except Exception:
        pass
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "pip", "show", name],
            text=True, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        for line in out.splitlines():
            if line.lower().startswith("version:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None

def ensure_package(
    name: str,
    *,
    version: Optional[str] = None,
    upgrade: bool = False,
    index_url: Optional[str] = None,
    quiet: bool = False,
    import_name: Optional[str] = None,
) -> PackageInfo:
    install_name = name if version is None else f"{name}=={version}"
    check_name = import_name or name
    
    current = package_version(name)
    
    if current is not None and not upgrade:
        if version is None or current == version:
            if not quiet:
                log.success(f"package '{name}' already installed ({current})")
            return PackageInfo(name=name, installed=True, version=current)
    
    action = "Upgrading" if upgrade and current else "Installing"
    if not quiet:
        log(
            "PKG",
            f"{action} '{install_name}'...",
            color="blue",
        )
    
    cmd = [sys.executable, "-m", "pip", "install", install_name, "--break-system-packages"]
    if upgrade:
        cmd.append("--upgrade")
    if index_url:
        cmd += ["--index-url", index_url]
    if quiet:
        cmd.append("-q")
    
    try:
        result = subprocess.run(
            cmd,
            text=True, encoding="utf-8", errors="replace",
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    
        if result.returncode != 0:
            err = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unknown error"
            log.error(f"ensure_package: failed to install '{name}': {err}")
            return PackageInfo(name=name, installed=False, error=err)
        
        new_version = package_version(name)
        
        try:
            import importlib
            importlib.import_module(check_name)
        except ImportError:
            pass
        
        if not quiet:
            log.success(f"'{name}' installed successfully ({new_version})")
        
        return PackageInfo(name=name, installed=True, version=new_version)
    
    except Exception as e:
        log.error(f"ensure_package: unexpected error: {e}")
        return PackageInfo(name=name, installed=False, error=str(e))

RamInfo = _namedtuple("RamInfo", ["total", "used", "free", "percent"])

def ram() -> RamInfo:
    def _windows() -> RamInfo:
        try:
            import ctypes
            class _MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]
            stat = _MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            total = stat.ullTotalPhys
            free  = stat.ullAvailPhys
            used  = total - free
            pct   = round(used / total * 100, 1) if total else 0.0
            return RamInfo(total=total, used=used, free=free, percent=pct)
        except Exception:
            return RamInfo(0, 0, 0, 0.0)

    def _linux() -> RamInfo:
        try:
            info = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2:
                        info[parts[0].rstrip(":")] = int(parts[1]) * 1024
            total    = info.get("MemTotal", 0)
            free_mem = info.get("MemFree", 0)
            buffers  = info.get("Buffers", 0)
            cached   = info.get("Cached", 0) + info.get("SReclaimable", 0) - info.get("Shmem", 0)
            used     = total - free_mem - buffers - cached
            free     = total - used
            pct      = round(used / total * 100, 1) if total else 0.0
            return RamInfo(total=total, used=used, free=free, percent=pct)
        except Exception:
            return RamInfo(0, 0, 0, 0.0)

    def _macos() -> RamInfo:
        try:
            out = subprocess.check_output(
                ["sysctl", "-n", "hw.memsize"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            total = int(out.strip())
            vm_out = subprocess.check_output(
                ["vm_stat"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            page_size = 16384
            ps_match = re.search(r"page size of (\d+) bytes", vm_out)
            if ps_match:
                page_size = int(ps_match.group(1))
            stats = {}
            for line in vm_out.splitlines():
                m = re.match(r"^(.+?):\s+(\d+)", line)
                if m:
                    stats[m.group(1).strip()] = int(m.group(2)) * page_size
            used = (
                stats.get("Pages active", 0) +
                stats.get("Pages wired down", 0) +
                stats.get("Pages occupied by compressor", 0)
            )
            free = total - used
            pct  = round(used / total * 100, 1) if total else 0.0
            return RamInfo(total=total, used=used, free=free, percent=pct)
        except Exception:
            return RamInfo(0, 0, 0, 0.0)

    def _freebsd() -> RamInfo:
        try:
            total_out = subprocess.check_output(
                ["sysctl", "-n", "hw.physmem"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            total = int(total_out.strip())
            vmstat_out = subprocess.check_output(
                ["vmstat", "-H"],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            lines = vmstat_out.strip().splitlines()
            if len(lines) >= 3:
                parts = lines[-1].split()
                free = int(parts[4]) * 1024 if len(parts) > 4 else 0
            else:
                free = 0
            used = total - free
            pct  = round(used / total * 100, 1) if total else 0.0
            return RamInfo(total=total, used=used, free=free, percent=pct)
        except Exception:
            return RamInfo(0, 0, 0, 0.0)

    def _default() -> RamInfo:
        return RamInfo(0, 0, 0, 0.0)

    return on_platform(
        windows=_windows,
        linux=_linux,
        macos=_macos,
        freebsd=_freebsd,
        default=_default,
    )

CpuInfo = _namedtuple("CpuInfo", ["count", "percent", "freq_mhz", "model"])

def cpu(interval: float = 0.1) -> CpuInfo:
    def _read_proc_stat():
        with open("/proc/stat", "r") as f:
            line = f.readline()
        fields = list(map(int, line.split()[1:]))
        idle  = fields[3] + (fields[4] if len(fields) > 4 else 0)
        total = sum(fields)
        return total, idle
    
    def _linux() -> CpuInfo:
        try:
            t1, i1 = _read_proc_stat()
            time.sleep(interval)
            t2, i2 = _read_proc_stat()
            dt = t2 - t1
            pct = round((1.0 - (i2 - i1) / dt) * 100, 1) if dt else 0.0
    
            count = 0
            try:
                with open("/proc/cpuinfo", "r") as f:
                    count = sum(1 for l in f if l.startswith("processor"))
            except Exception:
                pass
            
            model = ""
            freq  = 0.0
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if not model and line.startswith("model name"):
                            model = line.split(":", 1)[1].strip()
                        if not freq and line.startswith("cpu MHz"):
                            freq = round(float(line.split(":", 1)[1].strip()), 1)
                        if model and freq:
                            break
            except Exception:
                pass
            
            return CpuInfo(count=count, percent=pct, freq_mhz=freq, model=model)
        except Exception:
            return CpuInfo(0, 0.0, 0.0, "")
        
    def _windows() -> CpuInfo:
        try:
            import ctypes
            import ctypes.wintypes
            
            kernel32 = ctypes.windll.kernel32
            
            class _FILETIME(ctypes.Structure):
                _fields_ = [("dwLowDateTime", ctypes.wintypes.DWORD),
                            ("dwHighDateTime", ctypes.wintypes.DWORD)]
                
            def _ft_to_int(ft):
                return (ft.dwHighDateTime << 32) | ft.dwLowDateTime
            
            def _sample():
                idle = _FILETIME(); kern = _FILETIME(); user = _FILETIME()
                kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kern), ctypes.byref(user))
                return _ft_to_int(idle), _ft_to_int(kern) + _ft_to_int(user)
            
            i1, t1 = _sample()
            time.sleep(interval)
            i2, t2 = _sample()
            dt = t2 - t1
            pct = round((1.0 - (i2 - i1) / dt) * 100, 1) if dt else 0.0
            
            count = int(os.environ.get("NUMBER_OF_PROCESSORS", 0))
            
            model = ""
            freq  = 0.0
            try:
                out = subprocess.check_output(
                    ["wmic", "cpu", "get", "Name,MaxClockSpeed", "/format:csv"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                for line in out.splitlines():
                    parts = line.strip().split(",")
                    if len(parts) >= 3 and parts[1].strip().isdigit():
                        freq  = float(parts[1].strip())
                        model = parts[2].strip()
                        break
            except Exception:
                pass
            
            return CpuInfo(count=count, percent=pct, freq_mhz=freq, model=model)
        except Exception:
            return CpuInfo(0, 0.0, 0.0, "")
        
    def _macos() -> CpuInfo:
        try:
            out1 = subprocess.check_output(
                ["iostat", "-c", "2", "-w", str(interval)],
                text=True, encoding="utf-8", errors="replace",
                stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            pct = 0.0
            for line in reversed(out1.splitlines()):
                parts = line.split()
                if len(parts) >= 3 and parts[-1].replace(".", "").isdigit():
                    try:
                        idle = float(parts[-1])
                        pct  = round(100.0 - idle, 1)
                        break
                    except ValueError:
                        pass

            count = 0
            try:
                c_out = subprocess.check_output(
                    ["sysctl", "-n", "hw.logicalcpu"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                count = int(c_out.strip())
            except Exception:
                pass

            model = ""
            freq  = 0.0
            try:
                m_out = subprocess.check_output(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                model = m_out.strip()
                f_match = re.search(r"(\d+(?:\.\d+)?)\s*GHz", model)
                if f_match:
                    freq = round(float(f_match.group(1)) * 1000, 1)
            except Exception:
                pass

            return CpuInfo(count=count, percent=pct, freq_mhz=freq, model=model)
        except Exception:
            return CpuInfo(0, 0.0, 0.0, "")

    def _freebsd() -> CpuInfo:
        try:
            def _sample():
                out = subprocess.check_output(
                    ["sysctl", "-n", "kern.cp_time"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                vals = list(map(int, out.strip().split()))
                idle  = vals[4] if len(vals) > 4 else 0
                total = sum(vals)
                return total, idle

            t1, i1 = _sample()
            time.sleep(interval)
            t2, i2 = _sample()
            dt = t2 - t1
            pct = round((1.0 - (i2 - i1) / dt) * 100, 1) if dt else 0.0

            count = 0
            try:
                c_out = subprocess.check_output(
                    ["sysctl", "-n", "hw.ncpu"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                count = int(c_out.strip())
            except Exception:
                pass

            model = ""
            freq  = 0.0
            try:
                m_out = subprocess.check_output(
                    ["sysctl", "-n", "hw.model"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                model = m_out.strip()
                f_out = subprocess.check_output(
                    ["sysctl", "-n", "hw.clockrate"],
                    text=True, encoding="utf-8", errors="replace",
                    stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                freq = float(f_out.strip())
            except Exception:
                pass

            return CpuInfo(count=count, percent=pct, freq_mhz=freq, model=model)
        except Exception:
            return CpuInfo(0, 0.0, 0.0, "")

    def _default() -> CpuInfo:
        return CpuInfo(0, 0.0, 0.0, "")

    return on_platform(
        windows=_windows,
        linux=_linux,
        macos=_macos,
        freebsd=_freebsd,
        default=_default,
    )

@dataclass
class UnzipResult:
    success: bool
    dest: Optional[str] = None
    files: list[str] = field(default_factory=list)
    count: int = 0
    error: Optional[str] = None

    def __bool__(self):
        return self.success


def _unzip_progress(label: str, i: int, total: int):
    pct = i / total
    width = 28
    filled = int(width * pct)
    bar = "█" * filled + "░" * (width - filled)
    sys.stdout.write(
        f"\r{ColorSystem().blue(label)} |{bar}| "
        f"{pct*100:5.1f}% ({i}/{total})\033[K"
    )
    sys.stdout.flush()


def _detect_format(path: str) -> Optional[str]:
    name = path.lower()
    if name.endswith(".tar.gz") or name.endswith(".tgz"):   return "tar.gz"
    if name.endswith(".tar.bz2") or name.endswith(".tbz2"): return "tar.bz2"
    if name.endswith(".tar.xz") or name.endswith(".txz"):   return "tar.xz"
    if name.endswith(".tar.zst"):                           return "tar.zst"
    if name.endswith(".tar"):                               return "tar"
    if name.endswith(".zip"):                               return "zip"
    if name.endswith(".bz2"):                               return "bz2"
    if name.endswith(".gz"):                                return "gz"
    if name.endswith(".xz"):                                return "xz"
    if name.endswith(".zst"):                               return "zst"
    if name.endswith(".rar"):                               return "rar"
    if name.endswith(".7z"):                                return "7z"
    if zipfile.is_zipfile(path):                            return "zip"
    if tarfile.is_tarfile(path):                            return "tar"
    return None


def _unzip_zip(path, dest, overwrite, password, members, progress) -> UnzipResult:
    pwd = password.encode() if password else None
    label = os.path.basename(path)
    try:
        with zipfile.ZipFile(path, "r") as zf:
            all_members = zf.namelist()
            targets = members if members is not None else all_members
            targets = [m for m in targets if m in all_members]
            if not targets:
                return UnzipResult(success=False, dest=dest, error="No matching members")
            extracted = []
            for i, member in enumerate(targets, 1):
                out_path = os.path.join(dest, member)
                if not overwrite and os.path.exists(out_path):
                    continue
                if progress and sys.stdout.isatty():
                    _unzip_progress(label, i, len(targets))
                zf.extract(member, dest, pwd=pwd)
                extracted.append(out_path)
            if progress and sys.stdout.isatty():
                sys.stdout.write("\n"); sys.stdout.flush()
            return UnzipResult(success=True, dest=dest, files=extracted, count=len(extracted))
    except RuntimeError as e:
        return UnzipResult(success=False, error=str(e) + " (wrong password?)")
    except Exception as e:
        return UnzipResult(success=False, error=str(e))


def _unzip_tar(path, dest, overwrite, members, progress, mode="r:*") -> UnzipResult:
    label = os.path.basename(path)
    try:
        with tarfile.open(path, mode) as tf:
            all_members = tf.getnames()
            targets_names = set(members) if members is not None else None
            targets = [m for m in tf.getmembers()
                       if targets_names is None or m.name in targets_names]
            if not targets:
                return UnzipResult(success=False, dest=dest, error="No matching members")
            extracted = []
            for i, member in enumerate(targets, 1):
                out_path = os.path.join(dest, member.name)
                if not overwrite and os.path.exists(out_path):
                    continue
                if progress and sys.stdout.isatty():
                    _unzip_progress(label, i, len(targets))
                tf.extract(member, dest, set_attrs=False)
                extracted.append(out_path)
            if progress and sys.stdout.isatty():
                sys.stdout.write("\n"); sys.stdout.flush()
            return UnzipResult(success=True, dest=dest, files=extracted, count=len(extracted))
    except Exception as e:
        return UnzipResult(success=False, error=str(e))


def _unzip_single(path, dest, overwrite, progress, open_fn) -> UnzipResult:
    import shutil
    label = os.path.basename(path)
    out_name = re.sub(r'\.(gz|bz2|xz|zst)$', '', label, flags=re.IGNORECASE)
    out_path = os.path.join(dest, out_name)
    if not overwrite and os.path.exists(out_path):
        return UnzipResult(success=False, dest=dest, error="File already exists. Use overwrite=True.")
    try:
        with open_fn(path, "rb") as src, open(out_path, "wb") as dst:
            chunk_size = 1024 * 64
            total_written = 0
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                dst.write(chunk)
                total_written += len(chunk)
                if progress and sys.stdout.isatty():
                    sys.stdout.write(
                        f"\r{ColorSystem().blue(label)} "
                        f"{_humanize_bytes(total_written)} "
                        f"{ColorSystem().grey('...')}\033[K"
                    )
                    sys.stdout.flush()
        if progress and sys.stdout.isatty():
            sys.stdout.write("\n"); sys.stdout.flush()
        return UnzipResult(success=True, dest=dest, files=[out_path], count=1)
    except Exception as e:
        return UnzipResult(success=False, error=str(e))


def _unzip_rar(path, dest, overwrite, password, members, progress) -> UnzipResult:
    label = os.path.basename(path)
    try:
        import rarfile
        with rarfile.RarFile(path, "r") as rf:
            if password:
                rf.setpassword(password)
            all_members = rf.namelist()
            targets = members if members is not None else all_members
            targets = [m for m in targets if m in all_members]
            if not targets:
                return UnzipResult(success=False, dest=dest, error="No matching members")
            extracted = []
            for i, member in enumerate(targets, 1):
                out_path = os.path.join(dest, member)
                if not overwrite and os.path.exists(out_path):
                    continue
                if progress and sys.stdout.isatty():
                    _unzip_progress(label, i, len(targets))
                rf.extract(member, dest)
                extracted.append(out_path)
            if progress and sys.stdout.isatty():
                sys.stdout.write("\n"); sys.stdout.flush()
            return UnzipResult(success=True, dest=dest, files=extracted, count=len(extracted))
    except ImportError:
        pass
    for tool in ("unrar", "rar"):
        if shutil.which(tool):
            cmd = [tool, "x", "-y", path, dest + os.sep]
            if password:
                cmd.insert(2, f"-p{password}")
            res = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                extracted = [os.path.join(dp, f)
                            for dp, _, fns in os.walk(dest) for f in fns]
                return UnzipResult(success=True, dest=dest, files=extracted, count=len(extracted))
    return UnzipResult(success=False, error="RAR support requires 'rarfile' package or unrar/rar in PATH")


def _unzip_7z(path, dest, overwrite, password, members, progress) -> UnzipResult:
    try:
        import py7zr
        with py7zr.SevenZipFile(path, "r", password=password) as sz:
            targets = members if members is not None else None
            sz.extract(dest, targets=targets)
            extracted = [os.path.join(dp, f)
                        for dp, _, fns in os.walk(dest) for f in fns]
            return UnzipResult(success=True, dest=dest, files=extracted, count=len(extracted))
    except ImportError:
        pass
    for tool in ("7z", "7za", "7zr"):
        if shutil.which(tool):
            cmd = [tool, "x", path, f"-o{dest}", "-y"]
            if password:
                cmd.append(f"-p{password}")
            res = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if res.returncode == 0:
                extracted = [os.path.join(dp, f)
                            for dp, _, fns in os.walk(dest) for f in fns]
                return UnzipResult(success=True, dest=dest, files=extracted, count=len(extracted))
    return UnzipResult(success=False, error="7z support requires 'py7zr' package or 7z in PATH")


def _unzip_zst(path, dest, overwrite, progress) -> UnzipResult:
    try:
        import zstandard
        return _unzip_single(path, dest, overwrite, progress,
                            lambda p, m: zstandard.open(p, "rb"))
    except ImportError:
        pass
    if shutil.which("zstd"):
        out_name = re.sub(r'\.zst$', '', os.path.basename(path), flags=re.IGNORECASE)
        out_path = os.path.join(dest, out_name)
        res = subprocess.run(["zstd", "-d", path, "-o", out_path, "-f"],
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return UnzipResult(success=True, dest=dest, files=[out_path], count=1)
    return UnzipResult(success=False, error="zst support requires 'zstandard' package or zstd in PATH")


def unzip(
    path: str,
    dest: Optional[str] = None,
    *,
    overwrite: bool = True,
    password: Optional[str] = None,
    members: Optional[list[str]] = None,
    progress: bool = True,
) -> UnzipResult:
    

    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        log.error(f"unzip: file not found: {path}")
        return UnzipResult(success=False, error=f"File not found: {path}")

    fmt = _detect_format(path)
    if fmt is None:
        log.error(f"unzip: unsupported or unrecognized format: {path}")
        return UnzipResult(success=False, error="Unsupported or unrecognized archive format")

    if dest is None:
        base = path
        for ext in (".tar.gz", ".tar.bz2", ".tar.xz", ".tar.zst", ".tgz", ".tbz2", ".txz"):
            if path.lower().endswith(ext):
                base = path[: -len(ext)]
                break
        else:
            base = os.path.splitext(path)[0]
        dest = base

    dest = os.path.expanduser(dest)
    os.makedirs(dest, exist_ok=True)

    start = time.perf_counter()

    if fmt == "zip":
        result = _unzip_zip(path, dest, overwrite, password, members, progress)
    elif fmt in ("tar", "tar.gz", "tar.bz2", "tar.xz", "tar.zst"):
        result = _unzip_tar(path, dest, overwrite, members, progress)
    elif fmt == "gz":
        result = _unzip_single(path, dest, overwrite, progress, gzip.open)
    elif fmt == "bz2":
        result = _unzip_single(path, dest, overwrite, progress, bz2.open)
    elif fmt == "xz":
        result = _unzip_single(path, dest, overwrite, progress, lzma.open)
    elif fmt == "zst":
        result = _unzip_zst(path, dest, overwrite, progress)
    elif fmt == "rar":
        result = _unzip_rar(path, dest, overwrite, password, members, progress)
    elif fmt == "7z":
        result = _unzip_7z(path, dest, overwrite, password, members, progress)
    else:
        result = UnzipResult(success=False, error=f"Unsupported format: {fmt}")

    elapsed = time.perf_counter() - start

    if result.success:
        log.success(
            f"unzip: extracted {result.count} file(s) - {dest} "
            f"({_format_duration(elapsed)})"
        )
    else:
        log.error(f"unzip: {result.error}")

    return result

@dataclass
class RemoveResult:
    success: bool
    path: str
    error: Optional[str] = None

    def __bool__(self):
        return self.success


def remove(
    path: str,
    *,
    recursive: bool = False,
    missing_ok: bool = True,
    trash: bool = False,
) -> RemoveResult:
    path = os.path.expanduser(path)

    if not os.path.exists(path):
        if missing_ok:
            return RemoveResult(success=True, path=path)
        log.error(f"remove: path not found: {path}")
        return RemoveResult(success=False, path=path, error="Path not found")

    if trash:
        def _windows_trash() -> RemoveResult:
            try:
                from ctypes import windll, create_unicode_buffer
                import struct
                SHFileOperationW = windll.shell32.SHFileOperationW
                buf = create_unicode_buffer(path + "\0\0")
                params = struct.pack(
                    "PHHPHHPP",
                    0, 0x0003, 0,
                    buf, 0x0054, 0, None, None,
                )
                SHFileOperationW(params)
                return RemoveResult(success=True, path=path)
            except Exception:
                pass
            try:
                subprocess.run(
                    ["powershell", "-Command",
                    f'Add-Type -AssemblyName Microsoft.VisualBasic; '
                    f'[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('
                    f'"{path}",'
                    f'"OnlyErrorDialogs","SendToRecycleBin")'],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=True,
                )
                return RemoveResult(success=True, path=path)
            except Exception as e:
                return RemoveResult(success=False, path=path, error=str(e))

        def _macos_trash() -> RemoveResult:
            try:
                script = f'tell application "Finder" to delete POSIX file "{path}"'
                subprocess.run(
                    ["osascript", "-e", script],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, check=True,
                )
                return RemoveResult(success=True, path=path)
            except Exception as e:
                return RemoveResult(success=False, path=path, error=str(e))

        def _linux_trash() -> RemoveResult:
            for tool in ("gio", "trash-put", "gvfs-trash"):
                if shutil.which(tool):
                    cmd = ["gio", "trash", path] if tool == "gio" else [tool, path]
                    try:
                        subprocess.run(
                            cmd, stdin=subprocess.DEVNULL,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            check=True,
                        )
                        return RemoveResult(success=True, path=path)
                    except Exception:
                        continue
            try:
                ensure_package("send2trash", quiet=True)
                import send2trash
                send2trash.send2trash(path)
                return RemoveResult(success=True, path=path)
            except Exception as e:
                return RemoveResult(success=False, path=path, error=str(e))

        result = on_platform(
            windows=_windows_trash,
            macos=_macos_trash,
            linux=_linux_trash,
            default=lambda: RemoveResult(success=False, path=path, error="Trash not supported on this platform"),
        )

        if result.success:
            log.success(f"remove: moved to trash: {path}")
        else:
            log.error(f"remove: {result.error}")
        return result

    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            if recursive:
                shutil.rmtree(path)
            else:
                log.error(f"remove: '{path}' is a directory, use recursive=True")
                return RemoveResult(success=False, path=path, error="Is a directory. Use recursive=True.")
        log.success(f"remove: deleted '{path}'")
        return RemoveResult(success=True, path=path)
    except PermissionError as e:
        log.error(f"remove: permission denied: {path}")
        return RemoveResult(success=False, path=path, error=str(e))
    except Exception as e:
        log.error(f"remove: {e}")
        return RemoveResult(success=False, path=path, error=str(e))

def md5(
    data: Union[str, bytes, os.PathLike],
    *,
    chunk_size: int = 1024 * 256,
    encoding: str = "utf-8",
) -> str:
    h = hashlib.md5()

    if isinstance(data, (str, os.PathLike)) and os.path.isfile(data):
        with open(data, "rb") as f:
            if hasattr(f, "readinto"):
                buf = bytearray(chunk_size)
                view = memoryview(buf)
                while True:
                    n = f.readinto(buf)
                    if not n:
                        break
                    h.update(view[:n])
            else:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    h.update(chunk)
    elif isinstance(data, bytes):
        h.update(data)
    elif isinstance(data, str):
        h.update(data.encode(encoding))
    else:
        raise TypeError(f"Unsupported data type: {type(data)}")

    return h.hexdigest()

def triangle(
    char: str = "█",
    *,
    delay: float = 0.02,
    color: str = "cyan",
    end_delay: float = 0.5,
) -> None:
    colors = ColorSystem()
    colorize = getattr(colors, color, colors.blue)

    try:
        term_size = os.get_terminal_size()
        term_width = term_size.columns
        term_height = term_size.lines
    except OSError:
        term_width = 80
        term_height = 24

    rows = term_height - 1

    time.sleep(end_delay)
    cls()

    for i in range(1, rows + 1):
        ratio = i / rows
        count = max(1, round(ratio * term_width))
        if count % 2 == 0:
            count -= 1
        count = min(count, term_width)

        pad = (term_width - count) // 2
        line = " " * pad + colorize(char * count)

        sys.stdout.write(line + "\n")
        sys.stdout.flush()
        time.sleep(delay)

    time.sleep(end_delay)
    cls()

if __name__ == "__main__":
    cls()
    print(ColorSystem().info("Tooly v{}".format(__version__)))