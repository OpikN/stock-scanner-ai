# =========================
# ACCOUNT CONFIG
# =========================
INITIAL_BALANCE = 100_000_000  # 100 juta


# =========================
# RISK MANAGEMENT
# =========================
RISK_SAFE = 0.01        # 1% risk per trade
RISK_AGGRESSIVE = 0.03  # 3% risk per trade


# =========================
# BASIC TRADE PARAMETER
# =========================
SL_PERCENT = 0.02   # 2% stop loss
TP_PERCENT = 0.04   # fallback TP


# =========================
# ADVANCED TRADE MANAGEMENT 🔥
# =========================
TP1_PERCENT = 0.02           # partial close (50%)
TP2_PERCENT = 0.04           # final TP
BREAK_EVEN_TRIGGER = 0.015   # pindah SL ke entry
TRAILING_PERCENT = 0.01      # trailing stop 1%
PARTIAL_CLOSE_RATIO = 0.5    # 50% close


# =========================
# POSITION SIZING 🔥
# =========================
MAX_OPEN_POSITIONS = 5
MIN_TRADE_SIZE = 100_000     # minimal 100rb


# =========================
# AI MODE SWITCH
# =========================
MODE_SAFE = "SAFE"
MODE_AGGRESSIVE = "AGGRESSIVE"
MODE_SCALP = "SCALP"
