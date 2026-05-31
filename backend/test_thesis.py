"""
Test đối chiếu Thuyết minh tham khảo — Đặng Ngọc Thoại
========================================================
Hệ dẫn động Thùng trộn — HGT 2 cấp Côn-Trụ

DỮ LIỆU TỪ PDF:
- P_lv = 2.5 kW
- n_lv = 44 v/ph
- η_KN = 0.99, η_ol = 0.99 (mỗi cặp), η_brc = 0.96, η_brt = 0.97, η_x = 0.93
- η_tổng = 0.824
- P_ct = 2.5 / 0.824 = 3.034 kW
- Động cơ: DK.51-4, P_dc = 4.5 kW, n_dc = 1440 v/ph
- u_chung = 1440/44 = 32.73
- u_h = 14 (u1=4.05 côn, u2=3.46 trụ)
- u_x = 32.73/14 = 2.34
- n1 = 1440 v/ph
- n2 = 1440/4.05 ≈ 355.6 v/ph (PDF ghi 365 — có thể lỗi làm tròn)
- n3 = n2/3.46 ≈ 102.8 v/ph (PDF ghi 103)
- P_I = 3.034 × 0.99 × 0.99 = 2.97 kW
- P_II = 2.97 × 0.96 × 0.99 = 2.82 kW (PDF ghi 2.83)
- P_III = 2.83 × 0.97 × 0.99 = 2.72 kW (PDF ghi 2.71)
"""

import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from ai_core.formulas import gear_design, chain_design, select_motor

print("=" * 70)
print("DOI CHIEU THUYET MINH THAM KHAO — Dang Ngoc Thoai")
print("He dan dong Thung tron — HGT 2 cap Con-Tru")
print("=" * 70)

# ============================================================
# PHAN 1: KIEM TRA HIEU SUAT VA CONG SUAT
# ============================================================
print("\n--- PHAN 1: HIEU SUAT & CONG SUAT ---")

eta_kn = 0.99
eta_ol = 0.99  # moi cap
n_ol = 4       # 4 cap o lan
eta_brc = 0.96
eta_brt = 0.97
eta_x = 0.93   # Thuyet minh dung 0.93 (khac voi he thong cua ta: 0.96)

eta_total_pdf = eta_kn * (eta_ol ** n_ol) * eta_brc * eta_brt * eta_x
print(f"  eta_tong (tinh lai)  = {eta_total_pdf:.4f}")
print(f"  eta_tong (PDF ghi)   = 0.8240")
print(f"  Sai lech: {abs(eta_total_pdf - 0.824):.6f}")

P_lv = 2.5  # kW
P_ct = P_lv / eta_total_pdf
print(f"\n  P_ct (tinh lai) = {P_lv}/{eta_total_pdf:.4f} = {P_ct:.3f} kW")
print(f"  P_ct (PDF ghi)  = 3.034 kW")
print(f"  Sai lech: {abs(P_ct - 3.034):.4f} kW")

# ============================================================
# PHAN 2: CHON DONG CO
# ============================================================
print("\n--- PHAN 2: CHON DONG CO ---")
print(f"  PDF chon: DK.51-4, P_dc=4.5 kW, n_dc=1440 v/ph")
print(f"  (Dong co DK — dong cu, KHONG co trong DB 4A cua ta)")

# Thu chon trong DB 4A cua ta voi cung dieu kien
n_sb = 44 * 32.73  # = 1440 (lam tron)
motor = select_motor(P_ct, n_sb)
if motor:
    print(f"  He thong ta chon: {motor['motorCode']}, P_dm={motor['P_dm']} kW, n_dm={motor['n_dm']} v/ph")
    print(f"  -> KHAC dong co vi DB khac (4A vs DK), nhung P_dm >= P_ct: OK")
else:
    print(f"  -> Khong tim thay dong co phu hop trong DB 4A")

