"""
MechDrive AI Q-Learning — Configuration & Hyperparameters
=========================================================
BẢN ĐẶC TẢ CHÍNH THỨC — khớp 100% tài liệu kỹ thuật.
Mọi giá trị rời rạc, hệ số, hằng số đều lấy từ spec.

5 biến State × 5 biến Action → 1 Agent duy nhất.
"""

import os
import json
import math
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
LOOKUP_DIR = BASE_DIR / "lookup_tables"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ══════════════════════════════════════════════════════════════════════
# HYPERPARAMETERS (Phần IV - Spec)
# ══════════════════════════════════════════════════════════════════════
EPOCHS = 1_000_000          # Số vòng lặp train
ALPHA = 0.1                 # Learning rate (α)
GAMMA = 0.0                 # Discount factor (γ = 0: bài toán 1 bước, không chuỗi)
EPSILON_START = 1.0          # ε ban đầu (khám phá 100%)
EPSILON_END = 0.01           # ε tối thiểu
# Decay tuyến tính: ε giảm đều từ 1.0 → 0.01 trong EPOCHS vòng
EPSILON_LINEAR_DECAY = True  # True = tuyến tính, False = exponential

# Evaluation checkpoint: đánh giá mô hình mỗi N epochs
EVAL_EVERY = 10_000
# Log progress mỗi N epochs
LOG_EVERY = 5_000

# ══════════════════════════════════════════════════════════════════════
# STATE SPACE (Phần I.1 - Spec) — 5 biến, 3024 states
# ══════════════════════════════════════════════════════════════════════
P_YC_BINS = [1, 2, 3, 5, 7, 10, 15]                  # kW (7)
N_YC_BINS = [50, 75, 100, 120, 150, 200]              # v/p (6)
U_TOTAL_BINS = [5, 8, 10, 12.5, 15, 20]               # tỉ số truyền tổng (6)
LH_BINS = [5000, 10000, 15000, 20000]                  # giờ tuổi thọ (4)
LOAD_TYPES = [0, 1, 2]                                 # 0=Tĩnh, 1=Va đập nhẹ, 2=Va đập mạnh (3)
LOAD_TYPE_NAMES = {0: "Tĩnh", 1: "Va_đập_nhẹ", 2: "Va_đập_mạnh"}

TOTAL_STATES = len(P_YC_BINS) * len(N_YC_BINS) * len(U_TOTAL_BINS) * len(LH_BINS) * len(LOAD_TYPES)
# = 7 × 6 × 6 × 4 × 3 = 3024

# ══════════════════════════════════════════════════════════════════════
# ACTION SPACE (Phần I.2 - Spec) — 5 biến, 1 agent
# ══════════════════════════════════════════════════════════════════════
UD_VALUES = [1.25, 1.6, 2.0, 2.5, 3.15, 4.0, 5.0, 6.3]     # u_d (8)
PSI_BA_VALUES = [0.2, 0.25, 0.315, 0.4, 0.5]                  # ψ_ba (5)

# matID: mã vật liệu đại diện
# "3" = Thép 45 (tôi cải thiện, phổ thông)
# "7" = Thép 40X (tôi cải thiện, trung cấp)
# "8" = Thép 40X (tôi cải thiện s≤60, cứng hơn)
# "19" = Thép 20X (thấm cacbon, cao cấp)
# "13" = Thép 40XH (tôi cải thiện, cao cấp)
MAT_IDS = ["3", "7", "8", "13", "19"]                         # matID (5)
EXPENSIVE_MATS = {"19", "13"}  # Thép đắt tiền

GEAR_TYPES = ["rang_thang", "rang_nghieng"]                    # gear_type (2)

Z1_CHAIN_VALUES = [19, 21, 23, 25, 27]                         # z₁ xích (5)

TOTAL_ACTIONS = (len(UD_VALUES) * len(PSI_BA_VALUES) * len(MAT_IDS)
                 * len(GEAR_TYPES) * len(Z1_CHAIN_VALUES))
# = 8 × 5 × 5 × 2 × 5 = 2000

# Q-Table size: 3024 × 2000 = 6,048,000 ô

# ══════════════════════════════════════════════════════════════════════
# MECHANICAL CONSTANTS
# ══════════════════════════════════════════════════════════════════════
# Hiệu suất thành phần
ETA_CHAIN = 0.96            # Bộ truyền xích
ETA_GEAR_CON = 0.97         # BR côn
ETA_GEAR_TRU = 0.97         # BR trụ
ETA_OL = 0.99               # Ổ lăn (1 cặp)
ETA_KHOP = 0.99             # Khớp nối
NUM_OL_PAIRS = 4            # 3 trục → 3-4 cặp ổ lăn
ETA_TOTAL = ETA_CHAIN * ETA_GEAR_CON * ETA_GEAR_TRU * (ETA_OL ** NUM_OL_PAIRS) * ETA_KHOP

