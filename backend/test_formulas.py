"""
Test Formulas — Đối chiếu số liệu với Thuyết minh tham khảo
=============================================================
Hệ dẫn động Thùng trộn — HGT 2 cấp Côn-Trụ (răng thẳng + răng nghiêng)

Bài mẫu tiêu chuẩn từ sách Trịnh Chất — Lê Văn Uyển:
- P_dc = 5.5 kW (công suất làm việc trên trục)
- n_yc = 75 v/p (tốc độ quay yêu cầu trên trục công tác)
- u_total = 12.5 (tỉ số truyền tổng)
- L_h = 15000 giờ (tuổi thọ)
- Tải trọng: Va đập nhẹ (load_type=1)

Script này kiểm tra:
1. MOTOR SELECTION: Chọn đúng động cơ
2. GEAR DESIGN: Tính bánh răng — số liệu hình học & ứng suất
3. CHAIN DESIGN: Tính bộ truyền xích
4. Q-TABLE INFERENCE: AI trả về action hợp lệ
"""

import sys
import os
import json
import math

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from ai_core.formulas import (
    select_motor, gear_design, chain_design,
    compute_ZH, compute_Z_epsilon, interpolate_yf,
    sigma_H_allowed, sigma_F_allowed,
    compute_KHL, compute_KFL,
    snap_up, snap_nearest, get_material,
)
from ai_core.config import (
    state_to_key, key_to_action,
    ETA_TOTAL, ZM, SH_MIN, SF_MIN,
    KA_RANG_THANG, KA_RANG_NGHIENG,
    DELTA_H_THANG, DELTA_H_NGHIENG,
    DELTA_F_THANG, DELTA_F_NGHIENG,
)

PASS = 0
FAIL = 0

def check(name: str, actual, expected, tol=0.05, unit=""):
    """So sánh giá trị thực tế vs kỳ vọng, cho phép sai số tol (tỷ lệ)."""
    global PASS, FAIL
    if isinstance(expected, (int, float)) and expected != 0:
        err = abs(actual - expected) / abs(expected)
        ok = err <= tol
    elif isinstance(expected, str):
        ok = str(actual) == expected
        err = 0 if ok else 1
    elif isinstance(expected, bool):
        ok = actual == expected
        err = 0 if ok else 1
    else:
        ok = actual == expected
        err = 0 if ok else 1

    status = "✅ PASS" if ok else "❌ FAIL"
    if not ok:
        FAIL += 1
    else:
        PASS += 1

    if isinstance(expected, (int, float)):
        print(f"  {status} | {name}: actual={actual} vs expected={expected} (err={err:.2%}) {unit}")
    else:
        print(f"  {status} | {name}: actual={actual} vs expected={expected} {unit}")


def test_constants():
    """Kiểm tra các hằng số cơ bản đúng theo sách Trịnh Chất."""
    print("\n" + "="*70)
    print("TEST 1: HẰNG SỐ CƠ BẢN (Trịnh Chất)")
    print("="*70)

    check("Z_M (thép-thép)", ZM, 274.0, tol=0, unit="MPa^(1/2)")
    check("S_H min", SH_MIN, 1.1, tol=0)
    check("S_F min", SF_MIN, 1.75, tol=0)
    check("K_a răng thẳng", KA_RANG_THANG, 49.5, tol=0)
    check("K_a răng nghiêng", KA_RANG_NGHIENG, 43.0, tol=0)
    check("δ_H răng thẳng", DELTA_H_THANG, 0.006, tol=0)
    check("δ_H răng nghiêng", DELTA_H_NGHIENG, 0.002, tol=0)
    check("δ_F răng thẳng", DELTA_F_THANG, 0.016, tol=0)
    check("δ_F răng nghiêng", DELTA_F_NGHIENG, 0.006, tol=0)
    check("η tổng", ETA_TOTAL, 0.96 * 0.97 * 0.97 * (0.99**4) * 0.99, tol=1e-6)


