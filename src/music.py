"""
Music and Sound System
Handles background music using MIDI files
"""

import pygame
import os
import random

class MusicSystem:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.current_music = None
        self.music_volume = 0.7
        self.music_tracks = []
        self.is_playing = False
        self.load_music_tracks()
        
    def load_music_tracks(self):
        """Load MIDI music tracks, prioritizing ambient and exploration"""
        music_dir = "music"
        
        # Focus on ambient and exploration tracks as requested
        preferred_tracks = [
            'background_ambient.mid',
            'background_exploration.mid'
        ]
        
        if os.path.exists(music_dir):
            # First try to load preferred tracks
            for track_name in preferred_tracks:
                track_path = os.path.join(music_dir, track_name)
                if os.path.exists(track_path):
                    self.music_tracks.append(track_path)
                    print(f"Loaded preferred track: {track_name}")
            
            # If no preferred tracks found, load any MIDI files
            if not self.music_tracks:
                for file in os.listdir(music_dir):
                    if file.endswith(('.mid', '.midi')):
                        self.music_tracks.append(os.path.join(music_dir, file))
                        print(f"Loaded track: {file}")
    
    def play_background_music(self, loop=True):
        """Start playing background music using MIDI files"""
        if self.music_tracks and not self.is_playing:
            try:
                # Start with a random track (prefer ambient/exploration)
                track = random.choice(self.music_tracks)
                pygame.mixer.music.load(track)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(-1 if loop else 0)
                self.current_music = track
                self.is_playing = True
                print(f"Started playing: {os.path.basename(track)}")
            except pygame.error as e:
                print(f"Error starting music: {e}")
                self.is_playing = False
    
    def change_track(self):
        """Change to a different random track"""
        if len(self.music_tracks) > 1:
            # Get a different track than the current one
            available_tracks = [t for t in self.music_tracks if t != self.current_music]
            if available_tracks:
                track = random.choice(available_tracks)
                try:
                    pygame.mixer.music.load(track)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1)
                    self.current_music = track
                    print(f"Changed to: {os.path.basename(track)}")
                except pygame.error as e:
                    print(f"Error changing track: {e}")
    
    def play_simple_tone(self):
        """Legacy method - now uses MIDI files instead"""
        self.play_background_music()
    
    def stop_music(self):
        """Stop the background music"""
        pygame.mixer.music.stop()
        self.current_music = None
        self.is_playing = False
    
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def is_playing_music(self):
        """Check if music is currently playing"""
        return pygame.mixer.music.get_busy() and self.is_playing
    
    def update(self, dt):
        """Update music system - restart if track ended"""
        if self.is_playing and not pygame.mixer.music.get_busy():
            # Track ended, play another one
            self.play_background_music()