# ============================================================
# PHAN 3: TI SO TRUYEN
# ============================================================
print("\n--- PHAN 3: TI SO TRUYEN ---")
n_dc_pdf = 1440  # v/ph
n_lv = 44
u_chung = n_dc_pdf / n_lv
print(f"  u_chung = {n_dc_pdf}/{n_lv} = {u_chung:.2f} (PDF: 32.73)")

u_h = 14      # HGT
u1 = 4.05     # BR con cap nhanh
u2 = u_h / u1
u_x_pdf = u_chung / u_h
print(f"  u_h = {u_h} (HGT)")
print(f"  u1 = {u1} (BR con)")
print(f"  u2 = {u_h}/{u1} = {u2:.2f} (PDF: 3.46)")
print(f"  u_x = {u_chung:.2f}/{u_h} = {u_x_pdf:.2f} (PDF: 2.34)")

# ============================================================
# PHAN 4: CONG SUAT & VONG QUAY TREN CAC TRUC
# ============================================================
print("\n--- PHAN 4: CONG SUAT & VONG QUAY TREN CAC TRUC ---")
P_I = P_ct * eta_kn * eta_ol
P_II = P_I * eta_brc * eta_ol
P_III = P_II * eta_brt * eta_ol

n1 = n_dc_pdf
n2 = n1 / u1
n3 = n2 / u2

print(f"  P_I   = {P_ct:.3f} x 0.99 x 0.99 = {P_I:.3f} kW (PDF: 2.97)")
print(f"  P_II  = {P_I:.3f} x 0.96 x 0.99 = {P_II:.3f} kW (PDF: 2.83)")
print(f"  P_III = {P_II:.3f} x 0.97 x 0.99 = {P_III:.3f} kW (PDF: 2.71)")
print()
print(f"  n1 = {n1} v/ph (PDF: 1440)")
print(f"  n2 = {n1}/{u1} = {n2:.1f} v/ph (PDF ghi 365 — NHUNG 1440/4.05 = {1440/4.05:.1f})")
print(f"  n3 = {n2:.1f}/{u2:.2f} = {n3:.1f} v/ph (PDF: 103)")

# Momen xoan
T1 = 9.55e6 * P_I / n1
T2 = 9.55e6 * P_II / n2
T3 = 9.55e6 * P_III / n3
print(f"\n  T1 = 9.55e6 x {P_I:.3f} / {n1} = {T1:.0f} N.mm")
print(f"  T2 = 9.55e6 x {P_II:.3f} / {n2:.1f} = {T2:.0f} N.mm")
print(f"  T3 = 9.55e6 x {P_III:.3f} / {n3:.1f} = {T3:.0f} N.mm")

# ============================================================
# PHAN 5: CHAY GEAR DESIGN VOI THONG SO TU PDF
# ============================================================
print("\n--- PHAN 5: GEAR DESIGN (BR tru rang thang, cap cham u2=3.46) ---")
print("  (Dung truc tiep formulas.py voi thong so tu PDF)")

# Cap cham: BR tru rang thang, u_d = u2 = 3.46
# Cong suat tren truc II: P_II
# Vong quay truc vao cap cham: n2
# Chon vat lieu pho thong: Thep 45 TCI (matID=3) hoac 40X (matID=7)
# psi_ba = 0.4 (gia tri thuong dung cho HGT 2 cap)