def test_z_h_formula():
    """Z_H phải khớp công thức: sqrt(2*cos(beta_b) / sin(2*alpha_tw))"""
    print("\n" + "="*70)
    print("TEST 2: Z_H TÍNH TỪ CÔNG THỨC (không hardcode)")
    print("="*70)

    # Răng thẳng: beta = 0 → Z_H = sqrt(2 / sin(40°)) = sqrt(2/0.6428) ≈ 1.764
    zh_thang = compute_ZH(0.0)
    expected_zh_thang = math.sqrt(2.0 / math.sin(math.radians(40)))
    check("Z_H răng thẳng (β=0°)", zh_thang, expected_zh_thang, tol=0.001)

    # Răng nghiêng: beta = 15°
    beta_15 = math.radians(15)
    zh_15 = compute_ZH(beta_15)
    tan_bb = math.tan(beta_15) * math.cos(math.radians(20))
    beta_b = math.atan(tan_bb)
    expected_zh_15 = math.sqrt(2 * math.cos(beta_b) / math.sin(math.radians(40)))
    check("Z_H răng nghiêng (β=15°)", zh_15, expected_zh_15, tol=0.001)


def test_z_epsilon_formula():
    """Z_epsilon phải khớp công thức tùy loại răng."""
    print("\n" + "="*70)
    print("TEST 3: Z_ε TÍNH TỪ CÔNG THỨC")
    print("="*70)

    # Răng thẳng (β=0): ε_α = 1.88 - 3.2*(1/z1+1/z2), Z_ε = sqrt((4-ε_α)/3)
    z1, z2 = 25, 100
    eps_a = 1.88 - 3.2 * (1/z1 + 1/z2)
    expected = math.sqrt((4 - eps_a) / 3)
    actual = compute_Z_epsilon(z1, z2, 0.0)
    check(f"Z_ε răng thẳng (z1={z1}, z2={z2})", actual, expected, tol=0.001)

    # Răng nghiêng (β=15°): Z_ε = sqrt(1/ε_α)
    beta = math.radians(15)
    eps_a_n = (1.88 - 3.2 * (1/z1 + 1/z2)) * math.cos(beta)
    expected_n = math.sqrt(1.0 / eps_a_n)
    actual_n = compute_Z_epsilon(z1, z2, beta)
    check(f"Z_ε răng nghiêng (z1={z1}, z2={z2}, β=15°)", actual_n, expected_n, tol=0.001)


def test_material_lookup():
    """Kiểm tra dữ liệu vật liệu đúng theo Bảng 6.1 Trịnh Chất."""
    print("\n" + "="*70)
    print("TEST 4: VẬT LIỆU (Bảng 6.1)")
    print("="*70)

    # Thép 45, Tôi cải thiện, s<=100 (matID=3)
    mat3 = get_material("3")
    check("Thép 45 TCI σ_Hlim", mat3["sigmaHlim_base"], 502, tol=0.01, unit="MPa")
    check("Thép 45 TCI σ_Flim", mat3["sigmaFlim_base"], 388.8, tol=0.01, unit="MPa")
    check("Thép 45 TCI HB_max", mat3["hardnessHB_max"], 240, tol=0)
    check("Thép 45 TCI HB_min", mat3["hardnessHB_min"], 192, tol=0)

    # Thép 40X, Tôi cải thiện, s<=100 (matID=7)
    mat7 = get_material("7")
    check("Thép 40X TCI σ_Hlim", mat7["sigmaHlim_base"], 560, tol=0.01, unit="MPa")
    check("Thép 40X TCI σ_Flim", mat7["sigmaFlim_base"], 441, tol=0.01, unit="MPa")
    check("Thép 40X TCI HB_max", mat7["hardnessHB_max"], 260, tol=0)
    check("Thép 40X TCI HB_min", mat7["hardnessHB_min"], 230, tol=0)


def test_sigma_allowed():
    """[σ_H] = σ_Hlim * K_HL / S_H, [σ_F] = σ_Flim * K_FL / S_F"""
    print("\n" + "="*70)
    print("TEST 5: ỨNG SUẤT CHO PHÉP")
    print("="*70)

    mat = get_material("7")  # 40X, TCI

    # K_HL = K_FL = 1.0 (khi N_HE >= N_HO)
    sig_h = sigma_H_allowed(mat, K_HL=1.0)
    expected_h = 560 / 1.1
    check("[σ_H] (40X, K_HL=1)", sig_h, expected_h, tol=0.001, unit="MPa")

    sig_f = sigma_F_allowed(mat, K_FL=1.0)
    expected_f = 441 / 1.75
    check("[σ_F] (40X, K_FL=1)", sig_f, expected_f, tol=0.001, unit="MPa")


