import random
import math
import time
from PIL import Image, ImageTk
import tkinter as tk
import colorsys
import numpy as np
import imageio.v2 as imageio

# Expression classes
class Variable:
    def __init__(self, name):
        self.name = name
    def eval(self, x, y, t):
        return {"x": x, "y": y, "t": t}[self.name]

class Sin:
    def __init__(self, prob):
        self.arg = buildExpression(prob**2)
    def eval(self, x, y, t):
        return math.sin(self.arg.eval(x, y, t))

class Cos:
    def __init__(self, prob):
        self.arg = buildExpression(prob**2)
    def eval(self, x, y, t):
        return math.cos(self.arg.eval(x, y, t))
    
class Times:
    def __init__(self, prob):
        self.a = buildExpression(prob**2)
        self.b = buildExpression(prob**2)
    def eval(self, x, y, t):
        return self.a.eval(x, y, t) * self.b.eval(x, y, t)

class Avg:
    def __init__(self, prob):
        self.a = buildExpression(prob**2)
        self.b = buildExpression(prob**2)
    def eval(self, x, y, t):
        return (self.a.eval(x, y, t) + self.b.eval(x, y, t)) / 2

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
            nx = (px - w / 2) / ppu
            ny = (py - h / 2) / ppu
            r = math.sqrt(nx**2 + ny**2)
            theta = math.atan2(ny, nx)
            val = expr.eval(nx + math.sin(t / 8) * 0.2, ny + math.cos(t / 10) * 0.2, t / 10)
            val += math.sin(r * 3 - t / 5) * math.cos(theta * 2)
            intensity = int((val + 1) * 127.5) % 256
            pixels[px, py] = intensity
    return img

def plotColor(expr, ppu, w, h, t):
    base = plotPattern(expr, ppu, w, h, t)
    rgb_img = Image.new("RGB", (w, h))
    pixels = rgb_img.load()
    base_pixels = base.load()

    # Expanded nature/movement-inspired themes
    themes = {
        "forest": [(34, 139, 34), (85, 107, 47), (139, 69, 19), (245, 245, 220)],
        "sea": [(0, 0, 128), (30, 144, 255), (135, 206, 250), (240, 248, 255)],
        "clouds": [(240, 248, 255), (176, 196, 222), (119, 136, 153), (70, 80, 90)],
        "fire": [(255, 69, 0), (255, 140, 0), (255, 215, 0), (139, 0, 0)],
        "sunset": [(255, 99, 71), (255, 165, 0), (255, 215, 0), (75, 0, 130)],
        "aurora": [(0, 255, 127), (0, 191, 255), (123, 104, 238), (25, 25, 112)],
        "jungle": [(0, 100, 0), (46, 139, 87), (107, 142, 35), (85, 107, 47)],
        "ocean_deep": [(0, 0, 50), (0, 105, 148), (70, 130, 180), (173, 216, 230)]
    }

    # Cycle theme every 5 seconds
    theme_names = list(themes.keys())
    theme_index = int(t // 5) % len(theme_names)
    theme_name = theme_names[theme_index]
    palette = themes[theme_name]

    for py in range(h):
        for px in range(w):
            v = base_pixels[px, py] / 255.0
            if v < 0.25:
                color = tuple(int(c1 * (v / 0.25) + c2 * (1 - v / 0.25))
                              for c1, c2 in zip(palette[0], palette[1]))
            elif v < 0.5:
                color = tuple(int(c1 * ((v - 0.25) / 0.25) + c2 * (1 - (v - 0.25) / 0.25))
                              for c1, c2 in zip(palette[1], palette[2]))
            elif v < 0.75:
                color = tuple(int(c1 * ((v - 0.5) / 0.25) + c2 * (1 - (v - 0.5) / 0.25))
                              for c1, c2 in zip(palette[2], palette[3]))
            else:
                color = tuple(int(c1 * ((v - 0.75) / 0.25) + c2 * (1 - (v - 0.75) / 0.25))
                              for c1, c2 in zip(palette[3], palette[0]))
            pixels[px, py] = color
            
    return rgb_img


def save_video(expr, ppu, w, h, duration_seconds=10, fps=30):
    print("Generating video... This may take a moment.")
    writer = imageio.get_writer('video.mp4', fps=fps, codec='libx264')  # removed pixel_format
    num_frames = duration_seconds * fps
    start_time = time.time()

    # Save first frame as image
    first_frame_img = plotColor(expr, ppu, w, h, 0)
    first_frame_img.save("nature_frame.png")

    for i in range(num_frames):
        t = (time.time() - start_time) + i / fps
        img = plotColor(expr, ppu, w, h, t)
        # Ensure correct RGB format
        img_array = np.array(img.convert("RGB"), dtype=np.uint8)
        print(img_array.shape)  # should be (144, 256, 3)
        writer.append_data(img_array)

    writer.close()

def update_image(label, root, ppu, sw, sh, tw, th):
    global expr, start_time
    t = time.time() - start_time
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
    
    # Video settings
    ppu = 80
    sw, sh = 256, 144 # 256, 256 for symmetric
    expr = buildExpression()
    save_video(expr, ppu, sw, sh, duration_seconds=5, fps=30)
    # Live animation settings
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    label = tk.Label(root)
    label.pack(fill="both", expand=True)
    tw, th = root.winfo_screenwidth(), root.winfo_screenheight()
    
    expr = buildExpression()
    start_time = time.time()
    
    root.after(0, update_image, label, root, ppu, sw, sh, tw, th)

    root.mainloop()

if __name__ == "__main__":
    main()