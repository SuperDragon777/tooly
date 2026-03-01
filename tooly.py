__version__ = "1.1.0"
__author__ = "SuperDragon777"
__all__ = ["ColorSystem"]

import platform
import sys
import os
import time
from contextlib import contextmanager
import difflib
from enum import Enum

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
    import threading
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


if __name__ == "__main__":
    print(ColorSystem().info("Tooly v{}".format(__version__)))