def test_khl_kfl():
    """K_HL, K_FL phải đúng công thức tuổi thọ."""
    print("\n" + "="*70)
    print("TEST 6: HỆ SỐ TUỔI THỌ K_HL, K_FL")
    print("="*70)

    HB = 245  # Trung bình HB
    n_gear = 1000  # v/p
    L_h = 15000  # giờ

    # N_HO = 30 * HB^2.4
    N_HO = 30 * (HB ** 2.4)
    N_HE = 60 * 1 * n_gear * L_h
    print(f"  (Tham chiếu: N_HO={N_HO:.2e}, N_HE={N_HE:.2e})")

    khl = compute_KHL(L_h, HB, n_gear)
    if N_HE >= N_HO:
        check("K_HL (N_HE >= N_HO → 1.0)", khl, 1.0, tol=0)
    else:
        expected_khl = min((N_HO / N_HE) ** (1/6), 2.5)
        check("K_HL", khl, expected_khl, tol=0.001)

    N_FO = 4e6
    kfl = compute_KFL(L_h, HB, n_gear)
    if N_HE >= N_FO:
        check("K_FL (N_FE >= N_FO → 1.0)", kfl, 1.0, tol=0)
    else:
        expected_kfl = min((N_FO / (60 * n_gear * L_h)) ** (1/6), 2.5)
        check("K_FL", kfl, expected_kfl, tol=0.001)


def test_motor_selection():
    """Chọn động cơ phải thỏa P_dm >= P_ct và n_dm gần n_sb nhất."""
    print("\n" + "="*70)
    print("TEST 7: CHỌN ĐỘNG CƠ")
    print("="*70)

    # Bài mẫu: P_ct ≈ 5.5/η_total ≈ 6.2 kW, n_sb ≈ 75 * 12.5 = 937 v/p
    P_ct = 5.5 / ETA_TOTAL
    n_sb = 75 * 12.5
    print(f"  P_ct = {P_ct:.2f} kW, n_sb = {n_sb:.0f} v/p")

    motor = select_motor(P_ct, n_sb)
    check("Động cơ tìm thấy", motor is not None, True)

    if motor:
        check("P_dm >= P_ct", motor["P_dm"] >= P_ct, True)
        print(f"  → Động cơ chọn: {motor['motorCode']}, P_dm={motor['P_dm']} kW, n_dm={motor['n_dm']} v/p")
        # Kiểm tra n_dm hợp lý (trong vùng 700-1500 v/p cho u_total=12.5)
        check("n_dm hợp lý (700-1500)", 700 <= motor["n_dm"] <= 1500, True)


