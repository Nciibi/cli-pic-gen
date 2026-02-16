import argparse
from PIL import Image
import os
import sys
import time
from converter import (
    convert_to_ascii, 
    convert_to_pixel_art, 
    convert_to_colored_ascii, 
    ASCII_CHARS,
    strip_ansi_codes,
    convert_to_html,
    save_as_pixel_jpeg,
    save_as_animated_pixel_gif,
    get_frames_as_ansi
)

def print_banner():
    b = "\x1b[1;36m" # cyan border
    c = "\x1b[1;33m" # yellow content
    m = "\x1b[1;35m" # magenta author
    g = "\x1b[1;32m" # green headers
    r = "\x1b[0m"    # reset
    
    width = 76 # Internal content width
    
    def box_line(text, color=r, style='left'):
        if style == 'center':
            content = text.center(width)
        else:
            content = text.ljust(width)
        return f"{b}┃{r} {color}{content}{r} {b}┃{r}"

    art = [
        "██████╗ ██╗     ██╗    ██████╗ ██╗ ██████╗     ██████╗ ███████╗███╗   ██╗",
        "██╔════╝ ██║     ██║    ██╔══██╗██║██╔════╝    ██╔════╝ ██╔════╝████╗  ██║",
        "██║     ██║     ██║    ██████╔╝██║██║         ██║  ███╗█████╗  ██╔██╗ ██║",
        "██║     ██║     ██║    ██╔═══╝ ██║██║         ██║   ██║██╔══╝  ██║╚██╗██║",
        "██╔██████╗███████╗██║  ██║     ██║╚██████╗    ╚██████╔╝███████╗██║ ╚████║",
        "╚═════╝╚══════╝╚═╝    ╚═╝     ╚═╝ ╚═════╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝"
    ]
    
    print(f"{b}┏{'━' * (width + 2)}┓{r}")
    print(box_line(""))
    for line in art:
        print(box_line(line.center(width), c))
    print(box_line(""))
    print(box_line("--- Created by Tyrel ---", m, 'center'))
    print(box_line(""))
    print(f"{b}┣{'━' * (width + 2)}┫{r}")
    print(box_line(""))
    print(box_line("How to use:", g))
    print(box_line("  python3 main.py <path_to_image> [options]"))
    print(box_line(""))
    print(box_line("Main Commands:", g))
    print(box_line("  --mode [ascii|pixel|...]           Choose output style"))
    print(box_line("  --level <0-100>                    Pixelation resolution detail"))
    print(box_line("  --output <filename>                Save to file (.jpg, .gif, .html, .txt)"))
    print(box_line(""))
    print(box_line("Examples:", g))
    print(box_line("  python3 main.py headshot.png --mode pixel"))
    print(box_line("  python3 main.py art.png --mode pixel --output result.jpg"))
    print(box_line(""))
    print(f"{b}┗{'━' * (width + 2)}┛{r}")

