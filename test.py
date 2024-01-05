# for trippy party nights

# incomplete code
# 1. add better variations
# 2. add different expressions
# 3. make it "flowy" and faster between sequence of images

import random
import math
from PIL import Image, ImageTk
import tkinter as tk
import time

class Variable:
    def __init__(self, name):
        self.name = name

    def eval(self, x, y):
        return x if self.name == "x" else y

    def __str__(self):
        return self.name

class SinPi:
    def __init__(self, prob):
        self.arg = buildExpression(prob * prob)

    def eval(self, x, y):
        return math.sin(math.pi * self.arg.eval(x, y))

    def __str__(self):
        return f"sin(pi*{self.arg})"

class CosPi:
    def __init__(self, prob):
        self.arg = buildExpression(prob * prob)

    def eval(self, x, y):
        return math.cos(math.pi * self.arg.eval(x, y))

    def __str__(self):
        return f"cos(pi*{self.arg})"

class Times:
    def __init__(self, prob):
        self.lhs = buildExpression(prob * prob)
        self.rhs = buildExpression(prob * prob)

    def eval(self, x, y):
        return self.lhs.eval(x, y) * self.rhs.eval(x, y)

    def __str__(self):
        return f"{self.lhs}*{self.rhs}"

# convert the mathematical expression to an image RGB within the range [0, 255]
def plotIntensity(exp, pixelsPerUnit, screen_width, screen_height):
    canvas = Image.new("L", (screen_width, screen_height))
    for py in range(screen_height):
        for px in range(screen_width):
            x = (px - pixelsPerUnit) / pixelsPerUnit
            y = -(py - pixelsPerUnit) / pixelsPerUnit
            z = exp.eval(x, y)
            intensity = int(z * 127.5 + 127.5)
            canvas.putpixel((px, py), intensity)
    return canvas

# merge the RGB planes into a single color image
def plotColor(red, green, blue, pixelsPerUnit, screen_width, screen_height):
    red_plane = plotIntensity(red, pixelsPerUnit, screen_width, screen_height)
    green_plane = plotIntensity(green, pixelsPerUnit, screen_width, screen_height)
    blue_plane = plotIntensity(blue, pixelsPerUnit, screen_width, screen_height)
    return Image.merge("RGB", (red_plane, green_plane, blue_plane))

# builds the mathematical expression for the RGB image
def buildExpression(prob=0.99):
    if random.random() < prob:
        return random.choice([SinPi, CosPi, Times])(prob)
    else:
        return random.choice([Variable("x"), Variable("y")])

def introduce_variations(image, time):
    # parameters for the wave-like variation
    # random frequency and amplitude
    random.seed(time)
    frequency = random.randint(1, 20)
    amplitude = random.randint(1, 100)
    pixels = image.load()
    width, height = image.size

    # apply a wave-like variation to the entire image
    image_variation = Image.new("RGB", (width, height))
    pixels_variation = image_variation.load()

    for py in range(height):
        for px in range(width):
            # get the original RGB values
            r, g, b = pixels[px, py]

            # apply a wave-like variation to each channel
            r_variation = int(amplitude * math.sin(2 * math.pi * frequency * (time / 3)*r))
            g_variation = int(amplitude * math.sin(2 * math.pi * frequency * (time / 3 + 1)*g))
            b_variation = int(amplitude * math.sin(2 * math.pi * frequency * (time / 3 + 2)*b))

            # apply the variations to the original values
            r_new = max(0, min(255, r_variation))
            g_new = max(0, min(255, g_variation))
            b_new = max(0, min(255, b_variation))

            # if variation is 0 or 255, then the color is not changed
            if r_new == 0 or r_new == 255:
                r_new = r
            if g_new == 0 or g_new == 255:
                g_new = g
            if b_new == 0 or b_new == 255:
                b_new = b

            # Update the pixel in the new image with the new RGB values
            pixels_variation[px, py] = (r_new, g_new, b_new)

    return image_variation

def update_image(label, root, pixelsPerUnit, screen_width, screen_height,true_width, true_height, elapsed_time):
    global red, green, blue, image
    # check if 10 seconds have passed
    current_time = time.time()
    if 'last_update_time' not in globals():
        globals()['last_update_time'] = current_time
        elapsed_time = 0
    if current_time - globals()['last_update_time'] >= 10 or image is None:
        print(current_time)
        print(globals()['last_update_time'])
        # reset the timer
        globals()['last_update_time'] = current_time
        elapsed_time = 0
        # update the image every 10 seconds
        red = buildExpression()
        green = buildExpression()
        blue = buildExpression()
        # plot and display the updated image
        image = plotColor(red, green, blue, pixelsPerUnit, screen_width, screen_height)
        image = image.resize((true_width, true_height), Image.ANTIALIAS)
        tk_image = ImageTk.PhotoImage(image)

        label.configure(image=tk_image)
        label.image = tk_image
        # set the timer for introducing variations
        root.after(50, update_image, label, root, pixelsPerUnit, screen_width, screen_height, true_width, true_height, 0)
    else:
        print(current_time - globals()['last_update_time'])
        # add the variations to the image
        image = introduce_variations(image, elapsed_time)
        image = image.resize((true_width, true_height), Image.ANTIALIAS)
        # plot and display the current image with variations
        tk_image = ImageTk.PhotoImage(image)
        label.configure(image=tk_image)
        label.image = tk_image
        # continue updating the image every 50 milliseconds
        root.after(50, update_image, label, root, pixelsPerUnit, screen_width, screen_height, true_width, true_height, elapsed_time + 0.1)
def main():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    label = tk.Label(root)
    label.pack(fill="both", expand=True)
    true_width = root.winfo_screenwidth()
    true_height = root.winfo_screenheight()
    
    pixelsPerUnit = 50
    screen_width = 256
    screen_height = 144

    # initialize expressions
    global red, green, blue, image
    red = buildExpression()
    green = buildExpression()
    blue = buildExpression()
    image = plotColor(red, green, blue, pixelsPerUnit, screen_width, screen_height)
    # Scale the image to fill the entire screen
    image = image.resize((true_width, true_height), Image.ANTIALIAS)
    root.after(0, update_image, label, root, pixelsPerUnit, screen_width, screen_height, true_width, true_height, 0)  # Initial call to start the update loop
    root.mainloop()

if __name__ == "__main__":
    main()