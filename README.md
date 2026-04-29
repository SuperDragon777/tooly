# tooly

Lightweight but powerful terminal utilities for Python developers.

---

## Installation

```bash
pip install tooly-dev
```

---

# Overview

`tooly` provides a collection of utilities to improve CLI applications:

- Colored output
- Interactive input & menus
- Logging & debugging
- Progress & visualization
- System helpers
- Scheduling & retries
- File saves & temp tools
- Data generation (lorem)

---

# Quick Start

```python
import tooly

colors = tooly.ColorSystem()
print(colors.info("Hello, Tooly!"))
```

---

# Features

## 🎨 Colors & Text

```python
colors = tooly.ColorSystem()

print(colors.info("Info"))
print(colors.success("Success"))
print(colors.error("Error"))

text = "Some interesting text"
print(colors.highlight(text, ["interesting"], "yellow"))

print(colors.indent("folder/", 0))
print(colors.indent("file.py", 1))
```

---

## ⌨️ Input & Interaction

### userinput

```python
name = tooly.userinput("Name: ", validator=str.isalpha)
```

### menu

```python
choice = tooly.menu(["Start", "Stop", "Exit"])
```

### confirm

```python
if tooly.confirm("Continue?"):
    pass
```

### password

```python
pwd = tooly.password("Password: ", confirm=True)
```

---

## ⏱️ Execution Helpers

### typewrite

```python
tooly.typewrite("Hello", delay=0.05)
```

### measure

```python
with tooly.measure("Task"):
    pass
```

### spinner

```python
with tooly.spinner("Loading"):
    pass
```

### countdown

```python
tooly.countdown(5)
```

---

## 🔍 Diff

```python
tooly.diff_highlight(a, b, tooly.DiffMode.WORD)
tooly.diff_highlight(a, b, tooly.DiffMode.CHAR)
tooly.diff_highlight(a, b, tooly.DiffMode.LINE)
```

---

## 📊 Visualization

### progress

```python
for i in tooly.progress(range(100)):
    pass
```

### sparkline

```python
print(tooly.sparkline([1, 5, 3]))
```

### calendar

```python
tooly.calendar(title="Commits")
```

---

## 🧠 Logging

```python
tooly.log.set_file("app.log")

tooly.log.info("Info")
tooly.log.success("Success")
tooly.log.warn("Warning")
tooly.log.error("Error")
tooly.log.debug("Debug")
```

---

## 🔁 Retry

```python
@tooly.retry(attempts=3)
def fetch():
    pass
```

---

## 🔔 System & OS

### cls

```python
tooly.cls()
```

### on_platform

```python
tooly.on_platform(windows=lambda: "win")
```

### notify

```python
tooly.notify("Title", "Message")
```

---

## 📦 Files & Environment

### env

```python
url = tooly.env("DATABASE_URL", required=True)
```

### run

```python
tooly.run("ls -la")
```

### tempdir

```python
with tooly.tempdir() as tmp:
    pass
```

---

## 💾 Saves (Persistence)

```python
# save
tooly.saves.save("test", data)

# load
data = tooly.saves.load("test")

# exists
tooly.saves.exists("test")

# delete
tooly.saves.delete("test")

# list
tooly.saves.list()

# info
tooly.saves.info("test")

# find
tooly.saves.find("test")

# clear all
tooly.saves.clear()
```

---

## 📈 Humanize

```python
tooly.humanize(1500000, "bytes")
tooly.humanize(3600, "seconds")
```

---

## 🧪 Data Generation (Lorem)

```python
lorem = tooly.Lorem()

lorem.words(10)
lorem.sentences(3)
lorem.paragraph(5)

lorem.name()
lorem.email()
lorem.phone()
```

---

## ⏰ Scheduler

```python
@tooly.every(seconds=2)
def job():
    print("tick")
```

Control:

```python
job.stop()
job.pause()
job.resume()
```

---

## 🎬 Recorder

```python
with tooly.recorder("session.log"):
    print("recorded")
```

---

## 📺 Watch

```python
def get_time():
    return "time"


tooly.watch(get_time, interval=1)
```

---

## 🎨 Banner

```python
tooly.banner("Tooly")
```

---

# License

MIT