def main():
    if len(sys.argv) == 1:
        print_banner()
        return

    parser = argparse.ArgumentParser(
        description="Convert images to ASCII or Pixel Art for the CLI.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Add branding to help description
    parser.description = f"\x1b[1;33mCLI-PIC-GEN by Tyrel\x1b[0m\n\nConvert images to ASCII or Pixel Art for the CLI."
    parser.add_argument("input", help="Path to the input image file")
    parser.add_argument("--mode", choices=["ascii", "pixel", "colored-ascii"], default="ascii", help="Output mode (default: ascii)")
    parser.add_argument("--width", type=int, help="Override output width")
    parser.add_argument("--level", type=int, help="Pixelation level (0-100). Higher = More pixelated.")
    parser.add_argument("--charset", default=ASCII_CHARS, help="Custom charset for ASCII mode")
    parser.add_argument("--output", help="Optional path to save the output to a file")

    args = parser.parse_args()
    
    # Check if width was explicitly provided by checking sys.argv
    width_provided = "--width" in sys.argv
    level_provided = "--level" in sys.argv

    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)

    try:
        image = Image.open(args.input)
    except Exception as e:
        print(f"Error: Could not open image. {e}")
        sys.exit(1)

    # Detect terminal size for better capping
    try:
        ts = os.get_terminal_size()
        term_width = ts.columns
        term_height = ts.lines
    except:
        term_width = 80
        term_height = 24

    # Handle Pixelation Level logic
    level = args.level if level_provided else None
    if level is not None:
        level = max(0, min(100, level))
    else:
        level = 30 # Default

    is_gif = getattr(image, "is_animated", False) and image.format == 'GIF'
    
    # Calculate Physical Output Size (How many characters on screen)
    if not args.output:
        # Standard output logic
        h_margin = 8
        v_margin = 12
        
        # 1. Height Constraint (Most critical for vertical looping)
        width, height = image.size
        img_aspect = height / width
        
        if args.mode == "pixel":
            v_max = int((term_height - v_margin) / img_aspect)
        else:
            v_max = int((term_height - v_margin) / (img_aspect / 1.6))
            
        # 2. Width Constraint
        h_max = (term_width - h_margin) // 2 if args.mode == "pixel" else (term_width - h_margin)
        h_max = min(h_max, 100)

        args.width = min(h_max, v_max)
        args.width = max(10, args.width)
    else:
        # For saves, default to a high-res logical width if level is 0
        if not width_provided:
            args.width = 160 
        width_provided = True

    output = ""
    if is_gif:
        print(f"\x1b[1;33mPreparing {getattr(image, 'n_frames', 1)} frames (Level {level})...\x1b[0m")
        ansi_frames, durations = get_frames_as_ansi(image, args.mode, args.width, level=level)
        
        # Initial screen clear
        sys.stdout.write("\033[2J\x1b[?25l")
        sys.stdout.flush()
        
        try:
            while True:
                for i, frame in enumerate(ansi_frames):
                    # Standard: Home, write, then clear to end of screen (no flicker)
                    full_payload = f"\033[H{frame}\n\x1b[1;33m(Ctrl+C to stop) Frame {i+1}/{len(ansi_frames)}\x1b[0m\x1b[J"
                    sys.stdout.write(full_payload)
                    sys.stdout.flush()
                    time.sleep(durations[i])
        except KeyboardInterrupt:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            print("\x1b[?25h\x1b[1;32mPlayback stopped.\x1b[0m")
            time.sleep(0.3) 
        finally:
            sys.stdout.write("\x1b[?25h")
            sys.stdout.flush()
        
        output = ansi_frames[0]
    else:
        if args.mode == "ascii":
            output = convert_to_ascii(image, args.width, args.charset, level=level)
        elif args.mode == "pixel":
            output = convert_to_pixel_art(image, args.width, level=level)
        elif args.mode == "colored-ascii":
            output = convert_to_colored_ascii(image, args.width, args.charset, level=level)
        
        if args.banner:
            output = center_ansi(output, term_width)

    if args.output:
        save_output(output, args.output, image, args.width, width_provided, level=level)
    else:
        if not is_gif:
            print(output)
            
        try:
            print("\x1b[1;33m" + "="*40 + "\x1b[0m")
            save_choice = input("Would you like to save this output to a file? (y/n): ").lower().strip()
            if save_choice == 'y':
                filename = input("Enter filename (e.g., output.txt, output.html, output.jpg, output.gif): ").strip()
                if filename:
                    save_output(output, filename, image, args.width, width_provided, level=level)
                else:
                    print("Save cancelled: No filename provided.")
        except EOFError:
            pass
        except KeyboardInterrupt:
            print("\n\x1b[1;31mProgram exited.\x1b[0m")
            sys.exit(0)

def save_output(output, filename, original_image, width, width_provided=False, level=None):
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext in [".jpg", ".jpeg"]:
            save_as_pixel_jpeg(original_image, filename, level=level)
        elif ext == ".gif":
            save_as_animated_pixel_gif(original_image, filename, level=level)
        elif ext == ".html":
            html_content = convert_to_html(output)
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Output saved to {filename} (HTML format)")
        else:
            # Default to text, but strip ANSI if it's a .txt file
            if ext == ".txt":
                output = strip_ansi_codes(output)
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")

if __name__ == "__main__":
    main()
