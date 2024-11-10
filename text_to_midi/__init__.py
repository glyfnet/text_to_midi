import click
import yaml
from mido import Message, MidiFile, MidiTrack, bpm2tempo
import pygame
import time

# Load instrument and percussion data from YAML file
with open('instruments.yaml', 'r') as f:
    data = yaml.safe_load(f)

INSTRUMENTS = data["instruments"]
PERCUSSION_INSTRUMENTS = data["percussion"]

# Dictionary to convert note names to MIDI numbers
NOTE_TO_MIDI = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
}

# Define common scales
SCALES = {
    'major': [0, 2, 4, 5, 7, 9, 11],
    'minor': [0, 2, 3, 5, 7, 8, 10],
    'dorian': [0, 2, 3, 5, 7, 9, 10],
    'mixolydian': [0, 2, 4, 5, 7, 9, 10],
}

def note_to_midi_number(note):
    """Convert note in format (e.g., C4, D#4) to MIDI number."""
    note_name = note[:-1]  # Extract the note name (e.g., "C", "D#")
    octave = int(note[-1])  # Extract the octave (e.g., "4")
    if note_name not in NOTE_TO_MIDI:
        raise ValueError(f"Invalid note name: {note_name}")
    return (octave + 1) * 12 + NOTE_TO_MIDI[note_name]

def get_instrument_value(instrument_name, channel):
    """Retrieve the MIDI instrument value based on the instrument name and channel.
    
    Throws an error if the instrument name is unknown.
    """
    instrument_name = instrument_name.lower()

    if channel == 10:
        # Percussion instruments are on channel 10
        if instrument_name in PERCUSSION_INSTRUMENTS:
            return PERCUSSION_INSTRUMENTS[instrument_name]
        else:
            raise ValueError(f"Unknown percussion instrument: {instrument_name}")
    else:
        # Regular melodic instruments for other channels
        if instrument_name in INSTRUMENTS:
            return INSTRUMENTS[instrument_name]
        else:
            raise ValueError(f"Unknown melodic instrument: {instrument_name}")

def text_file_to_midi(file_path):
    """Convert notes in a text file to a MidiFile object with multiple tracks, looping, tempo, scale, and instrument settings."""
    mid = MidiFile()
    velocity = 64
    duration = 1.0
    tempo = 120
    time_per_beat = bpm2tempo(tempo) / 1_000_000
    root_note = 'C'
    scale = SCALES['major']
    tracks = {}
    current_track_num = 1
    channel = 1  # Default to Channel 1 for melodic instruments

    # Loop management
    loop_buffer = []
    inside_loop = False
    loop_repeat_count = 1

    click.echo("Starting MIDI file generation...")

    with open(file_path, 'r') as file:
        lines = file.readlines()
        i = 0

        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("#") or line.startswith("//") or not line:
                # Skip comments or empty lines
                i += 1
                continue

            # Remove inline comments and split into parts
            line = line.split("#")[0].strip()
            parts = line.split()
            if not parts:
                i += 1
                continue

            command = parts[0].upper()
            part_1 = parts[1] if len(parts) > 1 else None
            part_2 = parts[2] if len(parts) > 2 else None

            # Handle valid commands directly
            if command == "TEMPO":
                tempo = int(part_1)
                time_per_beat = bpm2tempo(tempo) / 1_000_000
                click.echo(f"Setting tempo: {tempo} BPM")

            elif command == "SCALE":
                root_note = part_1.capitalize()
                if root_note not in NOTE_TO_MIDI:
                    raise ValueError(f"Invalid root note: {root_note}")
                
                scale_mode = part_2.lower() if part_2 else 'major'
                if scale_mode not in SCALES:
                    raise ValueError(f"Invalid scale mode: {scale_mode}")
                
                scale = SCALES.get(scale_mode)
                click.echo(f"Setting scale: {root_note} {scale_mode}")

            elif command == "TRACK":
                current_track_num = int(part_1)
                channel = 1
                if current_track_num not in tracks:
                    tracks[current_track_num] = MidiTrack()
                    mid.tracks.append(tracks[current_track_num])
                    click.echo(f"Created new track {current_track_num}")

            elif command == "CHANNEL":
                channel = int(part_1)

            elif command == "INSTRUMENT":
                instrument_name = part_1 if part_1 else 'acoustic_grand_piano'
                instrument = get_instrument_value(instrument_name, channel)
                tracks[current_track_num].append(Message('program_change', program=instrument, channel=channel, time=0))
                click.echo(f"Setting track {current_track_num} to instrument {instrument_name}")

            elif command == "VELOCITY":
                velocity = int(part_1)
                click.echo(f"Setting velocity: {velocity}")

            elif command == "DURATION":
                duration = float(part_1)
                click.echo(f"Setting duration: {duration}")

            elif command == "LOOP":
                if inside_loop:
                    raise ValueError("Nested loops are not supported")
                
                loop_repeat_count = int(part_1) if part_1 else 1
                inside_loop = True
                loop_buffer = []
                click.echo("Starting loop block")
                i += 1
                continue

            elif command == "END":
                click.echo(f"Ending loop block, repeating {loop_repeat_count} times")

                # Ensure the current track exists
                if current_track_num not in tracks:
                    tracks[current_track_num] = MidiTrack()
                    mid.tracks.append(tracks[current_track_num])
                    click.echo(f"Created new track {current_track_num} for loop processing")

                for _ in range(loop_repeat_count):
                    for loop_line in loop_buffer:
                        process_line(loop_line, tracks[current_track_num], duration, velocity, time_per_beat, root_note, scale, mid.ticks_per_beat, channel)
                inside_loop = False
                i += 1
                continue

            # If we're inside a loop, accumulate loop lines
            if inside_loop:
                loop_buffer.append(line)
            else:
                # Ensure the current track exists before processing the line
                if current_track_num not in tracks:
                    tracks[current_track_num] = MidiTrack()
                    mid.tracks.append(tracks[current_track_num])
                    click.echo(f"Created new track {current_track_num}")

                # Process the line for notes and rests
                process_line(line, tracks[current_track_num], duration, velocity, time_per_beat, root_note, scale, mid.ticks_per_beat, channel)

            i += 1

    click.echo("MIDI file generation complete.")
    return mid

