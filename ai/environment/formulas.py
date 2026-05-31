"""
MechDrive AI — Physics Engine (Formulas)
==========================================
Cong thuc co hoc chinh xac theo Trinh Chat - Le Van Uyen.
Khop 100% "Ban ve thiet ke Luong API va Ma tran Cong thuc".

Pipeline: T1 -> a_w -> m -> z -> b_w -> v -> K_v -> sigma_H, sigma_F

CUM 1: Truyen dong hoc tong the
CUM 2: Hinh hoc banh rang
CUM 3: Ung suat tiep xuc (sigma_H)
CUM 4: Ung suat uon (sigma_F)
CUM 5: Truyen dong xich
"""

import math
import json
from pathlib import Path

from config import (
    KA_RANG_THANG, KA_RANG_NGHIENG, ZM,
    DELTA_H_THANG, DELTA_H_NGHIENG,
    DELTA_F_THANG, DELTA_F_NGHIENG,
    SH_MIN, SF_MIN,
)

# ── Load lookup tables ─────────────────────────────────────────────────
_LOOKUP_DIR = Path(__file__).parent.parent / "lookup_tables"


def _load(name: str):
    with open(_LOOKUP_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


_MATERIALS = {m["matID"]: m for m in _load("std_material.json")}
_MODULES = sorted([m["modVal"] for m in _load("std_module.json")])
_AW_VALUES = sorted([a["awValue"] for a in _load("std_center_distance.json")])
_MOTORS = _load("std_motor.json")
_CHAINS = _load("std_chain.json")
_K_HBETA = _load("k_hbeta.json")
_K_FBETA = _load("k_fbeta.json")
_K_HALPHA = _load("k_halpha.json")
_K_FALPHA = _load("k_falpha.json")
_YF_TABLE = _load("y_f_table.json")   # Bang 6.18: Y_F theo z_v (x=0)
_G0_TABLE = _load("g0_table.json")    # Bang 6.16: g0 theo cap CX va loai rang


# ══════════════════════════════════════════════════════════════════════
# HELPER: Lam tron tieu chuan
# ══════════════════════════════════════════════════════════════════════

def snap_up(value: float, std_list: list[float]) -> float:
    """Lam tron LEN den gia tri tieu chuan gan nhat >= value. KHONG dung sai."""
    for s in sorted(std_list):
        if s >= value:
            return s
    raise ValueError(f"snap_up: {value:.2f} vuot moi gia tri tieu chuan TCVN")


def snap_nearest(value: float, std_list: list[float]) -> float:
    """Lay gia tri tieu chuan gan nhat."""
    return min(std_list, key=lambda s: abs(s - value))


def snap_down_module(value: float) -> float:
    """Chon modun tieu chuan: lay gia tri <= value (an toan hon -> nhieu rang hon)."""
    candidates = [m for m in _MODULES if m <= value * 1.05]
    return max(candidates) if candidates else _MODULES[0]


def interpolate_yf(z_v: float) -> float:
    """
    Noi suy tuyen tinh Y_F tu Bang 6.18 (Trinh Chat).
    Neu z_v nam ngoai bang, clamp ve moc gan nhat.
    """
    # Parse keys thanh sorted float list
    keys = sorted([float(k) for k in _YF_TABLE.keys()])
    vals = [_YF_TABLE[str(int(k))] for k in keys]

    # Clamp bien
    if z_v <= keys[0]:
        return vals[0]
    if z_v >= keys[-1]:
        return vals[-1]

    # Tim 2 moc kep
    for i in range(len(keys) - 1):
        if keys[i] <= z_v <= keys[i + 1]:
            # Noi suy tuyen tinh: Y_F = Y1 + (Y2 - Y1) * (z_v - z1) / (z2 - z1)
            t = (z_v - keys[i]) / (keys[i + 1] - keys[i])
            return vals[i] + t * (vals[i + 1] - vals[i])

    return vals[-1]  # Fallback


def lookup_g0(grade: int, is_nghieng: bool) -> float:
    """
    Tra g0 tu Bang 6.16 (Trinh Chat) theo cap chinh xac va loai rang.
    Grade: 6, 7, 8, 9
    """
    grade_str = str(grade)
    if grade_str not in _G0_TABLE:
        grade_str = "8"  # Mac dinh cap 8 neu sai
    gear_key = "Răng nghiêng" if is_nghieng else "Răng thẳng"
    return _G0_TABLE[grade_str].get(gear_key, 73)


# ══════════════════════════════════════════════════════════════════════
# MATERIAL
# ══════════════════════════════════════════════════════════════════════

def get_material(matID: str) -> dict:
    return _MATERIALS.get(matID, _MATERIALS["7"])


def is_hardened(mat: dict) -> bool:
    """HB > 350 -> tham / toi cung."""
    return mat["hardnessHB_min"] > 350


def sigma_H_allowed(mat: dict, K_HL: float = 1.0, S_H: float = SH_MIN) -> float:
    """[sigma_H] = sigma_Hlim * K_HL / S_H"""
    return mat["sigmaHlim_base"] * K_HL / S_H


def sigma_F_allowed(mat: dict, K_FL: float = 1.0, S_F: float = SF_MIN) -> float:
    """[sigma_F] = sigma_Flim * K_FL / S_F"""
    return mat["sigmaFlim_base"] * K_FL / S_F


def compute_KHL(L_h: float, HB: float, n_gear: float) -> float:
    """
    He so tuoi tho tiep xuc K_HL.
    K_HL = (N_HO / N_HE)^(1/6)  khi N_HE < N_HO
    N_HO = 30 * HB^2.4
    N_HE = 60 * c * n_gear * L_h  (c=1 cho 1 doi rang an khop)
    Neu N_HE >= N_HO -> K_HL = 1
    """
    N_HO = 30 * (HB ** 2.4)
    N_HE = 60 * 1 * n_gear * L_h
    if N_HE >= N_HO:
        return 1.0
    return min((N_HO / N_HE) ** (1.0 / 6.0), 2.5)


def compute_KFL(L_h: float, HB: float, n_gear: float) -> float:
    """
    He so tuoi tho uon K_FL.
    K_FL = (N_FO / N_FE)^(1/6)
    N_FO = 4e6 (cho tat ca loai thep)
    N_FE = 60 * c * n_gear * L_h
    """
    N_FO = 4e6
    N_FE = 60 * 1 * n_gear * L_h
    if N_FE >= N_FO:
        return 1.0
    return min((N_FO / N_FE) ** (1.0 / 6.0), 2.5)


# ══════════════════════════════════════════════════════════════════════
# Z_H, Z_epsilon: TINH THEO CONG THUC (khong hardcode)
# ══════════════════════════════════════════════════════════════════════

def compute_ZH(beta_rad: float, alpha_tw_rad: float = math.radians(20)) -> float:
    """
    He so hinh dang be mat tiep xuc:
    Z_H = sqrt(2 * cos(beta_b) / sin(2 * alpha_tw))
    
    beta_b: goc nghieng tren mat tru co so
    tan(beta_b) = tan(beta) * cos(alpha_tw)
    alpha_tw: goc an khop mat dau (mac dinh 20 do)
    """
    # Goc nghieng tren mat tru co so
    tan_beta_b = math.tan(beta_rad) * math.cos(alpha_tw_rad)
    beta_b = math.atan(tan_beta_b)
    cos_beta_b = math.cos(beta_b)
    
    sin_2alpha = math.sin(2 * alpha_tw_rad)
    if sin_2alpha <= 0:
        raise ValueError(f"Goc an khop phi vat ly: sin(2*alpha_tw) = {sin_2alpha:.6f} <= 0")
    
    return math.sqrt(2 * cos_beta_b / sin_2alpha)


def compute_Z_epsilon(z1: int, z2: int, beta_rad: float) -> float:
    """
    He so trung khop Z_epsilon.
    
    1. Tinh he so trung khop ngang:
       epsilon_alpha = [1.88 - 3.2*(1/z1 + 1/z2)] * cos(beta)
       
    2. Neu rang thang (beta=0):
       Z_epsilon = sqrt((4 - epsilon_alpha) / 3)
       
    3. Neu rang nghieng (beta>0):
       Z_epsilon = sqrt(1 / epsilon_alpha)
    """
    cos_beta = math.cos(beta_rad)
    
    epsilon_alpha = (1.88 - 3.2 * (1.0 / z1 + 1.0 / z2)) * cos_beta
    epsilon_alpha = max(1.0, epsilon_alpha)  # gioi han duoi = 1.0
    
    if beta_rad < math.radians(1):  # rang thang
        return math.sqrt((4 - epsilon_alpha) / 3)
    else:  # rang nghieng
        return math.sqrt(1.0 / epsilon_alpha)


# ══════════════════════════════════════════════════════════════════════
# K_Hbeta, K_Fbeta, K_Halpha, K_Falpha LOOKUP (noi suy)
# ══════════════════════════════════════════════════════════════════════

def _interpolate_k_beta(table_data: dict, psi_bd: float,
                        scheme: int, is_hard: bool) -> float:
    """Noi suy K_Hbeta hoac K_Fbeta tu bang 6.4."""
    key = "HB_gt_350" if is_hard else "HB_le_350"
    data = table_data[key]
    scheme_idx = scheme - 1

    psi_bd = max(0.2, min(1.6, psi_bd))
    psi_keys = sorted([float(k) for k in data.keys()])
    lower = max([p for p in psi_keys if p <= psi_bd], default=psi_keys[0])
    upper = min([p for p in psi_keys if p >= psi_bd], default=psi_keys[-1])

    def get_val(pk):
        vals = data[str(pk)]
        return vals[scheme_idx] if scheme_idx < len(vals) else None

    v_low, v_up = get_val(lower), get_val(upper)
    if v_low is None and v_up is None:
        raise KeyError(f"K_beta: khong co du lieu cho psi_bd={psi_bd:.3f}, scheme={scheme}")
    if v_low is None:
        if v_up is None:
            raise KeyError(f"K_beta: du lieu bang tra thieu cho psi_bd={psi_bd:.3f}")
        return v_up
    if v_up is None:
        return v_low
    if abs(upper - lower) < 1e-9:
        return v_low
    return v_low + (psi_bd - lower) / (upper - lower) * (v_up - v_low)


def lookup_K_Hbeta(psi_ba: float, u_d: float, scheme: int, is_hard: bool) -> float:
    psi_bd = psi_ba * (u_d + 1) / 2
    return _interpolate_k_beta(_K_HBETA, psi_bd, scheme, is_hard)


def lookup_K_Fbeta(psi_ba: float, u_d: float, scheme: int, is_hard: bool) -> float:
    psi_bd = psi_ba * (u_d + 1) / 2
    return _interpolate_k_beta(_K_FBETA, psi_bd, scheme, is_hard)


def _lookup_k_alpha_val(table_data: dict, grade: int, v_ms: float) -> float:
    grade_key = f"grade_{grade}"
    if grade_key not in table_data:
        grade_key = "grade_8"
    data = table_data[grade_key]
    v_keys = sorted([float(k) for k in data.keys()])
    v_ms = max(v_keys[0], min(v_keys[-1], v_ms))
    lower = max([v for v in v_keys if v <= v_ms], default=v_keys[0])
    upper = min([v for v in v_keys if v >= v_ms], default=v_keys[-1])

    def try_get(k):
        for fmt in [str(k), f"{k:.1f}", str(int(k)) if k == int(k) else None]:
            if fmt and fmt in data:
                return data[fmt]
        return None

    v_low, v_up = try_get(lower), try_get(upper)
    if v_low is None and v_up is None:
        raise KeyError(f"K_alpha: khong co du lieu cho grade={grade}, v={v_ms:.3f} m/s")
    if v_low is None:
        if v_up is None:
            raise KeyError(f"K_alpha: du lieu bang tra thieu cho grade={grade}")
        return v_up
    if v_up is None:
        return v_low
    if abs(upper - lower) < 1e-9:
        return v_low
    return v_low + (v_ms - lower) / (upper - lower) * (v_up - v_low)


def lookup_K_Halpha(grade: int, v_ms: float) -> float:
    return _lookup_k_alpha_val(_K_HALPHA, grade, v_ms)


def lookup_K_Falpha(grade: int, v_ms: float) -> float:
    return _lookup_k_alpha_val(_K_FALPHA, grade, v_ms)


# ══════════════════════════════════════════════════════════════════════
# MOTOR SELECTION
# ══════════════════════════════════════════════════════════════════════

def select_motor(P_ct: float, n_sb: float) -> dict | None:
    """Chon dong co: P_dm >= P_ct, n_dm gan n_sb nhat."""
    candidates = [m for m in _MOTORS if m["P_dm"] >= P_ct]
    if not candidates:
        return None
    candidates.sort(key=lambda m: (abs(m["n_dm"] - n_sb), m["P_dm"]))
    return candidates[0]


# ══════════════════════════════════════════════════════════════════════
# GEAR DESIGN — 5 CUM CONG THUC
# ══════════════════════════════════════════════════════════════════════

def gear_design(P_yc: float, n_yc: float, u_total: float, L_h: float,
                load_type: int, u_d: float, psi_ba: float, matID: str,
                gear_type: str, scheme: int = 3, grade: int = 8) -> dict:
    """
    Tinh toan banh rang day du theo spec.
    Tra ve dict voi MOI bien trung gian.
    
    CUM 1: Truyen dong hoc -> T1
    CUM 2: Hinh hoc -> a_w, m, z, b_w, d_w1
    CUM 3: Ung suat tiep xuc -> sigma_H (voi Z_H, Z_epsilon tinh theo CT)
    CUM 4: Ung suat uon -> sigma_F (voi Y_F, Y_beta, z_v)
    """
    mat = get_material(matID)
    is_hard = is_hardened(mat)
    HB_avg = (mat["hardnessHB_max"] + mat["hardnessHB_min"]) / 2

    is_nghieng = (gear_type == "rang_nghieng")

    # ══════════════════════════════════════════════════════════════════
    # CUM 1: TRUYEN DONG HOC TONG THE
    # ══════════════════════════════════════════════════════════════════
    # u_x = u_total / u_d (ti so truyen xich)
    u_x = u_total / u_d

    # Nếu sơ đồ là: Động cơ -> Hộp số -> Xích -> Tải
    n_gear = n_yc * u_total  # (Vòng quay trục I = vòng quay động cơ)
    
    # HOẶC Nếu sơ đồ là: Động cơ -> Xích -> Hộp số -> Tải
    # n_gear = n_yc * u_d
    if n_gear <= 0 or u_total <= 0:
        return _fail("n_gear <= 0")

    # He so tuoi tho (su dung n_gear thuc te, KHONG gan cuong n_est=300)
    K_HL = compute_KHL(L_h, HB_avg, n_gear)
    K_FL = compute_KFL(L_h, HB_avg, n_gear)

    sig_H_allow = sigma_H_allowed(mat, K_HL)
    sig_F_allow = sigma_F_allowed(mat, K_FL)
    
    # T1 = 9.55 * 10^6 * P_yc / n_1  (N.mm)
    T1 = 9.55e6 * P_yc / n_gear

    # ══════════════════════════════════════════════════════════════════
    # CUM 2: HINH HOC BANH RANG
    # ══════════════════════════════════════════════════════════════════
    
    # Ka: hang so vat lieu
    K_a = KA_RANG_NGHIENG if is_nghieng else KA_RANG_THANG
    
    # K_Hbeta: he so tap trung tai (tra bang 6.4)
    K_Hbeta = lookup_K_Hbeta(psi_ba, u_d, scheme, is_hard)
    K_Fbeta = lookup_K_Fbeta(psi_ba, u_d, scheme, is_hard)

    # --- 2.1 Khoang cach truc so bo ---
    # a_w = K_a * (u_d + 1) * cbrt(T1 * K_Hbeta / ([sigma_H]^2 * u_d * psi_ba))
    inner = T1 * K_Hbeta / (sig_H_allow ** 2 * u_d * psi_ba)
    if inner <= 0:
        return _fail("inner <= 0")
    a_w_calc = K_a * (u_d + 1) * (inner ** (1.0 / 3.0))
    
    # BAT BUOC: lam tron len day tieu chuan
    a_w = snap_up(a_w_calc, _AW_VALUES)

    # --- 2.2 Mo-dun phap (m) ---
    # Loc module tieu chuan trong khoang [0.01*a_w, 0.02*a_w] (Bang 6.8)
    m_min_range = 0.01 * a_w
    m_max_range = 0.02 * a_w
    valid_modules = [mod for mod in _MODULES if m_min_range <= mod <= m_max_range]

    if not valid_modules:
        raise ValueError(f"Khong tim thay mo-dun TCVN trong [{m_min_range:.3f}, {m_max_range:.3f}] voi a_w={a_w}")

    # Chon module NHO NHAT (SGK Trinh Chat: uu tien nhieu rang, tang do em)
    m = valid_modules[0]
    m_calc = (m_min_range + m_max_range) / 2  # Gia tri tinh toan (trung binh khoang)

    # --- 2.3 So rang z1, z2 va goc nghieng beta ---
    if is_nghieng:
        # Gioi han goc nghieng: beta in [8°, 20°]
        cos_beta_upper = math.cos(math.radians(8))   # ~0.9903
        cos_beta_lower = math.cos(math.radians(20))  # ~0.9397

        # Kep tong so rang z_t vao 2 can tu gioi han beta
        zt_min = math.ceil(2 * a_w * cos_beta_lower / m)
        zt_max = math.floor(2 * a_w * cos_beta_upper / m)

        if zt_min > zt_max:
            return _fail("Cannot form helical angle within 8-20 degrees")

        # Uu tien so rang lon nhat (tang he so trung khop, chay em)
        z_total = zt_max
        z1 = max(1, round(z_total / (u_d + 1)))
        z2 = round(z1 * u_d)
        z_t = z1 + z2

        # Tinh CHINH XAC cos_beta tu z_t da chot (back-calculate)
        cos_beta = m * z_t / (2 * a_w)
        cos_beta = max(cos_beta_lower, min(cos_beta_upper, cos_beta))
        beta_rad = math.acos(cos_beta)
        beta_deg = math.degrees(beta_rad)
    else:
        # Rang thang: z_t = round(2*a_w / m), roi tinh lai a_w thuc te
        z_total = round(2 * a_w / m)
        z1 = max(1, round(z_total / (u_d + 1)))
        z2 = round(z1 * u_d)
        z_t = z1 + z2

        # Tinh lai a_w thuc te tu z_t va m
        # (rang thang khong co cos_beta de hap thu so le)
        a_w = m * z_t / 2.0

        cos_beta = 1.0
        beta_rad = 0.0
        beta_deg = 0.0

    # Ti so truyen thuc: u_m = z2 / z1
    u_m = z2 / z1 if z1 > 0 else u_d

    # --- 2.4 Kich thuoc thuc te ---
    # Be rong vanh rang: b_w = psi_ba * a_w
    b_w = psi_ba * a_w
    
    # Duong kinh vong lan:
    # d_w1 = 2 * a_w / (u_m + 1)
    d_w1 = 2 * a_w / (u_m + 1)
    d_w2 = 2 * a_w * u_m / (u_m + 1)

    # ══════════════════════════════════════════════════════════════════
    # CUM 3: UNG SUAT TIEP XUC (sigma_H)
    # sigma_H = Z_M * Z_H * Z_epsilon * sqrt(2*T1*K_H*(u_m+1) / (b_w*u_m*d_w1^2))
    # ══════════════════════════════════════════════════════════════════
    
    # Van toc vong: v = pi * d_w1 * n1 / 60000 (m/s)
    n1 = n_gear
    v = math.pi * d_w1 * n1 / 60000

    # K_Halpha, K_Falpha (tra theo cap chinh xac va van toc)
    K_Halpha = lookup_K_Halpha(grade, v)
    K_Falpha = lookup_K_Falpha(grade, v)

    # --- K_Hv (he so tai trong dong - PHUC TAP NHAT) ---
    # v_H = delta_H * g_0 * v * sqrt(a_w / u_m)
    # delta_H: rang thang = 0.006, rang nghieng = 0.002
    # g_0: tra Bang 6.16 theo cap chinh xac va loai rang
    delta_H = DELTA_H_NGHIENG if is_nghieng else DELTA_H_THANG
    g0 = lookup_g0(grade, is_nghieng)
    v_H = delta_H * g0 * v * math.sqrt(a_w / u_m) if u_m > 0 else 0

    # K_Hv = 1 + v_H * b_w * d_w1 / (2 * T1 * K_Hbeta * K_Halpha)
    denom_Hv = 2 * T1 * K_Hbeta * K_Halpha
    if denom_Hv <= 0:
        raise ValueError(f"Mau so K_Hv <= 0: T1={T1:.2f}, K_Hbeta={K_Hbeta:.4f}, K_Halpha={K_Halpha:.4f}")
    K_Hv = 1 + (v_H * b_w * d_w1 / denom_Hv)

    # --- K_Fv (tuong tu, dung delta_F) ---
    # delta_F: rang thang = 0.016, rang nghieng = 0.006 (SPEC CHUAN)
    delta_F = DELTA_F_NGHIENG if is_nghieng else DELTA_F_THANG
    v_F = delta_F * g0 * v * math.sqrt(a_w / u_m) if u_m > 0 else 0
    denom_Fv = 2 * T1 * K_Fbeta * K_Falpha
    if denom_Fv <= 0:
        raise ValueError(f"Mau so K_Fv <= 0: T1={T1:.2f}, K_Fbeta={K_Fbeta:.4f}, K_Falpha={K_Falpha:.4f}")
    K_Fv = 1 + (v_F * b_w * d_w1 / denom_Fv)

    # He so tai trong tong:
    # K_H = K_Hbeta * K_Halpha * K_Hv
    # K_F = K_Fbeta * K_Falpha * K_Fv
    K_H = K_Hbeta * K_Halpha * K_Hv
    K_F = K_Fbeta * K_Falpha * K_Fv

    if b_w <= 0 or d_w1 <= 0 or u_m <= 0:
        return _fail("Zero geometry")

    # --- Z_M: He so vat lieu ---
    # Thep-thep: Z_M = 274 MPa^(1/2)
    Z_M = ZM  # = 274.0

    # --- Z_H: He so hinh dang be mat (TINH TU CONG THUC, KHONG HARDCODE) ---
    # Z_H = sqrt(2 * cos(beta_b) / sin(2*alpha_tw))
    Z_H = compute_ZH(beta_rad)

    # --- Z_epsilon: He so trung khop (TINH TU CONG THUC) ---
    # epsilon_alpha = [1.88 - 3.2*(1/z1 + 1/z2)] * cos(beta)
    Z_eps = compute_Z_epsilon(z1, z2, beta_rad)

    # He so trung khop ngang (tra ve de hien thi)
    epsilon_alpha = (1.88 - 3.2 * (1.0/z1 + 1.0/z2)) * cos_beta
    epsilon_alpha = max(1.0, epsilon_alpha)

    # === CONG THUC CHINH: sigma_H ===
    # sigma_H = Z_M * Z_H * Z_eps * sqrt(2*T1*K_H*(u_m+1) / (b_w * u_m * d_w1^2))
    inner_H = 2 * T1 * K_H * (u_m + 1) / (b_w * u_m * d_w1 ** 2)
    sigma_H = Z_M * Z_H * Z_eps * math.sqrt(max(0, inner_H))

    # ══════════════════════════════════════════════════════════════════
    # CUM 4: UNG SUAT UON (sigma_F)
    # sigma_F = 2*T1*K_F*Y_F*Y_beta / (b_w * d_w1 * m)
    # ══════════════════════════════════════════════════════════════════

    # --- z_v: So rang tuong duong ---
    # z_v = z1 / cos^3(beta)
    z_v = z1 / (cos_beta ** 3) if cos_beta > 0 else z1

    # --- Y_F: He so dang rang (TRA BANG 6.18, NOI SUY TUYEN TINH) ---
    Y_F1 = interpolate_yf(z_v)
    
    # Y_F2 cho banh lon
    z_v2 = z2 / (cos_beta ** 3) if cos_beta > 0 else z2
    Y_F2 = interpolate_yf(z_v2)

    # --- Y_beta: He so do nghieng rang ---
    # Y_beta = 1 - beta_deg / 140 (chi cho rang nghieng)
    if is_nghieng:
        Y_beta = max(0.7, 1 - beta_deg / 140)
    else:
        Y_beta = 1.0

    # === CONG THUC CHINH: sigma_F ===
    # sigma_F1 = 2*T1*K_F*Y_F1*Y_beta / (b_w * d_w1 * m)
    sigma_F1 = 2 * T1 * K_F * Y_F1 * Y_beta / (b_w * d_w1 * m)
    sigma_F2 = 2 * T1 * K_F * Y_F2 * Y_beta / (b_w * d_w1 * m)
    
    # Lay sigma_F lon nhat (nguy hiem nhat) de kiem tra
    sigma_F = max(sigma_F1, sigma_F2)

    # He so su dung
    S_H = sigma_H / sig_H_allow if sig_H_allow > 0 else 999
    S_F = sigma_F / sig_F_allow if sig_F_allow > 0 else 999

    # z_min kiem tra cat chan rang (undercut)
    z_min = 17 * (cos_beta ** 3)

    volume = a_w ** 2 * b_w

    return {
        # CUM 1: Dong luc hoc
        "T1": round(T1, 2),
        "n_gear": round(n_gear, 2),
        "u_x": round(u_x, 4),
        "u_d": u_d,
        
        # CUM 2: Hinh hoc
        "a_w": a_w,
        "a_w_calc": round(a_w_calc, 2),
        "m": m,
        "m_calc": round(m_calc, 3),
        "z1": z1,
        "z2": z2,
        "z_t": z_t,
        "u_m": round(u_m, 4),
        "d_w1": round(d_w1, 2),
        "d_w2": round(d_w2, 2),
        "b_w": round(b_w, 2),
        "beta_deg": round(beta_deg, 2),
        "cos_beta": round(cos_beta, 6),
        
        # CUM 3: Ung suat tiep xuc
        "v": round(v, 4),
        "v_H": round(v_H, 6),
        "Z_M": Z_M,
        "Z_H": round(Z_H, 4),
        "Z_epsilon": round(Z_eps, 4),
        "epsilon_alpha": round(epsilon_alpha, 4),
        "K_Hbeta": round(K_Hbeta, 4),
        "K_Halpha": round(K_Halpha, 4),
        "K_Hv": round(K_Hv, 6),
        "K_H": round(K_H, 6),
        "sigma_H": round(sigma_H, 2),
        "sigma_H_allow": round(sig_H_allow, 2),
        "S_H": round(S_H, 4),
        
        # CUM 4: Ung suat uon
        "z_v": round(z_v, 2),
        "z_v2": round(z_v2, 2),
        "Y_F1": round(Y_F1, 4),
        "Y_F2": round(Y_F2, 4),
        "Y_beta": round(Y_beta, 4),
        "v_F": round(v_F, 6),
        "K_Fbeta": round(K_Fbeta, 4),
        "K_Falpha": round(K_Falpha, 4),
        "K_Fv": round(K_Fv, 6),
        "K_F": round(K_F, 6),
        "sigma_F1": round(sigma_F1, 2),
        "sigma_F2": round(sigma_F2, 2),
        "sigma_F": round(sigma_F, 2),
        "sigma_F_allow": round(sig_F_allow, 2),
        "S_F": round(S_F, 4),
        
        # Kiem tra
        "z_min": round(z_min, 2),
        "pass_undercut": z1 >= z_min,
        "pass_H": S_H <= 1.0,
        "pass_F": S_F <= 1.0,
        "volume": round(volume, 0),
        
        # Tuoi tho
        "K_HL": round(K_HL, 4),
        "K_FL": round(K_FL, 4),
        
        # Vat lieu
        "matID": matID,
        "matName": mat.get("matName", ""),
        "gear_type": gear_type,
    }


def _fail(reason: str) -> dict:
    return {
        "error": reason,
        "pass_undercut": False, "pass_H": False, "pass_F": False,
        "S_H": 999, "S_F": 999,
        "sigma_H": 0, "sigma_H_allow": 0,
        "sigma_F": 0, "sigma_F_allow": 0,
        "volume": float("inf"), "z1": 0, "z_min": 17,
    }


# ══════════════════════════════════════════════════════════════════════
# CUM 5: TRUYEN DONG XICH
# ══════════════════════════════════════════════════════════════════════

def chain_design(P_kw: float, n_rpm: float, u_x: float, z1: int,
                 load_type: int = 1, chain_conditions: dict = None) -> dict:
    """
    Tinh bo truyen xich day du.
    
    chain_conditions: Dict chua cac he so dieu kien van hanh:
        K_0:   He so goc nghieng (1.0 khi <40 do, 1.25 khi >60 do)
        K_dc:  Dieu chinh KC truc (1.0 tu dong, 1.25 tam xich)
        K_bt:  Boi tron (1.0 ngam dau, 1.3 nho giot, 1.5 dinh ky)
        K_c:   So day xich (1.0 mot day, 1.7 hai day, 2.5 ba day)
        k_f:   He so vong xich (1.0 <40 do, 1.5 40-60 do, 6.0 dung)
        a_factor: He so khoang cach truc (30-50, mac dinh 40)
        n_01:  Toc do quy doi (50 cho xich con lan 1 day)
        num_strands: So day xich (1, 2, 3)
        k_m:   He so luc huong tam (1.15 nam ngang, 1.05 thang dung)
    """
    cc = chain_conditions or {}
    K_0 = cc.get("K_0", 1.0)
    K_dc = cc.get("K_dc", 1.25)
    K_bt = cc.get("K_bt", 1.3)
    K_c = cc.get("K_c", 1.0)
    k_f = cc.get("k_f", 1.0)
    a_factor = cc.get("a_factor", 40)
    n_01 = cc.get("n_01", 50.0)
    num_strands = cc.get("num_strands", 1)

    z2 = min(round(u_x * z1), 120)
    u_real = z2 / z1 if z1 > 0 else u_x

    # K = K_0 * K_d * K_dc * K_bt * K_c
    Kd_map = {0: 1.0, 1: 1.2, 2: 1.5}
    K_d = Kd_map.get(load_type, 1.2)
    K = K_0 * K_d * K_dc * K_bt * K_c
    
    K_z = 25 / z1 if z1 > 0 else 1.0
    K_n = n_01 / n_rpm if n_rpm > 0 else 1.0
    P_t = P_kw * K * K_z * K_n

    best_chain = None
    best_p = float("inf")

    for chain in _CHAINS:
        if chain["numStrands"] != num_strands:
            continue
        p = chain["pitch_p"]
        Q = chain["breakingLoad_Q"]
        q = chain["massPerMeter_q"]
        
        # v_xich = z1 * p * n / 60000 (m/s)
        v_chain = z1 * p * n_rpm / 60000
        if v_chain <= 0:
            continue
        
        # F_t = 1000 * P / v (N)
        F_t = 1000 * P_kw / v_chain
        
        # F_v = q * v^2 (N) — luc ly tam
        F_v = q * v_chain ** 2
        
        # a = a_factor * p (khoang cach truc, a_factor in [30, 50])
        a = a_factor * p
        
        # F_0 = 9.81 * k_f * a * q / 1000 (N) — luc cang ban dau
        F_o = 9.81 * k_f * q * a / 1000
        
        # s = Q*1000 / (F_t + F_o + F_v)
        s = (Q * 1000) / (F_t + F_o + F_v) if (F_t + F_o + F_v) > 0 else 0

        if s >= 7.6 and p < best_p:
            best_p = p
            best_chain = {
                "chainID": chain["chainID"],
                "pitch_p": p,
                "Q": Q,
                "q": q,
                "v_chain": round(v_chain, 4),
                "F_t": round(F_t, 2),
                "F_v": round(F_v, 2),
                "F_o": round(F_o, 2),
                "s": round(s, 2),
                "a": round(a, 2),
            }

    if best_chain is None:
        return {"pass": False, "z1": z1, "z2": z2, "u_real": round(u_real, 4)}

    p = best_chain["pitch_p"]
    a = best_chain["a"]
    
    # So mat xich X (lam tron chan)
    X = round(2 * a / p + (z1 + z2) / 2 + ((z2 - z1) / (2 * math.pi)) ** 2 * p / a)
    if X % 2 != 0:
        X += 1
    
    # Luc tac dung len truc (k_m: 1.15 nam ngang, 1.05 thang dung)
    k_m = cc.get("k_m", 1.15)
    F_r = best_chain["F_t"] * k_m

    return {
        "pass": True,
        "z1": z1,
        "z2": z2,
        "u_real": round(u_real, 4),
        "pitch_p": p,
        "X": X,
        "s": best_chain["s"],
        "Q": best_chain["Q"],
        "v_chain": best_chain["v_chain"],
        "F_t": best_chain["F_t"],
        "F_v": best_chain["F_v"],
        "F_o": best_chain["F_o"],
        "F_r": round(F_r, 2),
        "a": best_chain["a"],
        "P_t": round(P_t, 4),
        "K": round(K, 4),
        "K_z": round(K_z, 4),
        "K_n": round(K_n, 4),
    }


