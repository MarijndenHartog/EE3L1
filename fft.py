from scipy.signal import stft
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# Load audio
x, sr = sf.read('session_20260604_144032.wav')

# Convert to mono if stereo
if x.ndim > 1:
    x = x[:, 0]  # meestal linkerkanaal; jij gebruikte eerder [:,1]

# Time axis for waveform
t = np.arange(len(x)) / sr

# --- STFT ---
f, tt, Zxx = stft(x, fs=sr, nperseg=1024)
magnitude_db = 20 * np.log10(np.abs(Zxx) + 1e-10)

# --- Combined figure ---
fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(12, 8),
    sharex=True,
    gridspec_kw={'height_ratios': [1, 2]}
)

# Waveform
ax1.plot(t, x)
ax1.set_title("Waveform")
ax1.set_ylabel("Amplitude")

# Spectrogram (STFT)
img = ax2.imshow(
    magnitude_db,
    aspect='auto',
    origin='lower',
    extent=[tt.min(), tt.max(), f.min(), f.max()]
)
ax2.set_title("STFT Magnitude (dB)")
ax2.set_xlabel("Time (s)")
ax2.set_ylabel("Frequency (Hz)") 

plt.tight_layout()
plt.show()