def process_line(line, track, duration, velocity, time_per_beat, root_note, scale, ticks_per_beat, channel):
    """Process a single line of the input file to add notes or set parameters."""
    parts = line.split()
    command = parts[0].upper()

    if command == "REST":
        # Handle rest by advancing time
        rest_duration = float(parts[1]) if len(parts) > 1 else duration
        ticks = int(rest_duration / time_per_beat * ticks_per_beat)
        track.append(Message('note_off', velocity=0, time=ticks))
        click.echo(f"Adding rest: {rest_duration} beats")

    else:
        # Process note sequence with calculated durations and velocities
        notes = []
        for part in parts:
            if channel == 10 and part.isdigit():
                # Handle percussion channel
                midi_note = int(part)
                if midi_note in PERCUSSION_INSTRUMENTS:
                    notes.append(midi_note)
            elif part[0].isalpha() and part[-1].isdigit():
                # Convert note like C4 or G#3 to MIDI number
                midi_note = note_to_midi_number(part)
                notes.append(midi_note)

        note_duration = duration
        note_velocity = velocity
        ticks = int(note_duration / time_per_beat * ticks_per_beat)

        click.echo(f"Adding notes {notes} with duration {note_duration} and velocity {note_velocity}")

        for note in notes:
            # Start note with `note_on` event, using the cumulative offset
            track.append(Message('note_on', note=note, velocity=note_velocity, time=0, channel=channel))
            # End note with `note_off` after the duration
            track.append(Message('note_off', time=ticks, channel=channel))
        
def play_midi_file(filename):
    """Plays a MIDI file using pygame."""
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', default='output.mid', help='Output MIDI file name')
@click.option('--play', is_flag=True, help='Play the MIDI file after creation')
def main(file_path, output, play):
    """
    Convert an expressive text file of musical notes to a MIDI file with multiple tracks, looping, tempo, scale, and instruments.
    """
    midi_file = text_file_to_midi(file_path)
    midi_file.save(output)
    click.echo(f'Successfully created MIDI file: {output}')

    if play:
        click.echo("Playing MIDI file...")
        play_midi_file(output)

if __name__ == '__main__':
    main()
