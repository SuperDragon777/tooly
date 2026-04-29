import time
import os
from datetime import datetime
import requests
import tooly

# =========================
# CONFIG
# =========================
WAIT = 1.5
INTERACTIVE = False  # disable blocking input for demo runs

colors = tooly.ColorSystem()

# =========================
# HELPERS
# =========================

def pause(msg="Press Enter to continue..."):
    if INTERACTIVE:
        input(msg)


def section(title: str):
    print("\n" + colors.info(f"=== {title} ==="))


# =========================
# BASIC OUTPUT
# =========================

def basic_examples():
    section("Basic Output")
    print(colors.info("Welcome to Tooly!"))
    tooly.typewrite(colors.info("Typing animation..."), delay=0.03)

    with tooly.measure("Sleeping"):
        time.sleep(WAIT)

    with tooly.spinner("Working", done_msg="Done"):
        time.sleep(WAIT)


# =========================
# TEXT UTILITIES
# =========================

def text_examples():
    section("Text Utilities")

    text = "Some interesting text with keywords"
    print(colors.highlight(text, ["keywords", "text"], "yellow"))

    print(colors.indent("project/", 0))
    print(colors.indent("main.py", 1))
    print(colors.indent("README.md", 1))


# =========================
# DIFF
# =========================

def diff_examples():
    section("Diff")

    before = "SELECT id, name FROM users"
    after = "SELECT id, email FROM users LIMIT 100"
    print(tooly.diff_highlight(before, after, tooly.DiffMode.WORD))


# =========================
# INPUT
# =========================

def input_examples():
    if not INTERACTIVE:
        return

    section("User Input")

    name = tooly.userinput(
        "Name: ", validator=str.isalpha, error_msg="Only letters"
    )
    age = tooly.userinput(
        "Age: ", validator=str.isdigit, error_msg="Only digits"
    )

    print(f"Hello {name}, age {age}")


# =========================
# SYSTEM
# =========================

def system_examples():
    section("System")

    platform_name = tooly.on_platform(
        windows=lambda: "Windows",
        linux=lambda: "Linux",
        macos=lambda: "macOS",
        default=lambda: "Unknown",
    )
    print("Platform:", platform_name)


# =========================
# LOGGING
# =========================

def log_examples():
    section("Logging")

    tooly.log.set_file("example.log")
    tooly.log.info("Info message")
    tooly.log.success("Success message")
    tooly.log.warn("Warning message")
    tooly.log.error("Error message")


# =========================
# RETRY
# =========================

def retry_examples():
    section("Retry")

    @tooly.retry(attempts=3, delay=0.3)
    def fetch():
        requests.get("https://httpbin.org/status/500").raise_for_status()

    try:
        fetch()
    except requests.exceptions.HTTPError as e:
        tooly.log.error("Failed:", e)


# =========================
# PROGRESS
# =========================

def progress_examples():
    section("Progress")

    for _ in tooly.progress(range(30), label="Processing"):
        time.sleep(0.02)


# =========================
# FILES / TEMP
# =========================

def temp_examples():
    section("Temp Directory")

    with tooly.tempdir() as tmp:
        print("Temp:", tmp)
        path = os.path.join(tmp, "demo")
        tooly.run(f"mkdir {path}")


# =========================
# SCHEDULER
# =========================

def scheduler_examples():
    section("Scheduler")

    counter = {"n": 0}

    @tooly.every(seconds=1)
    def tick():
        counter["n"] += 1
        print("Tick", counter["n"])

    time.sleep(3)
    tick.stop()


# =========================
# MAIN
# =========================

def main():
    basic_examples()
    text_examples()
    diff_examples()
    input_examples()
    system_examples()
    log_examples()
    retry_examples()
    progress_examples()
    temp_examples()
    scheduler_examples()

    section("Done")


if __name__ == "__main__":
    main()
