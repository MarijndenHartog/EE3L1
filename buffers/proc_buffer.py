"""
import numpy as np
import threading

# ── Constanten ────────────────────────────────────────────────────────────────
from settings.settings import SAMPLE_RATE, REFRESH_FPS
IDEAL_STEP    = SAMPLE_RATE // REFRESH_FPS   # 300 samples/frame

STARTUP_MS  = 50
STARTUP_MIN = int(SAMPLE_RATE * STARTUP_MS / 1000)   # 300 samples (~25 ms)


LAG_DEAD_ZONE   = IDEAL_STEP // 2             # 150 samples; geen correctie
LAG_SCALE_FULL  = SAMPLE_RATE * 2             # 24 000 samples = 2 s achterstand

MAX_STEP_DELTA = 8

MIN_STEP = 10   #  75
MAX_STEP = 3000        # 1200


class ProcessedBuffer:


    def __init__(self, capacity: int, channels: int = 2, dtype=np.int16):
        self.capacity = int(capacity)
        self.channels = int(channels)
        self.dtype    = dtype

        self.buffer    = np.zeros((self.capacity, self.channels), dtype=self.dtype)
        self.write_idx = 0
        self.filled    = 0
        self.read_idx  = 0

        self._step_f: float = float(IDEAL_STEP)

        self.lock = threading.Lock()

    # ── Write ─────────────────────────────────────────────────────────────────
    def write(self, samples: np.ndarray):

        if samples.ndim != 2 or samples.shape[1] != self.channels:
            raise ValueError(
                f"Expected shape (N, {self.channels}), got {samples.shape}"
            )
        n = len(samples)
        with self.lock:
            first_part = min(self.capacity - self.write_idx, n)
            # 1. write first segment
            self.buffer[self.write_idx:self.write_idx + first_part] = samples[:first_part]
            # 2. wrap-around write if needed
            remaining = n - first_part
            if remaining > 0:
                self.buffer[:remaining] = samples[first_part:]
            # 3. update write pointer
            self.write_idx = (self.write_idx + n) % self.capacity
            # 4. track valid fill level (important early startup)
            self.filled = min(self.capacity, self.filled + n)

    # ── Read ──────────────────────────────────────────────────────────────────
    def read(self, n: int, nominal_step: int = IDEAL_STEP):
        
        with self.lock:
            # 1. Startup-guard
            
            if self.filled < STARTUP_MIN:
                return None, IDEAL_STEP
 
            # 2. Effectieve venstergrootte: groeit mee met filled
            k = min(n, self.filled)
 
            # 4. Lag meten t.o.v. huidig venster van grootte k
            end_of_window = (self.read_idx + k) % self.capacity
            lag = int((self.write_idx - end_of_window) % self.capacity)
 
            # 5. Adaptieve step (alleen actief in steady state)
            if lag <= LAG_DEAD_ZONE:
                target = float(nominal_step)
            else:
                t      = min(1.0, (lag - LAG_DEAD_ZONE) /
                                  (LAG_SCALE_FULL - LAG_DEAD_ZONE))
                target = nominal_step + t * (MAX_STEP - nominal_step)
 
            delta        = float(np.clip(target - self._step_f,
                                         -MAX_STEP_DELTA, MAX_STEP_DELTA))
            self._step_f = float(np.clip(self._step_f + delta, MIN_STEP, MAX_STEP))
            step         = int(round(self._step_f))
 
            # 6. read_idx opschuiven; clamp zodat venster write_idx niet passeert
            new_read = (self.read_idx + step) % self.capacity
            space    = int((self.write_idx - new_read) % self.capacity)
            if space < k:
                new_read = (self.write_idx - k) % self.capacity
 
            self.read_idx = new_read
 
            # 7. Extraheer venster [read_idx, read_idx + k)
            output = self._extract(self.read_idx, k)
            return output, step

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _extract(self, start: int, length: int) -> np.ndarray:
        end = (start + length) % self.capacity
        if start < end:
            return self.buffer[start:end].copy()
        return np.concatenate((self.buffer[start:], self.buffer[:end]), axis=0)

    @property
    def current_step(self) -> int:
        return int(round(self._step_f))

    @property
    def lag_samples(self) -> int:
        end_of_window = (self.read_idx) % self.capacity
        return int((self.write_idx - end_of_window) % self.capacity)
    

    def reset(self):
        with self.lock:
            self.write_idx = 0
            self.read_idx  = 0
            self.filled    = 0
            self._step_f   = float(IDEAL_STEP)
            self.buffer.fill(0)
            
            
            

"""
import numpy as np
import threading

# ── Constanten ────────────────────────────────────────────────────────────────
from settings.settings import SAMPLE_RATE, REFRESH_FPS

