import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

x, samplerate = sf.read('BYB_Recording_2026-04-22_15.23.02.wav')
print(samplerate)
n_frames = len(x)
pre_search_ms = 4
post_search_ms = 6

###################################################
#Plotting signal
###################################################
t = np.linspace(0, n_frames / samplerate, num=n_frames)

plt.figure(figsize=(12, 4))
plt.plot(t, x, color='blue')
plt.title("Raw waveform (WAV)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()

###################################################
#Spike detection 
###################################################
x_z = (x - np.mean(x)) / np.std(x) # normalize to z-score

threshold = 5  # >5 std above mean
min_distance_sec = 0.005  # 5 ms refractory period
min_distance_samples = int(min_distance_sec * samplerate)

peaks, _ = find_peaks(x_z, height=threshold, distance=min_distance_samples)

plt.figure(figsize=(14, 4))
plt.plot(t, x, label="Signal (z-scored)", linewidth=1)
plt.scatter(t[peaks], x[peaks], color='red', label='Spikes', s=20)
plt.title("Spike Detection")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (z-score)")
plt.legend()
plt.grid(True)
plt.show()

###################################################
#Average Spike
###################################################
pre_search = int(pre_search_ms * 1e-3 * samplerate)
post_search = int(post_search_ms * 1e-3 * samplerate)

spike_snippets = []

for p in peaks:
    if p - pre_search >= 0 and p + post_search < len(x):
        snippet = x[p - pre_search : p + post_search]
        spike_snippets.append(snippet)

spike_snippets = np.array(spike_snippets)
avg_snippet = np.mean(spike_snippets, axis=0)
peak_idx = np.argmax(np.abs(avg_snippet))

###################################################
#Finding return to baseline timestamps
###################################################
env = np.convolve(np.abs(avg_snippet), np.ones(5)/5, mode='same')
sigma = np.median(env[:int(0.2*len(env))]) / 0.6745
thr = 3 * sigma

left = peak_idx
while left > 0 and env[left] > thr:
    left -= 1

right = peak_idx
while right < len(env)-1 and env[right] > thr:
    right += 1

pre_ms = (peak_idx - left) / samplerate * 1000
post_ms = (right - peak_idx) / samplerate * 1000
print("Pre-spike (ms):", pre_ms)
print("Post-spike (ms):", post_ms)

spikes = spike_snippets[:, left:right]
avg = np.mean(spikes, axis=0)

###################################################
#Noise power and SNR calculation
###################################################
noise_start = 83
noise_end = 87
noise_mask = (t >= noise_start) & (t <= noise_end)
noise_segment = x[noise_mask]
noise_power = np.var(noise_segment)
print("Noise variance:", noise_power)

signal_power_avg = np.mean(avg**2)
snr_db_avg = 10 * np.log10(signal_power_avg / noise_power)
print("SNR:", snr_db_avg, "dB")

###################################################
#Plotting average spike with return to baseline
###################################################
t_snip = np.linspace(-pre_search_ms, post_search_ms, spike_snippets.shape[1])
pre_ms = (peak_idx - left) / samplerate * 1000
post_ms = (right - peak_idx) / samplerate * 1000
noise_end_idx = int(0.2 * len(avg_snippet))
noise_end_time = t_snip[noise_end_idx]

plt.figure(figsize=(8, 4))
for s in spike_snippets:
    plt.plot(t_snip, s, color='gray', alpha=0.2)

plt.plot(t_snip, avg_snippet, color='red', linewidth=2, label='Average spike')
plt.axvspan(t_snip[0], t_snip[noise_end_idx], color='orange', alpha=0.12)
plt.plot([], [], color='orange', alpha=0.3, label='Noise region (baseline estimate)')
plt.title("Average Spike Shape")
plt.xlabel("Time (ms)")
plt.axvline(-pre_ms, color='black', linestyle='--', label='pre')
plt.axvline(post_ms, color='black', linestyle='--', label='post')   
plt.axvspan(
    t_snip[0],
    t_snip[noise_end_idx],
    color='orange',
    alpha=0.12,
    label='_nolegend_'
)
plt.ylabel("Amplitude ")
plt.ylim(-0.4,0.55)
plt.legend()
plt.grid(True)
plt.show()