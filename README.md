# MIDI Text-to-Music Generator

This project is a Python-based tool that generates MIDI files from an expressive text file of musical notes, with support for multiple tracks, instruments, and various music-related commands.

## Features
- Generate MIDI files from a text-based note representation.
- Support for multiple instruments, percussion, channels, and looping.
- Integration with **click** for command-line interaction.
- Uses **pygame** for MIDI playback.

## Requirements
- Python 3.7+
- `click` (for command-line interaction)
- `yaml` (to load instrument configuration)
- `mido` (to handle MIDI file creation)
- `pygame` (to play MIDI files)

## Installation

### Preinstall Instructions for macOS (using Homebrew and Pyenv)

#### Step 1: Install **Homebrew** (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install pyenv and required dependencies

Use Homebrew to install pyenv and dependencies:

```bash
brew update
brew install pyenv
brew install pyenv-virtualenv
brew install portaudio
brew install fluidsynth
```

#### Step 3: Configure pyenv

Add the following lines to your shell profile (e.g., ~/.bashrc, ~/.zshrc, etc.) to initialize pyenv automatically:

```bash
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
```

Restart your terminal or run:

```bash
source ~/.zshrc  # Or source your profile file accordingly
```

#### Step 4: Install Python with pyenv

Install the required Python version (e.g., Python 3.12.0):

```bash
pyenv install 3.12.0
pyenv global 3.12.0
```

#### Step 5: Clone the Project from GitHub

To clone the project repository:

```bash
git clone https://github.com/glyfnet/text-to-midi.git
cd text-to-midi
```

#### Step 6: Install Python Dependencies Using Poetry

This project uses Poetry for dependency management. Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add Poetry to your path (if needed):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Use Poetry to install the required dependencies:

```bash
poetry install
```

#### Step 7: Activate Virtual Environment

To activate the virtual environment, use:

```bash
poetry shell
```

Now you can use the text-to-midi script to generate MIDI files.
Running the Script

The script is defined in the pyproject.toml as a Poetry script command. To generate a MIDI file from a text-based representation of the music, use:

```bash
poetry run text-to-midi sample.txt -o output.mid --play
```

This command will:
- Parse the file sample.txt to generate a MIDI file named output.mid.
- Optionally play the MIDI file using --play.

Alternatively, if you are already in the virtual environment (poetry shell), you can use:

```bash
text-to-midi sample.txt -o output.mid --play
```

Command-Line Options

    file_path (Required): Path to the text file containing music notes.
    --output, -o (Optional): Specify the output MIDI file name. Defaults to output.mid.
    --play (Optional): Plays the generated MIDI file after creation.

Text File Format:

The text file should contain commands to define:

- Tempo (TEMPO)
- Scale (SCALE)
- Track Setup (TRACK)
- Channel Selection (CHANNEL)
- Instrument Selection (INSTRUMENT)
- Note Velocity (VELOCITY)
- Note Duration (DURATION)
- Music Notes or Rest (REST)

Example File:

```
TEMPO 120
SCALE C major
TRACK 1
CHANNEL 1
INSTRUMENT Acoustic Grand Piano
VELOCITY 80
DURATION 1.0
C4 D4 E4 G4
REST 0.5
TRACK 2
CHANNEL 10
INSTRUMENT Side Stick
E4 E4 E4
```

Notes

    MIDI Channels: Channel 10 is reserved for percussion instruments.
    Instruments YAML: Instrument definitions are loaded from instruments.yaml. Make sure you have a properly formatted YAML file for this to work correctly.
    Delta Time: In MIDI, the time value represents the delay (in ticks) between subsequent events, not the absolute time.

Troubleshooting

    If you encounter issues with pygame initialization, ensure that your audio setup is properly configured on your machine.
    Make sure the instruments.yaml file contains valid instrument names and values.

License

This project is licensed under the MIT License.
Contributing

Feel free to open an issue or a pull request if you find a bug or want to contribute to the project.


This `README.md` includes details for using **pyenv** and **Poetry** and how to execute the script via Poetry (`poetry run text-to-midi`). It also explains running the script while in the virtual environment activated through `poetry shell`.