IDEAL_STEP = (SAMPLE_RATE // REFRESH_FPS)*2


# ── Startup ───────────────────────────────────────────────────────────────────
STARTUP_MS  = 50
STARTUP_MIN = int(SAMPLE_RATE * STARTUP_MS / 1000)


# ── PI controller parameters ─────────────────────────────────────────────────

# Doel: einde leesvenster volgt write_idx
DESIRED_LAG = 600


# Proportionele versterking:
# hogere waarde = sneller reageren
PI_KP = 0.005


# Integrale versterking:
# hogere waarde = sneller structurele drift corrigeren
PI_KI = 0.00002


# Anti windup grenzen
INTEGRAL_MIN = -50000
INTEGRAL_MAX = 50000


# ── Step grenzen ──────────────────────────────────────────────────────────────

MIN_STEP = max(1, IDEAL_STEP // 4)
MAX_STEP = IDEAL_STEP * 4


# Maximale verandering per frame
# voorkomt zichtbare sprongen
MAX_STEP_DELTA = 8



class ProcessedBuffer:



    def __init__(
        self,
        capacity: int,
        channels: int = 2,
        dtype=np.int16
    ):

        self.capacity = int(capacity)
        self.channels = int(channels)
        self.dtype = dtype
        #self.log = []


        self.buffer = np.zeros(
            (self.capacity, self.channels),
            dtype=self.dtype
        )


        self.write_idx = 0
        self.read_idx = 0
        self.filled = 0


        # huidige step (float voor vloeiende regeling)
        self._step_f = float(IDEAL_STEP)


        # PI integrator
        self._integral = 0.0


        self.lock = threading.Lock()



    # ── Write ─────────────────────────────────────────────────────────────────

    def write(self, samples: np.ndarray):


        if (
            samples.ndim != 2
            or samples.shape[1] != self.channels
        ):
            raise ValueError(
                f"Expected shape (N,{self.channels}), got {samples.shape}"
            )


        n = len(samples)


        with self.lock:

            first = min(
                self.capacity - self.write_idx,
                n
            )


            self.buffer[
                self.write_idx:
                self.write_idx + first
            ] = samples[:first]


            remaining = n - first


            if remaining > 0:
                self.buffer[:remaining] = samples[first:]


            self.write_idx = (
                self.write_idx + n
            ) % self.capacity


            self.filled = min(
                self.capacity,
                self.filled + n
            )



    # ── Read ──────────────────────────────────────────────────────────────────

    def read(
        self,
        n: int,
        nominal_step: int = IDEAL_STEP
    ):


        with self.lock:
            distance = (
                self.write_idx - self.read_idx
            ) % self.capacity
            distance = distance - 36000

            #self.log.append(distance)


            # startup bescherming
            if self.filled < STARTUP_MIN:
                return None, IDEAL_STEP



            # venster mag niet groter zijn dan beschikbare data
            k = min(
                n,
                self.filled
            )



            # einde huidige venster
            end_of_window = (
                self.read_idx + k
            ) % self.capacity



            # actuele achterstand
            lag = int(
                (
                    self.write_idx
                    - end_of_window
                )
                % self.capacity
            )



            # ───────────────────────────────────────────────
            # PI controller
            # ───────────────────────────────────────────────

            error = lag - DESIRED_LAG



            # integrator update
            self._integral += error


            # anti windup
            self._integral = float(
                np.clip(
                    self._integral,
                    INTEGRAL_MIN,
                    INTEGRAL_MAX
                )
            )



            correction = (
                PI_KP * error
                +
                PI_KI * self._integral
            )


            target_step = (
                nominal_step
                +
                correction
            )



            # ───────────────────────────────────────────────
            # Slew limiter + step begrenzing
            # ───────────────────────────────────────────────

            delta = np.clip(
                target_step - self._step_f,
                -MAX_STEP_DELTA,
                MAX_STEP_DELTA
            )


            candidate = (
                self._step_f
                + delta
            )


            limited = np.clip(
                candidate,
                MIN_STEP,
                MAX_STEP
            )



            # anti windup:
            # uitgang zit tegen limiet
            if limited != candidate:

                self._integral *= 0.90



            self._step_f = float(limited)


            step = int(
                round(self._step_f)
            )



            # ───────────────────────────────────────────────
            # Nieuwe leespositie
            # ───────────────────────────────────────────────

            new_read = (
                self.read_idx
                + step
            ) % self.capacity



            # nooit voorbij write_idx lopen
            available = int(
                (
                    self.write_idx
                    - new_read
                )
                % self.capacity
            )



            if available < k:

                new_read = (
                    self.write_idx
                    - k
                ) % self.capacity


            step_idx = (new_read - self.read_idx) % self.capacity
            self.read_idx = new_read


            output = self._extract(
                self.read_idx,
                k
            )

            return output, step_idx



    # ── Extract helper ────────────────────────────────────────────────────────

    def _extract(
        self,
        start: int,
        length: int
    ) -> np.ndarray:


        end = (
            start + length
        ) % self.capacity



        if start < end:

            return self.buffer[
                start:end
            ].copy()



        return np.concatenate(
            (
                self.buffer[start:],
                self.buffer[:end]
            ),
            axis=0
        )



    # ── Diagnostics ───────────────────────────────────────────────────────────

    @property
    def current_step(self):

        return int(
            round(self._step_f)
        )


    @property
    def lag_samples(self):

        end_of_window = (
            self.read_idx
        ) % self.capacity


        return int(
            (
                self.write_idx
                - end_of_window
            )
            % self.capacity
        )



    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self):

        with self.lock:
            #self.log = []

            self.write_idx = 0
            self.read_idx = 0
            self.filled = 0

            self._step_f = float(
                IDEAL_STEP
            )

            self._integral = 0.0

            self.buffer.fill(0)
            
    def get_read_index(self):
        with self.lock:
            return self.read_idx
