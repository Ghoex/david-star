# ⭐ star

A spinning ASCII star for your terminal. You can change its colors, the characters it's made of, and the way it spins. The installer also adds a `star` command, so you can run it from anywhere.

Русская инструкция: [INSTRUCTION_RU.md](INSTRUCTION_RU.md)

## What you need

- Linux and Python 3.6 or newer
- A terminal with 256-color support (most modern ones have it)

## Get the code

```bash
git clone https://github.com/Ghoex/david-star.git
cd david-star
```

Or just download the ZIP from GitHub and unpack it wherever you like.

The folder layout looks like this:

```
david-star/
├── main.py      # the animation
└── init/
    └── init.py  # installs the `star` command
```

`main.py` has to stay one level above `init/`. Otherwise, the installer won't find it.

## Install

```bash
cd david-star/init
python3 init.py
```

That's it. The `star` command ends up in `~/.local/bin`.

If the installer says `~/.local/bin` isn't in your `PATH`, run this once and then open a new terminal (or restart your computer):

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

Using zsh? Use `~/.zshrc` instead of `~/.bashrc`.

## Run it

```bash
star
```

Press `Ctrl+C` to stop.

Want to change how it looks? Add options:

```bash
star -c magenta               # different color
star -s '#*+'                 # build the star from these characters
star -d up                    # spin from bottom to top
star -c green -s '@' -d all   # combine options
```

### Options

| Option | What it does | Values |
| --- | --- | --- |
| `-c`, `--color` | Sets the color | `cyan` (default), `blue`, `green`, `red`, `magenta`, `yellow`, `white`, or your own 256-color codes like `27,51,231` (from back to front) |
| `-s`, `--chars` | Characters the star is drawn with | Any characters, e.g. `'#*+'`. Default: the original art |
| `-d`, `--direction` | Which way it spins | `right` (default), `left`, `up`, `down`, `all` |

Not sure what's available? Run `star -h`.

## Don't want to install it?

You can run it straight from the project folder:

```bash
cd david-star
python3 main.py -c blue -d down
```

## Uninstall

```bash
cd david-star/init
python3 init.py --uninstall
```

It only removes the `star` file it created. Nothing else gets touched.

## Installer options

The installer also has a few options of its own:

| Option | What it does |
| --- | --- |
| `--name NAME` | Install the command under a different name (default: `star`) |
| `--dir PATH` | Put the command in a different folder (default: `~/.local/bin`) |
| `--force` | Overwrite an existing file that the installer didn't create |
| `--uninstall` | Remove the command |

For example, `python3 init.py --name spin` gives you a `spin` command instead.

## Something's not working?

- **`star: command not found`**: your `PATH` doesn't include `~/.local/bin` yet. Add the line from the install section, then open a new terminal. You can also run `~/.local/bin/star` directly.
- **`main.py not found`**: `main.py` isn't one level above `init/`. Move it there and run the installer again.
- **Colors look dim**: try `-c white`, or switch to a terminal that supports 256 colors.
- **Moved the folder?** Run `python3 init.py` again from its new location.
