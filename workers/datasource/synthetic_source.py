import threading
import time
import numpy as np
from settings.settings import SAMPLE_RATE, PACKED_BUFFER_SIZE
from simulations.stress_config import BLEStressConfig
import wave


class SyntheticBLESource:
    def __init__(self, pipeline, config=BLEStressConfig()):
        self.pipeline = pipeline
        self.config = config
        self._queue = []
        self._network_credit = 0.0

        self.sample_rate = SAMPLE_RATE
        self.packet_size = PACKED_BUFFER_SIZE

        self._running = False
        self._streaming = False
        self._recovery_factor = 1.0
        self._recovery_decay = 0.97
        
        self.ack = False

        # congestion simulation buffer
        self._queue = []

        # timing
        self._next_t = time.perf_counter()

        # worker thread (created on demand)
        self._thread = None
        
        self._gen_counter = 0

    # =========================================================
    # CONTROL
    # =========================================================
    def cmd_start(self):
        if self._streaming:
            return

        self._streaming = True
        self._running = True

        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self._thread.start()
        
        self.ack = True

    def cmd_stop(self):
        if not self._streaming:
            return

        self._streaming = False
        self._running = False

        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
            
        self.ack = True

    # =========================================================
    # SIGNAL GENERATION
    # =========================================================
    def _generate(self, n):
        noise = np.random.randn(n)
        noise = np.convolve(noise, np.ones(5) / 5, mode='same') * self.config.noise_level

        spikes = np.zeros(n)
        i = 0

        while i < n:
            if np.random.rand() < 0.0002:
                amp = np.random.choice([2000, 3000, 4000, 5000])
                width = np.random.randint(5, 12)

                for w in range(width):
                    if i + w < n:
                        spikes[i + w] += (
                            amp *
                            (1 - np.exp(-w / 2)) *
                            np.exp(-w / 3)
                        )

                i += np.random.randint(25, 80)
            else:
                i += 1

        signal = noise + spikes
        return np.clip(signal, -8192, 8191).astype(np.int16)

    # =========================================================
    # WORKER LOOP
    # =========================================================
    def _run_loop(self):

        dt = self.packet_size / self.sample_rate
        next_t = time.perf_counter()

        while self._running:

            if not self._streaming:
                time.sleep(0.01)
                next_t = time.perf_counter()
                continue

            # =====================================================
            # PACKET GENERATION
            # =====================================================
            packet = np.stack(
                [
                    self._generate_simple(self.packet_size),
                    self._generate_wav(self.packet_size),
                ],
                axis=1,
            )

            self.pipeline.live_counter()

            # =====================================================
            # PACKET LOSS (source-side drop)
            # =====================================================
            if (
                self.config.enable_packet_loss
                and np.random.rand() < self.config.packet_loss_prob
            ):
                continue

            # =====================================================
            # NETWORK / CONGESTION MODEL
            # =====================================================
            if self.config.enable_congestion:

                # Packet enters network buffer
                self._queue.append(packet)

                # Buffer overflow -> drop oldest packet
                while len(self._queue) > self.config.max_queue_size:
                    self._queue.pop(0)

                # -------------------------------------------------
                # Current network throughput
                # -------------------------------------------------

                congested = (
                    np.random.rand() < self.config.congestion_prob
                )

                if congested:
                    # During congestion:
                    # network delivers less than realtime
                    network_rate = np.random.uniform(
                        self.config.congested_rate_min,
                        self.config.congested_rate_max,
                    )
                else:
                    # Recovery / normal operation:
                    # network may deliver faster than realtime
                    network_rate = np.random.uniform(
                        self.config.recovery_rate_min,
                        self.config.recovery_rate_max,
                    )

                self._network_credit += network_rate

                # -------------------------------------------------
                # Release packets according to available bandwidth
                # -------------------------------------------------

                while (
                    self._network_credit >= 1.0
                    and len(self._queue) > 0
                ):
                    pkt = self._queue.pop(0)

                    send_count = int(round(self._recovery_factor))

                    for _ in range(send_count):
                        self.pipeline.push_raw(pkt)

                    self._network_credit -= 1.0

            else:
                # Direct transmission
                send_count = int(round(self._recovery_factor))

                for _ in range(send_count):
                    self.pipeline.push_raw(packet)

            # =====================================================
            # BURST DELAY
            # (temporary network pause)
            # =====================================================
            if (
                self.config.enable_burst
                and np.random.rand() < self.config.burst_prob
            ):
                time.sleep(
                    np.random.uniform(
                        *self.config.burst_delay_ms
                    )
                    / 1000.0
                )

            # =====================================================
            # STALL EVENT
            # (hard network freeze)
            # =====================================================
            if (
                self.config.enable_stall
                and np.random.rand() < self.config.stall_prob
            ):
                stall_duration = np.random.uniform(
                    *self.config.stall_ms
                ) / 1000.0
                
                print("stall")

                time.sleep(stall_duration)

                self._recovery_factor = min(
                    self._recovery_factor + 3.0,
                    6.0  # cap zodat het niet explodeert
                )

            # =====================================================
            # TIMING CONTROL
            # =====================================================
            next_t += dt

            if self.config.enable_jitter:
                jitter = np.random.normal(
                    0.0,
                    self.config.jitter_ms_std / 1000.0,
                )
            else:
                jitter = 0.0

            target_t = next_t + jitter

            sleep_time = (
                target_t - time.perf_counter()
            )

            if sleep_time > 0:
                time.sleep(sleep_time)

            # =====================================================
            # RECOVERY
            # Avoid runaway backlog after long stalls
            # =====================================================
            now = time.perf_counter()

            if now - next_t > 1.0:
                next_t = now
                
            self._recovery_factor *= self._recovery_decay

            if self._recovery_factor < 1.0:
                self._recovery_factor = 1.0
                
                            
    def connect(self, device):
        print(device)
        self.ack = True
        
    def disconnect(self):
        self.ack = True
        
        
    def _generate_simple(self, n):
        sr = 12000
        signal = np.zeros(n, dtype=np.float64)

        amplitude = np.random.normal(2000, 500)
        step = sr  # 1 seconde

        # globale sample index (belangrijk!)
        start_idx = self._gen_counter

        for i in range(n):
            global_idx = start_idx + i

            # elke seconde een pulse
            if global_idx % step == 0:
                # korte pulse (5 samples decay)
                for w in range(5):
                    if i + w < n:
                        signal[i + w] += amplitude * (1 - w / 5)

        self._gen_counter += n
        
        return np.clip(signal, -8192, 8191).astype(np.int16)
    


    def _generate_wav(self, n):

        # open WAV (1x doen in __init__ is beter, maar hier simpel gehouden)
        if not hasattr(self, "_wav"):
            self._wav = wave.open("rec_ch2_withoutstim.wav", "rb")
            self._wav_sr = self._wav.getframerate()
            self._wav_channels = self._wav.getnchannels()
            self._wav_length = self._wav.getnframes()

        # globale positie in audio stream
        start = self._gen_counter

        # wrap-around (loop audio)
        start = start % self._wav_length

        # lees samples
        self._wav.setpos(start)
        raw = self._wav.readframes(n)

        # convert bytes -> int16
        audio = np.frombuffer(raw, dtype=np.int16)

        # stereo → mono (indien nodig)
        if self._wav_channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1).astype(np.int16)

        # als we aan het einde zitten → wrap fill
        if len(audio) < n:
            self._wav.setpos(0)
            raw2 = self._wav.readframes(n - len(audio))
            audio2 = np.frombuffer(raw2, dtype=np.int16)

            if self._wav_channels == 2:
                audio2 = audio2.reshape(-1, 2).mean(axis=1).astype(np.int16)

            audio = np.concatenate([audio, audio2])

        self._gen_counter += n

        audio = audio.astype(np.int32)
        # 1) map int16 (-32768..32767) → 0..65535
        audio = audio + 32768
        # 2) downscale naar 12-bit range (0..4095)
        audio = audio >> 4
        # 3) clamp safety
        audio = np.clip(audio, 0, 4095)
        return audio.astype(np.uint16)