# Sơ đồ bố trí (bảng 6.4) — mặc định sơ đồ 3 cho HGT côn-trụ
SCHEME_NUMBER = 3
# Cấp chính xác TCVN 1067-71 — mặc định cấp 8
ACCURACY_GRADE = 8

# Hệ số K_a (Công thức tính a_w sơ bộ)
KA_RANG_THANG = 49.5
KA_RANG_NGHIENG = 43.0

# Hệ số vật liệu (thép-thép)
ZM = 274.0        # MPa^(1/2)
# Z_H và Z_epsilon: TÍNH TỪ CÔNG THỨC trong formulas.py (không hardcode)

# Hệ số an toàn tối thiểu
SH_MIN = 1.1       # Bền tiếp xúc
SF_MIN = 1.75       # Bền uốn

# δ_H cho tính K_Hv (Bảng 6.15 - Trịnh Chất)
DELTA_H_THANG = 0.006     # Răng thẳng
DELTA_H_NGHIENG = 0.002   # Răng nghiêng

# δ_F cho tính K_Fv (Bảng 6.15 - Trịnh Chất) — GIÁ TRỊ RIÊNG, KHÔNG PHẢI δ_H×1.5
DELTA_F_THANG = 0.016      # Răng thẳng
DELTA_F_NGHIENG = 0.006    # Răng nghiêng


# ══════════════════════════════════════════════════════════════════════
# REWARD CONSTANTS (Phần III - Spec) — 3 cửa ải
# ══════════════════════════════════════════════════════════════════════
R_UNDERCUT = -2000              # Cửa 1: Cắt chân răng (z < z_min)
R_STRENGTH_BASE = -1000         # Cửa 2: Vi phạm sức bền (× max(S_H, S_F))
R_VOLUME_SCALE = 5e7            # Cửa 3: R_vol = 5×10⁷ / (a_w² × b_w)
R_SWEET_SPOT_BONUS = 500        # Bonus: 0.90 ≤ S_H ≤ 0.98
R_OVER_DESIGN_PENALTY = -200    # Phạt: S_H < 0.80 (over-engineering)
R_WASTE_MATERIAL_PENALTY = -300 # Phạt: thép đắt + S_H < 0.75

# ══════════════════════════════════════════════════════════════════════
# CHAIN CONSTANTS
# ══════════════════════════════════════════════════════════════════════
CHAIN_SAFETY_ALLOWED = 7.6     # [s] cho phép
CHAIN_IMPACT_ALLOWED = 25      # [i] cho phép (lần/s)

# ══════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════

def load_json(filename: str) -> dict | list:
    """Load a JSON lookup table."""
    filepath = LOOKUP_DIR / filename
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def discretize(value: float, bins: list[float]) -> float:
    """Snap a continuous value to the nearest bin."""
    return min(bins, key=lambda b: abs(b - value))


def state_to_key(P: float, n: float, u_total: float,
                 Lh: float, load: int) -> str:
    """
    Convert 5-tuple state to string key for Q-Table.
    Rời rạc hóa mỗi biến về bin gần nhất trước khi tạo key.
    """
    P_d = discretize(P, P_YC_BINS)
    n_d = discretize(n, N_YC_BINS)
    u_d = discretize(u_total, U_TOTAL_BINS)
    Lh_d = discretize(Lh, LH_BINS)
    return f"{P_d}|{n_d}|{u_d}|{Lh_d}|{load}"


def action_to_key(ud: float, psi_ba: float, matID: str,
                  gear_type: str, z1_chain: int) -> str:
    """Convert 5-tuple action to string key."""
    return f"{ud}|{psi_ba}|{matID}|{gear_type}|{z1_chain}"


def key_to_action(key: str) -> dict:
    """Parse action key back to dict."""
    parts = key.split("|")
    return {
        "optimal_ud": float(parts[0]),
        "optimal_psi_ba": float(parts[1]),
        "matID": parts[2],
        "gear_type": parts[3],
        "z1_chain": int(parts[4]),
    }


def key_to_state(key: str) -> dict:
    """Parse state key back to dict."""
    parts = key.split("|")
    return {
        "P_yc": float(parts[0]),
        "n_yc": float(parts[1]),
        "u_total": float(parts[2]),
        "L_h": float(parts[3]),
        "load_type": int(parts[4]),
    }
