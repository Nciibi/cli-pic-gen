# 🖼️ CLI-PIC-GEN

**A powerful, lightweight CLI tool to convert images and GIFs into stunning ASCII Art and Pixel Art.**

CLI-PIC-GEN allows you to transform standard images into terminal-friendly masterpieces. Whether you want a high-resolution pixelated GIF as your terminal background or a classic ASCII headshot, this tool has you covered.

---

## ✨ Features

- **Standard ASCII**: Classic light-to-dark character conversion.
- **Pixel Art Mode**: Uses ANSI colored blocks for a vibrant, retro aesthetic.
- **Colored ASCII**: Combines character density with true-color output.
- **GIF Support**: Full support for animated GIFs, including playback and multi-frame export.
- **Pixelation Granularity**: Decoupled resolution control (Level 0-100) to adjust detail without changing physical size.
- **Cross-Format Export**: Save your results as `.txt`, `.html`, `.jpg`, or even animated `.gif` pixel art.
- **Terminal Detection**: Automatically fits output to your terminal width and height.

---

## 🚀 Installation

### Prerequisites
- Python 3.x
- Pillow (PIL)

```bash
# Clone the repository
git clone https://github.com/your-username/cli-pic-gen.git
cd cli-pic-gen

# Install dependencies
pip install Pillow
```

---

## 🛠️ Usage

Run the tool by passing an image path and your desired options:

```bash
python3 main.py <path_to_image> [options]
```

### Basic Options
- `--mode [ascii|pixel|colored-ascii]`: Choose your output style (Default: `ascii`).
- `--level <0-100>`: Adjust the pixelation detail. `0` is highest detail, `100` is very blocky.
- `--width <number>`: Manually override the output width.
- `--output <filename>`: Save result to a file (Supports `.txt`, `.html`, `.jpg`, `.gif`).

### Examples

**Convert an image to Pixel Art:**
```bash
python3 main.py image.png --mode pixel
```

**Save a high-resolution Pixelated GIF:**
```bash
python3 main.py animation.gif --mode pixel --level 0 --output result.gif
```

**Generate a colored ASCII HTML page:**
```bash
python3 main.py headshot.jpg --mode colored-ascii --output headshot.html
```

---

## 🎮 Development

Built with ❤️ by Nciibi using Python and the Pillow library. 

Feel free to fork, submit PRs, or report issues!
