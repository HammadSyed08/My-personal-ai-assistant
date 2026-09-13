
import os
import sys
import wave
import struct
import math



PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ---------------------------------------------------------
# HAMMU audio effects
# ---------------------------------------------------------

AUDIO_DIR = os.path.join(
    PROJECT_ROOT,
    "frontend",
    "assets"
)

os.makedirs(AUDIO_DIR, exist_ok=True)


def create_hammu_sound(
    filename,
    frequencies,
    duration,
    volume=0.08
):
    """
    Generate a small futuristic WAV sound locally.
    No external audio package is required.
    """

    path = os.path.join(
        AUDIO_DIR,
        filename
    )

    if os.path.exists(path):
        return path

    sample_rate = 44100
    total_samples = int(
        sample_rate * duration
    )

    frames = []

    for i in range(total_samples):

        t = i / sample_rate

        # Smooth attack
        attack = min(
            1.0,
            t / 0.05
        )

        # Smooth release
        release = min(
            1.0,
            (duration - t) / 0.20
        )

        envelope = max(
            0.0,
            min(
                attack,
                release
            )
        )

        signal = 0.0

        for frequency in frequencies:
            signal += math.sin(
                2 * math.pi * frequency * t
            )

        signal /= len(frequencies)

        sample = int(
            32767 *
            volume *
            envelope *
            signal
        )

        frames.append(
            struct.pack(
                "<h",
                sample
            )
        )

    with wave.open(
        path,
        "wb"
    ) as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(
            sample_rate
        )

        wav_file.writeframes(
            b"".join(frames)
        )

    return path


STARTUP_SOUND = create_hammu_sound(
    "hammu_startup.wav",
    [70, 110, 165, 220, 330, 440],
    1.35,
    0.15
)

LISTEN_TICK_SOUND = create_hammu_sound(
    "hammu_listen_tick.wav",
    [1050, 1550],
    0.075,
    0.015
)