for mat_id, mat_name in [("3", "Thep 45 TCI"), ("7", "Thep 40X TCI")]:
    print(f"\n  ** Vat lieu: {mat_name} (matID={mat_id}) **")
    try:
        result = gear_design(
            P_yc=P_II,           # Cong suat truc vao cap cham
            n_yc=n3,             # Vong quay dau ra (truc III)
            u_total=u2,          # Ti so truyen cap cham = u2
            L_h=15000,           # Tuoi tho (gia dinh 15000h)
            load_type=0,         # Tai tinh (PDF: "tai trong khong doi")
            u_d=u2,              # u_d = u2 (cap cham chi co 1 cap)
            psi_ba=0.4,          # He so chieu rong vanh rang
            matID=mat_id,
            gear_type="rang_thang",  # Cap cham: rang thang theo PDF
            scheme=3,
            grade=8,
        )

        if "error" in result:
            print(f"    LOI: {result['error']}")
            continue

        print(f"    T1       = {result['T1']:.0f} N.mm")
        print(f"    a_w      = {result['a_w']} mm (tinh: {result['a_w_calc']:.1f})")
        print(f"    m        = {result['m']} mm")
        print(f"    z1       = {result['z1']}, z2 = {result['z2']}")
        print(f"    b_w      = {result['b_w']:.1f} mm")
        print(f"    d_w1     = {result['d_w1']:.1f} mm")
        print(f"    v        = {result['v']:.3f} m/s")
        print(f"    sigma_H  = {result['sigma_H']:.1f} / [{result['sigma_H_allow']:.1f}] MPa  (S_H={result['S_H']:.3f})")
        print(f"    sigma_F  = {result['sigma_F']:.1f} / [{result['sigma_F_allow']:.1f}] MPa  (S_F={result['S_F']:.3f})")
        print(f"    PASS_H   = {result['pass_H']}")
        print(f"    PASS_F   = {result['pass_F']}")
        print(f"    Z_H      = {result['Z_H']:.4f}")
        print(f"    Z_eps    = {result['Z_epsilon']:.4f}")
        print(f"    K_H      = {result['K_H']:.4f}")
        print(f"    K_F      = {result['K_F']:.4f}")
    except Exception as e:
        print(f"    EXCEPTION: {e}")

# ============================================================
# PHAN 6: CHAY CHAIN DESIGN VOI THONG SO TU PDF
# ============================================================
print("\n--- PHAN 6: CHAIN DESIGN (Bo truyen xich, u_x=2.34) ---")

# Cong suat tren truc III (ra khoi HGT, vao xich): P_III
# Vong quay truc III: n3
# u_x = 2.34
# z1: thuong chon 25-27 cho xich con lan
for z1_test in [25, 27]:
    print(f"\n  ** z1 = {z1_test} **")
    result_chain = chain_design(
        P_kw=P_III,
        n_rpm=n3,
        u_x=u_x_pdf,
        z1=z1_test,
        load_type=0,  # Tai tinh
        chain_conditions={
            "K_0": 1.0,
            "K_dc": 1.0,      # Dieu chinh tu dong
            "K_bt": 1.0,      # Boi tron ngam dau
            "K_c": 1.0,       # 1 day xich
            "k_f": 1.0,       # Nghieng < 40 do
            "a_factor": 40,
            "n_01": 50,
            "num_strands": 1,
        },
    )

    if result_chain.get("pass"):
        print(f"    Buoc xich p = {result_chain['pitch_p']} mm")
        print(f"    z2 = {result_chain['z2']}")
        print(f"    u_real = {result_chain['u_real']}")
        print(f"    s = {result_chain['s']:.1f} (>= 7.6)")
        print(f"    v_xich = {result_chain['v_chain']:.3f} m/s")
        print(f"    X = {result_chain['X']} mat xich")
        print(f"    a = {result_chain['a']:.1f} mm")
        print(f"    F_t = {result_chain['F_t']:.1f} N")
        print(f"    F_r = {result_chain['F_r']:.1f} N")
        print(f"    P_t = {result_chain['P_t']:.3f}")
        print(f"    K = {result_chain['K']:.3f}")
    else:
        print(f"    Khong tim duoc xich thoa man")

print("\n" + "=" * 70)
print("LUU Y QUAN TRONG:")
print("  1. PDF dung dong co DK (dong cu), ta dung 4A → so motor khac")
print("  2. PDF dung eta_x = 0.93, he thong ta: 0.96 → P_ct se khac")
print("  3. PDF ghi n2 = 365 nhung 1440/4.05 = 355.6 (loi lam tron PDF)")
print("  4. De so truc tiep sigma_H, sigma_F: can paste them PHAN 2.2 tu PDF")
print("=" * 70)
