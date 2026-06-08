class BLEStressConfig:

    def __init__(self,
        # =========================
        # JITTER
        # =========================
        enable_jitter=True,
        jitter_ms_std=100,

        # =========================
        # PACKET LOSS
        # =========================
        enable_packet_loss=True,
        packet_loss_prob=0.01,

        # =========================
        # BURST (micro congestion)
        # =========================
        enable_burst=True,
        burst_prob=0.02,
        burst_delay_ms=(5, 30),

        # =========================
        # STALL (BLE freeze events)
        # =========================
        enable_stall=True,
        stall_prob=0.01,
        stall_ms=(50, 200),

        # =========================
        # QUEUE / CONGESTION
        # =========================
        enable_congestion=True,
        max_queue_size=10,
        flush_threshold=3,

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