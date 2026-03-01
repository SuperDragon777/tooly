__version__ = "1.0.0"
__author__ = "SuperDragon777"
__all__ = ["ColorSystem"]

import platform
import sys
import os
import time
from contextlib import contextmanager

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

if __name__ == "__main__":
    print(ColorSystem().info("Tooly v{}".format(__version__)))