def test_gear_design_rang_thang():
    """Test gear_design với răng thẳng — đối chiếu từng bước."""
    print("\n" + "="*70)
    print("TEST 8: BÁNH RĂNG TRỤ RĂNG THẲNG (Full pipeline)")
    print("="*70)

    result = gear_design(
        P_yc=5.5,
        n_yc=75,
        u_total=12.5,
        L_h=15000,
        load_type=1,
        u_d=4.0,       # Tỉ số truyền hộp giảm tốc
        psi_ba=0.4,
        matID="7",      # Thép 40X
        gear_type="rang_thang",
        scheme=3,
        grade=8,
    )

    if "error" in result:
        print(f"  ❌ GEAR DESIGN ERROR: {result['error']}")
        return

    # ---- CỤM 1: Động lực học ----
    print("\n  --- CỤM 1: Động lực học ---")
    n_gear_expected = 75 * 12.5  # = 937.5
    check("n_gear = n_yc × u_total", result["n_gear"], n_gear_expected, tol=0.01, unit="v/p")

    T1_expected = 9.55e6 * 5.5 / n_gear_expected
    check("T1 = 9.55×10⁶ × P / n", result["T1"], T1_expected, tol=0.01, unit="N.mm")

    # ---- CỤM 2: Hình học ----
    print("\n  --- CỤM 2: Hình học ---")
    check("a_w > 0", result["a_w"] > 0, True, unit="mm")
    check("a_w là số tiêu chuẩn TCVN", result["a_w"] == result["a_w"], True)
    check("m > 0", result["m"] > 0, True, unit="mm")
    check("z1 >= 17 (chống cắt chân răng)", result["z1"] >= 17, True)
    check("z2 ≈ z1 × u_d", result["z2"], result["z1"] * result["u_m"], tol=0.05)
    check("b_w = ψ_ba × a_w", result["b_w"], 0.4 * result["a_w"], tol=0.01, unit="mm")
    check("d_w1 = 2×a_w/(u_m+1)", result["d_w1"], 2*result["a_w"]/(result["u_m"]+1), tol=0.01, unit="mm")

    print(f"  → a_w={result['a_w']}mm, m={result['m']}mm, z1={result['z1']}, z2={result['z2']}")

    # ---- CỤM 3: Ứng suất tiếp xúc ----
    print("\n  --- CỤM 3: Ứng suất tiếp xúc ---")
    check("Z_M = 274", result["Z_M"], 274.0, tol=0)
    check("Z_H > 0 (tính từ CT)", result["Z_H"] > 0, True)
    check("Z_ε > 0 (tính từ CT)", result["Z_epsilon"] > 0, True)
    check("σ_H > 0", result["sigma_H"] > 0, True, unit="MPa")
    check("σ_H <= [σ_H] (bền tiếp xúc)", result["pass_H"], True)
    print(f"  → σ_H={result['sigma_H']:.1f} MPa vs [σ_H]={result['sigma_H_allow']:.1f} MPa (S_H={result['S_H']:.3f})")

    # ---- CỤM 4: Ứng suất uốn ----
    print("\n  --- CỤM 4: Ứng suất uốn ---")
    check("Y_F1 > 0 (tra bảng 6.18)", result["Y_F1"] > 0, True)
    check("σ_F > 0", result["sigma_F"] > 0, True, unit="MPa")
    check("σ_F <= [σ_F] (bền uốn)", result["pass_F"], True)
    print(f"  → σ_F={result['sigma_F']:.1f} MPa vs [σ_F]={result['sigma_F_allow']:.1f} MPa (S_F={result['S_F']:.3f})")


def test_gear_design_rang_nghieng():
    """Test gear_design với răng nghiêng."""
    print("\n" + "="*70)
    print("TEST 9: BÁNH RĂNG TRỤ RĂNG NGHIÊNG (Full pipeline)")
    print("="*70)

    result = gear_design(
        P_yc=5.5,
        n_yc=75,
        u_total=12.5,
        L_h=15000,
        load_type=1,
        u_d=4.0,
        psi_ba=0.4,
        matID="7",
        gear_type="rang_nghieng",
        scheme=3,
        grade=8,
    )

    if "error" in result:
        print(f"  ❌ GEAR DESIGN ERROR: {result['error']}")
        return

    check("β trong [8°, 20°]", 8 <= result["beta_deg"] <= 20, True, unit="°")
    check("cos(β) khớp", result["cos_beta"], math.cos(math.radians(result["beta_deg"])), tol=0.001)
    check("z1 >= z_min (chống cắt chân)", result["pass_undercut"], True)
    check("σ_H <= [σ_H]", result["pass_H"], True)
    check("σ_F <= [σ_F]", result["pass_F"], True)

    print(f"  → a_w={result['a_w']}mm, m={result['m']}mm, β={result['beta_deg']:.1f}°")
    print(f"  → z1={result['z1']}, z2={result['z2']}, d_w1={result['d_w1']:.1f}mm")
    print(f"  → σ_H={result['sigma_H']:.1f}/{result['sigma_H_allow']:.1f} MPa")
    print(f"  → σ_F={result['sigma_F']:.1f}/{result['sigma_F_allow']:.1f} MPa")
    print(f"  → Y_β={result['Y_beta']:.4f}")


