import argparse
from PIL import Image
import os
import sys
from converter import convert_to_ascii, convert_to_pixel_art, convert_to_colored_ascii, ASCII_CHARS

def main():
    parser = argparse.ArgumentParser(description="Convert images to ASCII or Pixel Art for the CLI.")
    parser.add_argument("input", help="Path to the input image file")
    parser.add_argument("--mode", choices=["ascii", "pixel", "colored-ascii"], default="ascii", help="Output mode (default: ascii)")
    parser.add_argument("--width", type=int, default=80, help="Output width in characters (default: 80)")
    parser.add_argument("--charset", default=ASCII_CHARS, help="Custom charset for ASCII mode")
    parser.add_argument("--output", help="Optional path to save the output to a file")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File '{args.input}' not found.")
        sys.exit(1)

    try:
        image = Image.open(args.input)
    except Exception as e:
        print(f"Error: Could not open image. {e}")
        sys.exit(1)

    if args.mode == "ascii":
        output = convert_to_ascii(image, args.width, args.charset)
    elif args.mode == "pixel":
        output = convert_to_pixel_art(image, args.width)
    elif args.mode == "colored-ascii":
        output = convert_to_colored_ascii(image, args.width, args.charset)

    if args.output:
        with open(args.output, "w") as f:
            # Strip ANSI codes if saving to file unless it's a specific requirement
            # For now, we save raw output
            f.write(output)
            print(f"Output saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
