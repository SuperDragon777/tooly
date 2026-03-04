import tooly
import time

colors = tooly.ColorSystem() #? recommended
wait_time = 0.5

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

tooly.userinput("Enter your name: ", validator=lambda name: name.isalpha(), error_msg="Invalid name. Try again.")
tooly.userinput("Enter your age: ", validator=lambda name: name.isdigit(), error_msg="Invalid age. Try again.")

#* Recorder example
with tooly.recorder("example_session.log"):
    print("Recorder example...")
    name = tooly.userinput("Enter your name: ", validator=lambda name: name.isalpha(), error_msg="Invalid name. Try again.")
    print(f"Hello, {name}!")