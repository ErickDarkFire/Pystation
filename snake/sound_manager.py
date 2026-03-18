"""Procedural audio engine: synthesises SFX and looping music themes via numpy."""

import math
import numpy as np
import pygame

SAMPLE_RATE = 44100
CHANNELS = 2

VOL_SFX = 0.55
VOL_MUSIC = 0.26


def _make_tone(freq, duration, vol=0.5, wave="sine", decay=True):
    """Return a stereo int16 array containing a single synthesised tone.

    Args:
        freq: Frequency in Hz.
        duration: Length in seconds.
        vol: Peak amplitude (0–1).
        wave: Waveform type — 'sine', 'square', 'sawtooth', or 'triangle'.
        decay: When True, apply an exponential fade-out envelope.

    """
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    if wave == "sine":
        samples = np.sin(2 * math.pi * freq * t)
    elif wave == "square":
        samples = np.sign(np.sin(2 * math.pi * freq * t))
    elif wave == "sawtooth":
        samples = 2 * (t * freq - np.floor(t * freq + 0.5))
    elif wave == "triangle":
        samples = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
    else:
        samples = np.sin(2 * math.pi * freq * t)
    if decay:
        env = np.exp(-4.0 * t / duration)
        samples = samples * env
    samples = (samples * vol * 32767).astype(np.int16)
    return np.column_stack((samples, samples))


def _make_chord(freqs, duration, vol=0.4, wave="sine", decay=True):
    """Return a stereo int16 array with multiple frequencies mixed into a chord.

    Args:
        freqs: Iterable of frequencies in Hz to mix together.
        duration: Length in seconds.
        vol: Peak amplitude (0–1) of the combined signal.
        wave: Waveform type for all partials — 'sine', 'square', or 'triangle'.
        decay: When True, apply an exponential fade-out envelope.

    """
    n = int(SAMPLE_RATE * duration)
    mixed = np.zeros(n)
    t = np.linspace(0, duration, n, endpoint=False)
    env = np.exp(-3.5 * t / duration) if decay else np.ones(n)
    for f in freqs:
        if wave == "sine":
            mixed += np.sin(2 * math.pi * f * t)
        elif wave == "square":
            mixed += np.sign(np.sin(2 * math.pi * f * t)) * 0.5
        elif wave == "triangle":
            mixed += 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1
    mixed = mixed / len(freqs) * env
    mixed = (mixed * vol * 32767).astype(np.int16)
    return np.column_stack((mixed, mixed))


def _make_noise_burst(duration, vol=0.3):
    """Return a stereo int16 array of white noise with an exponential decay envelope.

    Args:
        duration: Length in seconds.
        vol: Peak amplitude (0–1).

    """
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, endpoint=False)
    noise = np.random.uniform(-1, 1, n)
    env = np.exp(-8.0 * t / duration)
    noise = (noise * env * vol * 32767).astype(np.int16)
    return np.column_stack((noise, noise))


def _arr_to_sound(arr):
    """Convert a contiguous numpy int16 stereo array to a pygame Sound object."""
    arr = np.ascontiguousarray(arr)
    return pygame.sndarray.make_sound(arr)


