"""
MIDI Music Generator
Creates background music tracks for the game
"""

import mido
import os

def create_background_music():
    """Create a simple ambient background MIDI track"""
    # Create a new MIDI file
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Set up instrument (pad/strings for ambient feel)
    track.append(mido.Message('program_change', program=88, time=0))  # Pad 1 (new age)
    
    # Define a more complex chord progression
    # I - vi - IV - V - iii - vi - ii - V (C - Am - F - G - Em - Am - Dm - G)
    chords = [
        [60, 64, 67],  # C major (C, E, G)
        [57, 60, 64],  # A minor (A, C, E)  
        [53, 57, 60],  # F major (F, A, C)
        [55, 59, 62],  # G major (G, B, D)
        [52, 55, 59],  # E minor (E, G, B)
        [57, 60, 64],  # A minor (A, C, E)
        [50, 53, 57],  # D minor (D, F, A)
        [55, 59, 62],  # G major (G, B, D)
    ]
    
    # Vary the rhythm - some chords held longer
    chord_durations = [960, 480, 960, 480, 720, 480, 720, 960]  # Different lengths
    
    # Play the progression several times with variations
    for cycle in range(6):  # 6 cycles for more variation
        for i, (chord, duration) in enumerate(zip(chords, chord_durations)):
            # Add some bass notes occasionally
            if cycle > 2 and i % 2 == 0:  # Add bass on cycles 3+ every other chord
                bass_note = chord[0] - 12  # Octave lower
                track.append(mido.Message('note_on', channel=0, note=bass_note, velocity=30, time=0))
            
            # Play chord notes with slight timing variation
            for j, note in enumerate(chord):
                delay = j * 20 if cycle > 1 else 0  # Slight arpeggio effect after first cycle
                track.append(mido.Message('note_on', channel=0, note=note, velocity=40 + cycle * 2, time=delay))
            
            # Hold the chord
            track.append(mido.Message('note_off', channel=0, note=chord[0], velocity=0, time=duration - sum(range(len(chord))) * 20))
            
            # Release other notes
            for note in chord[1:]:
                track.append(mido.Message('note_off', channel=0, note=note, velocity=0, time=0))
            
            # Release bass note if present
            if cycle > 2 and i % 2 == 0:
                track.append(mido.Message('note_off', channel=0, note=bass_note, velocity=0, time=0))
    
    # Add a more elaborate melody line
    melody_track = mido.MidiTrack()
    mid.tracks.append(melody_track)
    
    # Set up a different instrument for melody
    melody_track.append(mido.Message('program_change', program=73, time=0))  # Flute
    
    # More complex melody with different patterns per cycle
    melody_patterns = [
        [72, 74, 76, 77, 76, 74, 72, 69],  # Ascending then descending
        [67, 69, 72, 74, 76, 74, 72, 67],  # Different range
        [76, 77, 79, 76, 74, 72, 69, 67],  # Higher notes
        [60, 62, 64, 67, 69, 67, 64, 60],  # Lower octave
    ]
    
    for cycle, pattern in enumerate(melody_patterns):
        for i, note in enumerate(pattern):
            velocity = 35 + (i % 3) * 5  # Dynamic accents
            note_duration = 480 if i % 2 == 0 else 360  # Rhythm variation
            melody_track.append(mido.Message('note_on', channel=1, note=note, velocity=velocity, time=0))
            melody_track.append(mido.Message('note_off', channel=1, note=note, velocity=0, time=note_duration))
    
    # Save the MIDI file
    os.makedirs('music', exist_ok=True)
    mid.save('music/background_ambient.mid')
    print("Created enhanced background_ambient.mid")