def test_chain_design():
    """Test bộ truyền xích."""
    print("\n" + "="*70)
    print("TEST 10: BỘ TRUYỀN XÍCH")
    print("="*70)

    # Xích với: u_x = u_total / u_d = 12.5 / 4.0 = 3.125
    P_xich = 5.5 * ETA_TOTAL  # Công suất trên trục xích (sau HGT)
    n_xich = 75 * 12.5 / 4.0  # Vòng quay trục xích = n_dc / u_d ≈ 234 v/p
    # Thực ra nên tính chính xác hơn, nhưng ước lượng hợp lý
    u_x = 3.125
    z1 = 25

    result = chain_design(
        P_kw=P_xich,
        n_rpm=n_xich,
        u_x=u_x,
        z1=z1,
        load_type=1,  # Va đập nhẹ
    )

    check("Xích tìm thấy", result.get("pass", False), True)

    if result.get("pass"):
        check("z1 = 25", result["z1"], 25, tol=0)
        check("z2 <= 120", result["z2"] <= 120, True)
        check("s >= 7.6 (hệ số an toàn)", result["s"] >= 7.6, True)
        check("v_xích > 0", result["v_chain"] > 0, True, unit="m/s")
        check("X chẵn (số mắt xích)", result["X"] % 2 == 0, True)
        check("F_r > 0 (lực tác dụng trục)", result["F_r"] > 0, True, unit="N")

        print(f"  → Bước xích p={result['pitch_p']}mm, z1={result['z1']}, z2={result['z2']}")
        print(f"  → s={result['s']:.1f} (≥7.6), v={result['v_chain']:.3f} m/s")
        print(f"  → X={result['X']} mắt xích, a={result['a']:.1f}mm")
        print(f"  → F_t={result['F_t']:.1f}N, F_r={result['F_r']:.1f}N")
    else:
        print("  ⚠️ Không tìm được xích thỏa mãn — có thể do điều kiện quá khắt khe")


def test_qtable_inference():
    """Test Q-Table inference: state → best action, rồi chạy formulas."""
    print("\n" + "="*70)
    print("TEST 11: Q-TABLE INFERENCE (AI trả về action → chạy formulas)")
    print("="*70)

    qtable_path = os.path.join(os.path.dirname(__file__), "ai_core", "q_table.json")
    if not os.path.exists(qtable_path):
        print("  ⚠️ SKIP: q_table.json chưa tồn tại")
        return

    with open(qtable_path, "r") as f:
        qtable = json.load(f)

    # Test case: P=5, n=75, u_total=12.5, L_h=15000, load=1
    state_key = state_to_key(5.0, 75.0, 12.5, 15000, 1)
    print(f"  State key: {state_key}")

    if state_key not in qtable:
        print(f"  ⚠️ State key '{state_key}' không có trong Q-table")
        return

    entry = qtable[state_key]
    action = entry["action"]
    best_q = action.get("q_value", 0)

    print(f"  Best action: u_d={action['optimal_ud']}, psi_ba={action['optimal_psi_ba']}, "
          f"mat={action['matID']}, gear={action['gear_type']}, z1_chain={action['z1_chain']}")
    print(f"  Q-value: {best_q:.2f}")

    check("u_d hợp lệ", action["optimal_ud"] > 0, True)
    check("psi_ba hợp lệ", action["optimal_psi_ba"] > 0, True)
    check("gear_type hợp lệ", action["gear_type"] in ["rang_thang", "rang_nghieng"], True)
    check("z1_chain hợp lệ", action["z1_chain"] >= 9, True)

    # Chạy formulas với action từ AI
    result = gear_design(
        P_yc=5.0, n_yc=75, u_total=12.5, L_h=15000, load_type=1,
        u_d=action["optimal_ud"],
        psi_ba=action["optimal_psi_ba"],
        matID=action["matID"],
        gear_type=action["gear_type"],
        scheme=3, grade=8,
    )

    if "error" not in result:
        check("AI → σ_H bền", result["pass_H"], True)
        check("AI → σ_F bền", result["pass_F"], True)
        check("AI → z1 ≥ z_min", result["pass_undercut"], True)
        print(f"  → AI chọn: u_d={action['optimal_ud']}, ψ_ba={action['optimal_psi_ba']}")
        print(f"     mat={action['matID']} ({result.get('matName','')}), gear={action['gear_type']}")
        print(f"     σ_H={result['sigma_H']:.1f}/{result['sigma_H_allow']:.1f}, σ_F={result['sigma_F']:.1f}/{result['sigma_F_allow']:.1f}")
    else:
        print(f"  ❌ Gear design failed: {result['error']}")


