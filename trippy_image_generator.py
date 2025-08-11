import random
import math
from PIL import Image, ImageTk
import tkinter as tk
import time
# for trippy party nights
# since each RGB channel is generated from a different expression, with time-offset and different mathematical operations
# the images are rendered in a "flowy" manner, creating a trippy effect
# the expressions are evaluated to produce intensity values for each pixel
# the images are then rendered in RGB format
# 1. add better variations and expressions? It looks too trippy. 
# 2 want symmetry and better coloring


class Variable:
    def __init__(self, name): self.name = name
    def eval(self, x, y): return x if self.name == "x" else y
    def __str__(self): return self.name

class SinPi:
    def __init__(self, prob): self.arg = buildExpression(prob**2)
    def eval(self, x, y): return math.sin(math.pi * self.arg.eval(x, y))
    def __str__(self): return f"sin(pi*{self.arg})"

class CosPi:
    def __init__(self, prob): self.arg = buildExpression(prob**2)
    def eval(self, x, y): return math.cos(math.pi * self.arg.eval(x, y))
    def __str__(self): return f"cos(pi*{self.arg})"

class TanPi:
    def __init__(self, prob): self.arg = buildExpression(prob**2)
    def eval(self, x, y):
        try:
            return math.tan(math.pi * self.arg.eval(x, y)) / 5
        except:
            return 0
    def __str__(self): return f"tan(pi*{self.arg})"

class Times:
    def __init__(self, prob):
        self.lhs = buildExpression(prob**2)
        self.rhs = buildExpression(prob**2)
    def eval(self, x, y): return self.lhs.eval(x, y) * self.rhs.eval(x, y)
    def __str__(self): return f"({self.lhs}*{self.rhs})"

class Avg:
    def __init__(self, prob):
        self.a = buildExpression(prob**2)
        self.b = buildExpression(prob**2)
    def eval(self, x, y): return 0.5 * (self.a.eval(x, y) + self.b.eval(x, y))
    def __str__(self): return f"avg({self.a},{self.b})"

class Abs:
    def __init__(self, prob): self.arg = buildExpression(prob**2)
    def eval(self, x, y): return abs(self.arg.eval(x, y))
    def __str__(self): return f"abs({self.arg})"

class Mix:
    """Linear blend between two expressions controlled by a third """
    def __init__(self, prob):
        self.a = buildExpression(prob**2)
        self.b = buildExpression(prob**2)
        self.t = buildExpression(prob**2)
    def eval(self, x, y):
        t = (self.t.eval(x, y) + 1) / 2
        return self.a.eval(x, y) * (1 - t) + self.b.eval(x, y) * t
    def __str__(self): return f"mix({self.a},{self.b},{self.t})"
# this function builds a random mathematical expression based on the given probability
# it uses a mix of variables and functions to create a complex expression
def buildExpression(prob=0.99):
    primitives = [Variable("x"), Variable("y")]
    functions = [SinPi, CosPi, TanPi, Times, Avg, Abs, Mix]
    if random.random() < prob:
        return random.choice(functions)(prob)
    else:
        return random.choice(primitives)

# this basically renders the mathematical expression to an image
def plotIntensity(exp, ppu, w, h, t=0):
    canvas = Image.new("L", (w, h))
    for py in range(h):
        for px in range(w):
            # add time-based movement
            x = (px - w/2) / ppu + math.sin(t/10) * 0.3
            y = (py - h/2) / ppu + math.cos(t/15) * 0.3
            z = exp.eval(x, y)
            intensity = int((z + 1) * 127.5) % 256
            canvas.putpixel((px, py), intensity)
    return canvas
# this just plots the RGB channels of the image
# it uses the same expression for each channel but with different time offsets
def plotColor(r, g, b, ppu, w, h, t=0):
    return Image.merge("RGB", (
        plotIntensity(r, ppu, w, h, t),
        plotIntensity(g, ppu, w, h, t + 1),
        plotIntensity(b, ppu, w, h, t + 2)
    ))

def update_image(label, root, ppu, sw, sh, tw, th, elapsed):
    global red, green, blue, image, base_time

    current_time = time.time()
    elapsed = current_time - base_time

    # smoothly regenerate expressions every ~15s
    if elapsed > 15:
        base_time = current_time
        elapsed = 0
        red = buildExpression()
        green = buildExpression()
        blue = buildExpression()

    # render with time-based movement
    img = plotColor(red, green, blue, ppu, sw, sh, elapsed * 2)
    img = img.resize((tw, th), Image.LANCZOS)
    
    tk_img = ImageTk.PhotoImage(img)
    label.configure(image=tk_img)
    label.image = tk_img

    root.after(30, update_image, label, root, ppu, sw, sh, tw, th, elapsed)


def main():
    global red, green, blue, image, base_time

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    label = tk.Label(root)
    label.pack(fill="both", expand=True)
    tw, th = root.winfo_screenwidth(), root.winfo_screenheight()

    ppu = 60  # pixels per unit, it's kind of slow 
    sw, sh = 256, 144  # render resolution

    # initialize
    red, green, blue = buildExpression(), buildExpression(), buildExpression()
    base_time = time.time()

    root.after(0, update_image, label, root, ppu, sw, sh, tw, th, 0)
    # save a random image to start
    image = plotColor(red, green, blue, ppu, sw, sh)
    # save the first image as trippy_frame.png
    image.save("trippy_frame.png")
    root.mainloop()

if __name__ == "__main__":
    main()