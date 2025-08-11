import random, math, time
from PIL import Image, ImageTk
import tkinter as tk
import colorsys

class Variable:
    def __init__(self, name): self.name = name
    def eval(self, x, y, t): return {"x": x, "y": y, "t": t}[self.name]

class Sin:
    def __init__(self, prob): self.arg = buildExpression(prob**2)
    def eval(self, x, y, t): return math.sin(self.arg.eval(x, y, t))
    
class Cos:
    def __init__(self, prob): self.arg = buildExpression(prob**2)
    def eval(self, x, y, t): return math.cos(self.arg.eval(x, y, t))

class Times:
    def __init__(self, prob):
        self.a = buildExpression(prob**2)
        self.b = buildExpression(prob**2)
    def eval(self, x, y, t): return self.a.eval(x, y, t) * self.b.eval(x, y, t)

class Avg:
    def __init__(self, prob):
        self.a = buildExpression(prob**2)
        self.b = buildExpression(prob**2)
    def eval(self, x, y, t): return (self.a.eval(x, y, t) + self.b.eval(x, y, t)) / 2

def buildExpression(prob=0.95):
    primitives = [Variable("x"), Variable("y"), Variable("t")]
    funcs = [Sin, Cos, Times, Avg]
    if random.random() < prob:
        return random.choice(funcs)(prob)
    else:
        return random.choice(primitives)

def plotPattern(expr, ppu, w, h, t):
    img = Image.new("L", (w, h))
    pixels = img.load()
    for py in range(h):
        for px in range(w):
            # convert to centered coords
            nx = (px - w/2) / ppu
            ny = (py - h/2) / ppu

            # symmetry: polar coords
            r = math.sqrt(nx**2 + ny**2)
            theta = math.atan2(ny, nx)

            # feed both cartesian & polar into expression for variety
            val = expr.eval(nx + math.sin(t/8)*0.2, ny + math.cos(t/10)*0.2, t/10)
            val += math.sin(r*3 - t/5) * math.cos(theta*2)

            # normalize to [0,255]
            intensity = int((val + 1) * 127.5) % 256
            pixels[px, py] = intensity
    return img

def plotColor(expr, ppu, w, h, t):
    base = plotPattern(expr, ppu, w, h, t)

    # base image as value for hue shift
    rgb_img = Image.new("RGB", (w, h))
    pixels = rgb_img.load()
    base_pixels = base.load()

    for py in range(h):
        for px in range(w):
            v = base_pixels[px, py] / 255.0
            hue = (v + t/20) % 1.0  # drifting hue
            sat = 0.6 + 0.4 * math.sin(t/15)  # gently pulsating saturation
            r, g, b = colorsys.hsv_to_rgb(hue, sat, 0.9)
            pixels[px, py] = (int(r*255), int(g*255), int(b*255))
    return rgb_img

def update_image(label, root, ppu, sw, sh, tw, th):
    global expr, start_time
    t = time.time() - start_time

    # regenerate expression every ~25s for variety
    if int(t) % 10 == 0 and random.random() < 0.02:
        expr = buildExpression()

    img = plotColor(expr, ppu, sw, sh, t)
    img = img.resize((tw, th), Image.LANCZOS)

    tk_img = ImageTk.PhotoImage(img)
    label.configure(image=tk_img)
    label.image = tk_img

    root.after(30, update_image, label, root, ppu, sw, sh, tw, th)


def main():
    global expr, start_time
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    label = tk.Label(root)
    label.pack(fill="both", expand=True)
    tw, th = root.winfo_screenwidth(), root.winfo_screenheight()

    ppu = 80     # smoother geometry
    sw, sh = 256, 256  # square render for symmetry

    expr = buildExpression()
    start_time = time.time()

    root.after(0, update_image, label, root, ppu, sw, sh, tw, th)
    # save a random image to start
    image = plotColor(expr, ppu, sw, sh, 0)
    image.save("symmetric_trippy_frame.png")
    root.mainloop()

if __name__ == "__main__":
    main()