# star

A spinning ASCII figure for the terminal, with perspective, depth shading and a choice of colors, characters and spin directions. An installer adds a `star` command so you can run it from anywhere.

## Requirements

- Linux with Python 3.6 or newer
- A terminal with 256-color support (most modern terminals have it)

## Project layout

```
star/
├── main.py        # the animation
└── init/
    └── init.py    # installs the `star` command
```

## Installation

```bash
cd ~/projects/star/init
python3 init.py
```

This creates a `star` launcher in `~/.local/bin`. If that folder is not in your `PATH`, the installer prints the line to add to `~/.bashrc` or `~/.zshrc`. After adding it, open a new terminal.

Installer options:

| Option | Description |
| --- | --- |
| `--name NAME` | Command name to install (default: `star`) |
| `--dir PATH` | Directory for the launcher (default: `~/.local/bin`) |
| `--force` | Overwrite an existing file that was not installed by this script |
| `--uninstall` | Remove the installed launcher |

Examples:

```bash
python3 init.py --dir /usr/local/bin   # system-wide install, may need sudo
python3 init.py --name spin            # install as `spin` instead
python3 init.py --uninstall            # remove the command
```

## Usage

```bash
star                        # default: cyan gradient, original art, spins left to right
star -c magenta             # choose a color preset
star -s '#*+'               # build the figure from these characters
star -d up                  # spin from bottom to top
star -c green -s '@' -d all # combine options
```

Press `Ctrl+C` to exit. The terminal cursor is restored on exit.

### Options

| Option | Description |
| --- | --- |
| `-c`, `--color` | A color preset (`cyan`, `blue`, `green`, `red`, `magenta`, `yellow`, `white`), or a comma-separated list of 256-color codes from back to front, e.g. `27,51,231` |
| `-s`, `--chars` | Characters to build the figure from, cycled across the figure. Spaces are ignored. Default: the original art |
| `-d`, `--direction` | `right` (left to right, default), `left`, `up` (bottom to top), `down` (top to bottom), or `all` (tumble in every direction) |

Run `star -h` to see the same list in the terminal.

## Uninstall

```bash
cd ~/projects/star/init
python3 init.py --uninstall
```

The uninstaller only removes files it created. It leaves other commands alone.

## Running without installing

```bash
python3 main.py -c blue -d down
```

## How it works

`init.py` writes a small shell script to the chosen directory. The script runs `main.py` with the same Python interpreter used for installation and forwards all arguments, so `star -c magenta` runs `main.py -c magenta`.

If you move the `star` folder, run `init.py` again from its new location. The launcher stores the absolute path to `main.py`.

## Troubleshooting

- **`star: command not found`**: `~/.local/bin` is not in your `PATH`. Add `export PATH="$HOME/.local/bin:$PATH"` to your shell config and open a new terminal. You can also run the launcher directly with `~/.local/bin/star`.
- **`main.py not found`**: the launcher points to a missing file. Make sure `main.py` is in the parent folder of `init/`, then run the installer again.
- **Colors look wrong or dim**: try a brighter preset, such as `-c white` or `-c cyan`, or use a terminal with 256-color support.
