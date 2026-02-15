from PIL import Image
import sys

# Standard ASCII character set from dark to light
ASCII_CHARS = "@%#*+=-:. "

def resize_image(image, new_width=100, mode="ascii"):
    width, height = image.size
    
    # Terminal characters are typically taller than they are wide.
    # We adjust the aspect ratio to compensate for this.
    # Standard terminal character aspect ratio is ~0.5 (width/height)
    if mode == "ascii":
        aspect_ratio = height / width / 1.6  # 1.6 is a common adjustment for ASCII
    else:
        aspect_ratio = height / width
        
    new_height = int(new_width * aspect_ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

def grayify(image):
    return image.convert("L")

def pixels_to_ascii(image, charset=ASCII_CHARS):
    pixels = image.getdata()
    characters = "".join([charset[pixel * len(charset) // 256] for pixel in pixels])
    return characters

def convert_to_ascii(image, new_width=100, charset=ASCII_CHARS):
    image = resize_image(image, new_width, mode="ascii")
    image = grayify(image)
    
    ascii_str = pixels_to_ascii(image, charset)
    pixel_count = len(ascii_str)
    ascii_img = "\n".join([ascii_str[index:(index + new_width)] for index in range(0, pixel_count, new_width)])
    
    return ascii_img

def get_ansi_color(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"

def convert_to_pixel_art(image, new_width=80):
    image = resize_image(image, new_width, mode="pixel")
    image = image.convert("RGB")
    width, height = image.size
    pixels = list(image.getdata())
    
    pixel_art = ""
    for i in range(height):
        for j in range(width):
            r, g, b = pixels[i * width + j]
            # Use two spaces or a block character to represent a "pixel"
            # Two spaces often looks more square in terminals
            pixel_art += f"{get_ansi_color(r, g, b)}██"
        pixel_art += "\x1b[0m\n"
        
    return pixel_art

def convert_to_colored_ascii(image, new_width=100, charset=ASCII_CHARS):
    ascii_image = resize_image(image, new_width, mode="ascii")
    grayscale_image = grayify(ascii_image)
    rgb_image = ascii_image.convert("RGB")
    
    width, height = grayscale_image.size
    gs_pixels = list(grayscale_image.getdata())
    rgb_pixels = list(rgb_image.getdata())
    
    colored_ascii = ""
    for i in range(height):
        for j in range(width):
            idx = i * width + j
            r, g, b = rgb_pixels[idx]
            gs = gs_pixels[idx]
            char = charset[gs * len(charset) // 256]
            colored_ascii += f"{get_ansi_color(r, g, b)}{char}"
        colored_ascii += "\x1b[0m\n"
        
    return colored_ascii
