from PIL import Image

img = Image.open(r"C:\Users\29298\Desktop\ClaudeConfig.png")
img.save("icon.ico", format="ICO", sizes=[(256, 256)])