import tooly
import time
from datetime import datetime
import requests

colors = tooly.ColorSystem() #? recommended
wait_time = 2
skip_userinput = False

print(colors.info("Welcome to Tooly!")) #* Color example

tooly.typewrite(colors.info("Example text"), delay=0.05) #* Typewrite example

with tooly.measure("Example measure"):
    #? Do something
    time.sleep(wait_time)
    
with tooly.spinner("Example spinner", done_msg="Exaple spinner done"):
    #? Do something
    time.sleep(wait_time)

#* Highlight example
text = "Some interesting text with keywords"
print(colors.highlight(text, ["keywords", "text"], "yellow")) #? text, keywords, color

#* Indent example
#? You can use indent for file tree for example
print(colors.indent("Example folder/", 0))
print(colors.indent("Example python file", 1))
print(colors.indent("Example readme file", 1))
print(colors.indent("Example subfolder/", 1))
print(colors.indent("howtodoerrors.txt", 2))
print(colors.indent("Example file", 0))

#* Diff feature examples

# word mode sql example
sql_before = "SELECT id, name FROM users WHERE active = 1"
sql_after  = "SELECT id, email FROM users WHERE active = 1 LIMIT 100"
print(tooly.diff_highlight(sql_before, sql_after, tooly.DiffMode.WORD))

# char mode url example
url_before = "https://api.example.com/v1/users/42"
url_after  = "https://api.example.com/v2/users/42/profile"
print(tooly.diff_highlight(url_before, url_after, tooly.DiffMode.CHAR))

# line mode config example
cfg_before = """
host = localhost
port = 5432
debug = true
workers = 2
"""
cfg_after = """
host = example.com
port = 5432
debug = false
workers = 8
timeout = 30
"""
print(tooly.diff_highlight(cfg_before, cfg_after, tooly.DiffMode.LINE, context_lines=1))

#* Validator example
"""
Methods:
    str.isalpha() - only letters
    str.isdigit() - only dights
    str.isnumeric() - only dights (including unicode)
    str.isalnum() - digits and letters
    str.islower() - only lower case
    str.isupper() - only upper case
    str.istitle() - every word starts with a capital
    str.startswith(prefix) - starts with a prefix
    str.endswith(suffix) - ends with a suffix
    str.isprintable() - only printable characters
    str.isascii() -  only ASCII characters
"""
if not skip_userinput:
    tooly.userinput("Enter your name: ", validator=lambda name: name.isalpha(), error_msg="Invalid name. Try again.")
    tooly.userinput("Enter your age: ", validator=lambda name: name.isdigit(), error_msg="Invalid age. Try again.")

#* Recorder example
with tooly.recorder("example_session.log"):
    print("Recorder example...")
    name = tooly.userinput("Enter your name: ", validator=lambda name: name.isalpha(), error_msg="Invalid name. Try again.")
    print(f"Hello, {name}!")

#* Clear console example
print("Console will be cleared")
input("Press Enter to continue...")
tooly.cls()

#* On platform example
result = tooly.on_platform(
    windows=lambda: "Windows",
    linux=lambda: "Linux",
    macos=lambda: "macOS",
    android=lambda: "Android",
    ios=lambda: "iOS",
    default=lambda: "Unknown"
)
print(f"Current platform: {result}")
input("Press Enter to continue...")

#* Menu example
choice = tooly.menu(
    ["Start server", "Stop server", "Exit"],
    title="Example menu"
)
print(f"You chose: {choice}")

#* Confirm example
if tooly.confirm("Are you sure?"):
    print("Confirmed")
else:
    print("Canceled")
input("Press Enter to continue...")

#* Watch example
def show_time():
    return f"Текущее время: {datetime.now().strftime("%H:%M:%S")}"

tooly.watch(show_time, interval=1)

#* Notify example
tooly.notify("Example", "Example text")

#* Log example
tooly.log.set_file("example.log")
tooly.log.success("Example success log message")
tooly.log.debug("Example debug log message")
tooly.log.error("Example error log message")
tooly.log.warn("Example warning log message")
tooly.log.info("Example info log message")

#* Retry example
@tooly.retry(attempts=4, delay=0.5, backoff=2.0)
def fetch():
    requests.get("https://httpbin.org/status/500").raise_for_status() #? This will fail with 500 status code, triggering retries

try:
    fetch()
except requests.exceptions.HTTPError as e:
    tooly.log.error("Giving up:", e)

#* Countdown example
tooly.countdown(5) #? very simple to use, don't you?

#* Sparkline example
data = [1, 5, 3, 8, 2]
print(tooly.sparkline(data))