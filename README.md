# tooly

Lightweight terminal utilities for Python developers.

## Installation

```bash
pip install tooly-dev
```

## Usage

```python
import tooly
import time

colors = tooly.ColorSystem() # recommended
wait_time = 0.5

print(colors.info("Welcome to Tooly!")) # Color example

tooly.typewrite(colors.info("Example text"), delay=0.05) # Typewrite example

with tooly.measure("Example measure"):
    # Do something
    time.sleep(wait_time)

with tooly.spinner("Example spinner", done_msg="Exaple spinner done"):
    #Do something
    time.sleep(wait_time)

text = "Some interesting text with keywords"
print(colors.highlight(text, ["keywords", "text"], "yellow")) # text, keywords, color

# You can use indent for file tree for exaple
print(colors.indent("Example folder/", 0))
print(colors.indent("Example python file", 1))
print(colors.indent("Example readme file", 1))
print(colors.indent("Example subfolder/", 1))
print(colors.indent("howtodoerrors.txt", 2))
print(colors.indent("Example file", 0))
```

## License

MIT
