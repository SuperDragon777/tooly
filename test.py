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