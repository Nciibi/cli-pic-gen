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
        try:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Output saved to {args.output}")
        except Exception as e:
            print(f"Error saving to {args.output}: {e}")
    else:
        print(output)
        try:
            save_choice = input("\nWould you like to save this output to a file? (y/n): ").lower().strip()
            if save_choice == 'y':
                filename = input("Enter filename (e.g., output.txt): ").strip()
                if filename:
                    with open(filename, "w") as f:
                        f.write(output)
                    print(f"Output saved to {filename}")
                else:
                    print("Save cancelled: No filename provided.")
        except EOFError:
            pass
        except KeyboardInterrupt:
            print("\nSave cancelled.")
            sys.exit(0)


if __name__ == "__main__":
    main()