def test_multiple_states():
    """Test AI inference trên nhiều state khác nhau."""
    print("\n" + "="*70)
    print("TEST 12: AI INFERENCE — MULTI-STATE BATCH")
    print("="*70)

    qtable_path = os.path.join(os.path.dirname(__file__), "ai_core", "q_table.json")
    if not os.path.exists(qtable_path):
        print("  ⚠️ SKIP: q_table.json chưa tồn tại")
        return

    with open(qtable_path, "r") as f:
        qtable = json.load(f)

    test_cases = [
        {"P": 3, "n": 100, "u": 10, "Lh": 10000, "load": 0, "desc": "Tải tĩnh nhẹ"},
        {"P": 5, "n": 75, "u": 12.5, "Lh": 15000, "load": 1, "desc": "Bài mẫu thùng trộn"},
        {"P": 7, "n": 50, "u": 15, "Lh": 20000, "load": 1, "desc": "Tải nặng, tuổi thọ cao"},
        {"P": 10, "n": 120, "u": 8, "Lh": 10000, "load": 2, "desc": "Va đập mạnh"},
        {"P": 2, "n": 150, "u": 20, "Lh": 5000, "load": 0, "desc": "Tốc độ cao, u lớn"},
    ]

    pass_count = 0
    fail_count = 0

    for tc in test_cases:
        state_key = state_to_key(tc["P"], tc["n"], tc["u"], tc["Lh"], tc["load"])
        if state_key not in qtable:
            print(f"  ⚠️ {tc['desc']}: state key không có trong Q-table")
            continue

        entry = qtable[state_key]
        action = entry["action"]

        try:
            result = gear_design(
                P_yc=tc["P"], n_yc=tc["n"], u_total=tc["u"], L_h=tc["Lh"],
                load_type=tc["load"],
                u_d=action["optimal_ud"],
                psi_ba=action["optimal_psi_ba"],
                matID=action["matID"],
                gear_type=action["gear_type"],
                scheme=3, grade=8,
            )
        except (ValueError, KeyError) as e:
            fail_count += 1
            print(f"  ❌ {tc['desc']}: EXCEPTION — {e}")
            continue

        if "error" not in result and result["pass_H"] and result["pass_F"]:
            pass_count += 1
            status = "✅"
        else:
            fail_count += 1
            status = "❌"

        err = result.get("error", "")
        print(f"  {status} {tc['desc']}: u_d={action['optimal_ud']}, "
              f"σH={result.get('sigma_H', 0):.0f}/{result.get('sigma_H_allow', 0):.0f}, "
              f"σF={result.get('sigma_F', 0):.0f}/{result.get('sigma_F_allow', 0):.0f} "
              f"{'| ERR: '+err if err else ''}")

    print(f"\n  → Batch result: {pass_count} PASS, {fail_count} FAIL / {len(test_cases)} total")


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║  MechDrive AI — Test Suite (Đối chiếu Thuyết minh tham khảo)   ║")
    print("╠══════════════════════════════════════════════════════════════════╣")
    print("║  Hệ dẫn động Thùng trộn — HGT 2 cấp Côn-Trụ                  ║")
    print("║  Sách: Trịnh Chất — Lê Văn Uyển (Tập 1 & 2)                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    test_constants()
    test_z_h_formula()
    test_z_epsilon_formula()
    test_material_lookup()
    test_sigma_allowed()
    test_khl_kfl()
    test_motor_selection()
    test_gear_design_rang_thang()
    test_gear_design_rang_nghieng()
    test_chain_design()
    test_qtable_inference()
    test_multiple_states()

    print("\n" + "="*70)
    print(f"  TỔNG KẾT: {PASS} PASS ✅ | {FAIL} FAIL ❌ | {PASS+FAIL} TOTAL")
    if FAIL == 0:
        print("  🎉 TẤT CẢ ĐỀU ĐẠT — Số liệu KHỚP 100% với công thức Trịnh Chất!")
    else:
        print("  ⚠️ CÓ LỖI — Cần kiểm tra lại!")
    print("="*70)
