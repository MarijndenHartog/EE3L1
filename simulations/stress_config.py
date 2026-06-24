class BLEStressConfig:

    def __init__(self,
        # =========================
        # JITTER
        # =========================
        enable_jitter=False,
        jitter_ms_std=3,

        # =========================
        # PACKET LOSS
        # =========================
        enable_packet_loss=False,
        packet_loss_prob=0.01,

        # =========================
        # BURST (micro congestion)
        # =========================
        enable_burst=False,
        burst_prob=0.02,
        burst_delay_ms=(5, 30),

        # =========================
        # STALL (BLE freeze events)
        # =========================
        enable_stall=False,
        stall_prob=0.01,
        stall_ms=(100, 200),

        # =========================
        # QUEUE / CONGESTION
        # =========================
        enable_congestion=False,
        congestion_prob = 0.005,
        flush_threshold=3,
        
        max_queue_size = 100,

        congested_rate_min = 0.0,
        congested_rate_max = 0.4,

        recovery_rate_min = 1.0,
        recovery_rate_max = 4.0,



        # =========================
        # SIGNAL QUALITY
        # =========================
        noise_level=300,
    ):
        self.enable_jitter = enable_jitter
        self.jitter_ms_std = jitter_ms_std

        self.enable_packet_loss = enable_packet_loss
        self.packet_loss_prob = packet_loss_prob

        self.enable_burst = enable_burst
        self.burst_prob = burst_prob
        self.burst_delay_ms = burst_delay_ms

        self.enable_stall = enable_stall
        self.stall_prob = stall_prob
        self.stall_ms = stall_ms

        self.enable_congestion = enable_congestion
        self.max_queue_size = max_queue_size
        self.flush_threshold = flush_threshold

        self.noise_level = noise_level
        
        self.congested_rate_min = congested_rate_min 
        self.congested_rate_max = congested_rate_max

        self.recovery_rate_min = recovery_rate_min
        self.recovery_rate_max = recovery_rate_max 
        self.congestion_prob = congestion_prob