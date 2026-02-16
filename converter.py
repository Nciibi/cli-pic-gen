import sys
import re
import time
from PIL import Image, ImageSequence, ImageEnhance

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

def apply_pixelation(image, level, target_width, mode="pixel"):
    """
    Decouples pixelation from output size.
    level 0: no change
    level 100: 10px internal resolution
    """
    if level is None or level <= 0:
        return image
        
    level = min(100, level)
    width, height = image.size
    
    if mode == "ascii":
        aspect_ratio = (height / width) / 1.6
    else:
        aspect_ratio = height / width
        
    internal_width = int(target_width * (1 - level/100) + 10 * (level/100))
    internal_width = max(5, internal_width)
    internal_height = int(internal_width * aspect_ratio)
    
    target_height = int(target_width * aspect_ratio)
    
    # Downsample
    small = image.resize((internal_width, internal_height), resample=Image.BOX)
    # Upscale back to target size
    pixelated = small.resize((target_width, target_height), resample=Image.NEAREST)
    
    return pixelated

def convert_to_ascii(image, new_width=100, charset=ASCII_CHARS, level=None):
    image = apply_pixelation(image, level, new_width, mode="ascii")
    image = resize_image(image, new_width, mode="ascii")
    image = grayify(image)
    
    ascii_str = pixels_to_ascii(image, charset)
    pixel_count = len(ascii_str)
    ascii_img = "\n".join([ascii_str[index:(index + new_width)] for index in range(0, pixel_count, new_width)])
    
    return ascii_img

def get_ansi_color(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"

def convert_to_pixel_art(image, new_width=80, level=None):
    image = apply_pixelation(image, level, new_width, mode="pixel")
    image = resize_image(image, new_width, mode="pixel")
    image = image.convert("RGB")
    width, height = image.size
    pixels = list(image.getdata())
    
    pixel_art = ""
    for i in range(height):
        for j in range(width):
            r, g, b = pixels[i * width + j]
            # Use two characters to represent a "pixel"
            pixel_art += f"{get_ansi_color(r, g, b)}██"
        pixel_art += "\x1b[0m\n"
        
    return pixel_art

def convert_to_colored_ascii(image, new_width=100, charset=ASCII_CHARS, level=None):
    image = apply_pixelation(image, level, new_width, mode="ascii")
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

def strip_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def convert_to_html(ansi_text):
    """
    Highly simplified ANSI to HTML converter.
    Handles \x1b[38;2;r;g;bm and \x1b[0m
    """
    html_out = "<!DOCTYPE html>\n<html>\n<head>\n"
    html_out += "<style>\n"
    html_out += "body { background-color: #121212; color: white; font-family: monospace; line-height: 1; letter-spacing: 0; }\n"
    html_out += "pre { font-size: 8px; white-space: pre; }\n"
    html_out +="</style>\n</head>\n<body>\n<pre>\n"
    
    # Simple regex to find color codes and reset codes
    parts = re.split(r'(\x1b\[38;2;\d+;\d+;\d+m|\x1b\[0m)', ansi_text)
    
    current_span = False
    for part in parts:
        if part.startswith('\x1b[38;2;'):
            if current_span:
                html_out += "</span>"
            # Extract r, g, b
            match = re.search(r'38;2;(\d+);(\d+);(\d+)m', part)
            if match:
                r, g, b = match.groups()
                html_out += f'<span style="color: rgb({r},{g},{b});">'
                current_span = True
        elif part == '\x1b[0m':
            if current_span:
                html_out += "</span>"
                current_span = False
        else:
            # Escape HTML characters in the text part
            escaped = part.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html_out += escaped
            
    if current_span:
        html_out += "</span>"
        
    html_out += "\n</pre>\n</body>\n</html>"
    return html_out

def save_as_pixel_jpeg(image, output_path, new_width=160, level=None):
    # If width is large (default for saving), we still want to apply pixelation level
    # target_width should be high enough to look good (e.g., 1280 or 800)
    # but for now we follow new_width which is the logical pixels.
    # Actually, let's make it fixed size 1280 for output if it's a save.
    
    display_width = 1280
    image = apply_pixelation(image, level, display_width, mode="pixel")
    
    # After pixelation at 1280, it's already "blocky". We just save it.
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    image.save(output_path, "JPEG", quality=95)
    print(f"Pixelated JPEG saved to {output_path} (High Res with Level {level})")

def save_as_animated_pixel_gif(image, output_path, new_width=160, level=None):
    display_width = 1200 # Standard wide size
    
    frames = []
    durations = []
    
    for frame in ImageSequence.Iterator(image):
        pixelated_frame = apply_pixelation(frame.convert("RGBA"), level, display_width, mode="pixel")
        frames.append(pixelated_frame.convert("P", palette=Image.ADAPTIVE))
        durations.append(frame.info.get('duration', 100))
        
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=durations,
            loop=0,
            optimize=True
        )
        print(f"Animated Pixelated GIF saved to {output_path} (High Res with Level {level})")

def get_frames_as_ansi(image, mode="pixel", new_width=80, level=None):
    """
    Returns a list of strings (one per frame) formatted with ANSI codes.
    """
    ansi_frames = []
    durations = []
    
    for frame in ImageSequence.Iterator(image):
        if mode == "pixel":
            ansi_frames.append(convert_to_pixel_art(frame, new_width, level))
        elif mode == "colored-ascii":
            ansi_frames.append(convert_to_colored_ascii(frame, new_width, charset=ASCII_CHARS, level=level))
        else: # ascii
            ansi_frames.append(convert_to_ascii(frame, new_width, charset=ASCII_CHARS, level=level))
            
        durations.append(frame.info.get('duration', 100) / 1000.0) # convert to seconds
        
    return ansi_frames, durations