class SoundManager:
    """Singleton audio manager that owns all SFX and background music themes."""

    _THEME_BUILDERS = {
        0: "_theme_menu",
        1: "_theme_classic",
        2: "_theme_portal",
        3: "_theme_countdown",
        4: "_theme_chaos",
        5: "_theme_obstacles",
    }

    def __init__(self):
        """Initialise pygame.mixer and pre-build all SFX and music themes."""
        self._enabled = True
        self._music_on = True
        self._sfx = {}
        self._music_channel = None
        self._current_level = -99
        self._music_themes = {}

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.pre_init(SAMPLE_RATE, -16, CHANNELS, 512)
                pygame.mixer.init()
            except Exception:
                self._enabled = False
                return

        pygame.mixer.set_num_channels(16)
        self._build_sfx()
        self._build_music_themes()

    def _build_sfx(self):
        """Synthesise and cache all sound-effect pygame Sound objects."""
        try:
            self._sfx["eat"] = _arr_to_sound(
                np.vstack(
                    [
                        _make_tone(440, 0.04, 0.40, "sine"),
                        _make_tone(660, 0.05, 0.40, "sine"),
                        _make_tone(880, 0.07, 0.40, "sine"),
                    ]
                )
            )
            self._sfx["eat_rare"] = _arr_to_sound(
                np.vstack(
                    [
                        _make_chord([523, 659, 784], 0.06, 0.45, "sine"),
                        _make_chord([659, 784, 1047], 0.08, 0.45, "sine"),
                        _make_chord([784, 1047, 1319], 0.14, 0.40, "sine"),
                    ]
                )
            )
            self._sfx["die"] = _arr_to_sound(
                np.vstack(
                    [
                        _make_tone(440, 0.06, 0.50, "sawtooth"),
                        _make_tone(330, 0.06, 0.50, "sawtooth"),
                        _make_tone(220, 0.06, 0.50, "sawtooth"),
                        _make_tone(110, 0.12, 0.50, "sawtooth"),
                        _make_noise_burst(0.10, 0.30),
                    ]
                )
            )
            self._sfx["wall_hit"] = _arr_to_sound(
                np.vstack(
                    [
                        _make_tone(120, 0.04, 0.55, "square"),
                        _make_tone(80, 0.04, 0.50, "square"),
                        _make_noise_burst(0.06, 0.40),
                    ]
                )
            )
        except Exception as e:
            print(f"[SoundManager] SFX build warning: {e}")

    def _build_music_themes(self):
        """Synthesise and cache all background music theme pygame Sound objects."""
        for key, method_name in self._THEME_BUILDERS.items():
            try:
                arr = getattr(self, method_name)()
                snd = _arr_to_sound(arr)
                snd.set_volume(VOL_MUSIC)
                self._music_themes[key] = snd
            except Exception as e:
                print(f"[SoundManager] Music theme {key} warning: {e}")

    def _theme_menu(self):
        """Return a numpy array for the main-menu ambient melody."""
        notes = [261, 294, 329, 349, 392, 349, 329, 294]
        parts = []
        for n in notes:
            parts.append(_make_tone(n, 0.20, 0.18, "sine"))
            parts.append(_make_tone(n * 2, 0.20, 0.07, "sine"))
        return np.vstack(parts)

    def _theme_classic(self):
        """Return a numpy array for the Classic mode chiptune melody."""
        melody = [330, 392, 440, 392, 330, 294, 330, 294]
        bass = [165, 196, 220, 196, 165, 147, 165, 147]
        parts = []
        for m, b in zip(melody, bass):
            parts.append(_make_tone(m, 0.13, 0.22, "square"))
            parts.append(_make_tone(b, 0.13, 0.11, "square"))
        return np.vstack(parts)

    def _theme_portal(self):
        """Return a numpy array for the Portal mode ambient chord loop."""
        chords = [
            [261, 329, 392],
            [220, 277, 349],
            [233, 293, 370],
            [261, 329, 392],
        ]
        parts = []
        for ch in chords:
            parts.append(_make_chord(ch, 0.44, 0.19, "sine", decay=False))
            parts.append(
                _make_chord([f * 2 for f in ch], 0.44, 0.07, "triangle", decay=False)
            )
        return np.vstack(parts)

    def _theme_countdown(self):
        """Return a numpy array for the Contrarreloj (countdown) mode pulse loop."""
        parts = []
        for _ in range(4):
            parts.append(_make_tone(440, 0.08, 0.28, "square"))
            parts.append(_make_noise_burst(0.04, 0.09))
            parts.append(_make_tone(494, 0.08, 0.28, "square"))
            parts.append(_make_noise_burst(0.04, 0.07))
            parts.append(_make_tone(523, 0.10, 0.30, "square"))
            parts.append(_make_tone(494, 0.10, 0.24, "square"))
        return np.vstack(parts)

    def _theme_chaos(self):
        """Return a numpy array for the Caos mode dissonant sawtooth loop."""
        notes = [220, 311, 370, 415, 277, 349, 466, 262]
        parts = []
        for n in notes:
            dur = 0.09 + (n % 3) * 0.03
            parts.append(_make_tone(n, dur, 0.17, "sawtooth"))
            parts.append(_make_tone(n * 3, dur, 0.06, "sine"))
        return np.vstack(parts)

    def _theme_obstacles(self):
        """Return a numpy array for the Obstaculos mode industrial loop."""
        parts = []
        for _ in range(3):
            parts.append(_make_tone(110, 0.15, 0.30, "square"))
            parts.append(_make_noise_burst(0.05, 0.16))
            parts.append(_make_tone(138, 0.10, 0.25, "square"))
            parts.append(_make_tone(110, 0.10, 0.22, "sawtooth"))
            parts.append(_make_noise_burst(0.08, 0.12))
        return np.vstack(parts)

    def play(self, name: str):
        """Play the SFX identified by *name* if SFX are enabled."""
        if not self._enabled:
            return
        snd = self._sfx.get(name)
        if snd:
            snd.set_volume(VOL_SFX)
            snd.play()

    def set_music_level(self, level: int):
        """Switch background music to the theme mapped to *level* (0 = menu)."""
        if not self._enabled or not self._music_on:
            return
        if level == self._current_level:
            return
        self._current_level = level
        if self._music_channel and self._music_channel.get_busy():
            self._music_channel.stop()
        theme = self._music_themes.get(level)
        if theme:
            self._music_channel = theme.play(-1)

    def stop_music(self):
        """Stop any currently playing background music track."""
        if self._music_channel:
            self._music_channel.stop()
        self._current_level = -99

    def toggle_music(self):
        """Toggle background music on/off and return the new state."""
        self._music_on = not self._music_on
        if not self._music_on:
            self.stop_music()
        else:
            self.set_music_level(0)
        return self._music_on

    def toggle_sfx(self):
        """Toggle sound effects on/off and return the new state."""
        self._enabled = not self._enabled
        return self._enabled

    @property
    def music_on(self):
        """True when background music is currently enabled."""
        return self._music_on

    @property
    def sfx_on(self):
        """True when sound effects are currently enabled."""
        return self._enabled


_instance = None


def get_sound_manager() -> SoundManager:
    """Return the global SoundManager singleton, creating it on first call."""
    global _instance
    if _instance is None:
        _instance = SoundManager()
    return _instance
