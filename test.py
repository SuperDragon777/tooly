import tooly
import time

colors = tooly.ColorSystem() # recommended

print(colors.info("Welcome to Tooly!")) # Color example

tooly.typewrite(colors.info("Example text"), delay=0.05) # Typewrite example

with tooly.measure("Example measure"):
    # Do something
    time.sleep(2)