def create_upbeat_music():
    """Create a more upbeat track for action sequences"""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Use a more energetic instrument
    track.append(mido.Message('program_change', program=25, time=0))  # Electric Guitar
    
    # More energetic chord progression with power chords
    chords = [
        [48, 52, 55],  # C major (lower octave)
        [50, 53, 57],  # D major
        [45, 49, 52],  # F major 
        [47, 50, 54],  # G major
        [52, 55, 59],  # E major
        [50, 53, 57],  # D major
        [48, 52, 55],  # C major
        [47, 50, 54],  # G major
    ]
    
    ticks_per_chord = 240  # Even faster tempo
    
    for cycle in range(8):
        for i, chord in enumerate(chords):
            # Add driving rhythm with accents
            accent = 80 if i % 4 == 0 else 60
            for note in chord:
                track.append(mido.Message('note_on', channel=0, note=note, velocity=accent, time=0))
            
            # Shorter note durations for driving feel
            track.append(mido.Message('note_off', channel=0, note=chord[0], velocity=0, time=ticks_per_chord))
            
            for note in chord[1:]:
                track.append(mido.Message('note_off', channel=0, note=note, velocity=0, time=0))
    
    # Add percussion-like track
    drums_track = mido.MidiTrack()
    mid.tracks.append(drums_track)
    drums_track.append(mido.Message('program_change', program=116, time=0))  # Synth drum
    
    # Simple drum pattern
    for cycle in range(32):  # More repetitions for driving rhythm
        # Kick on 1 and 3
        drums_track.append(mido.Message('note_on', channel=9, note=36, velocity=100, time=0))
        drums_track.append(mido.Message('note_off', channel=9, note=36, velocity=0, time=240))
        
        # Snare on 2 and 4
        drums_track.append(mido.Message('note_on', channel=9, note=38, velocity=80, time=0))
        drums_track.append(mido.Message('note_off', channel=9, note=38, velocity=0, time=240))
    
    mid.save('music/background_upbeat.mid')
    print("Created enhanced background_upbeat.mid")

def create_exploration_music():
    """Create a mysterious exploration track"""
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Mysterious instrument
    track.append(mido.Message('program_change', program=95, time=0))  # Pad 8 (sweep)
    
    # Minor key progression for mystery
    chords = [
        [57, 60, 64],  # A minor
        [53, 56, 60],  # F minor
        [55, 58, 62],  # G minor  
        [52, 55, 59],  # E minor
        [50, 53, 57],  # D minor
        [57, 60, 64],  # A minor
        [55, 58, 62],  # G minor
        [57, 60, 64],  # A minor
    ]
    
    # Slower, more mysterious timing
    ticks_per_chord = 1440  # Longer, more atmospheric
    
    for cycle in range(4):
        for chord in chords:
            # Soft, mysterious volume
            for note in chord:
                track.append(mido.Message('note_on', channel=0, note=note, velocity=25 + cycle * 5, time=0))
            
            track.append(mido.Message('note_off', channel=0, note=chord[0], velocity=0, time=ticks_per_chord))
            
            for note in chord[1:]:
                track.append(mido.Message('note_off', channel=0, note=note, velocity=0, time=0))
    
    # Add eerie melody
    melody_track = mido.MidiTrack()
    mid.tracks.append(melody_track)
    melody_track.append(mido.Message('program_change', program=54, time=0))  # Synth voice
    
    # Eerie melody pattern
    melody_notes = [69, 67, 64, 62, 60, 62, 64, 67, 69, 72, 69, 67, 64, 60, 57, 60]
    
    for cycle in range(2):
        for i, note in enumerate(melody_notes):
            velocity = 30 + (i % 5) * 3
            melody_track.append(mido.Message('note_on', channel=1, note=note, velocity=velocity, time=0))
            melody_track.append(mido.Message('note_off', channel=1, note=note, velocity=0, time=720))
    
    mid.save('music/background_exploration.mid')
    print("Created background_exploration.mid")

if __name__ == "__main__":
    create_background_music()
    create_upbeat_music()
    create_exploration_music()
    print("Enhanced MIDI files created successfully!")