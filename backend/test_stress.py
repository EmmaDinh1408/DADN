import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from ai_core.formulas import compute_ZH, compute_Z_epsilon, interpolate_yf, ZM

# --- THONG SO TU THUYET MINH (CAP CHAM - BR TRU RANG THANG) ---
T1 = 75917      # N.mm (Mo men xoan truc II)
a_w = 160.0     # mm
m = 2.5         # mm
z1 = 28
z2 = 100
u_m = z2 / z1   # 3.5714
b_w = 50.5      # mm
d_w1 = m * z1   # 70.0 mm
v = 1.3         # m/s (Van toc vong)

# --- TINH UNG SUAT TIEP XUC (sigma_H) ---
# He so Z
Z_M = ZM  # 274
Z_H = compute_ZH(0.0)  # beta = 0 -> 1.764
Z_eps = compute_Z_epsilon(z1, z2, 0.0) # -> 0.869

# He so K_H theo Thuyet minh ghi: KH = 1.1284
K_H = 1.1284

inner_H = 2 * T1 * K_H * (u_m + 1) / (b_w * u_m * d_w1 ** 2)
sigma_H = Z_M * Z_H * Z_eps * math.sqrt(inner_H)

# --- TINH UNG SUAT UON (sigma_F) ---
# He so Y_F
Y_F1 = interpolate_yf(z1) 
Y_F2 = interpolate_yf(z2) 

# He so K_F theo Thuyet minh ghi: KF = 1.177
K_F = 1.177
Y_beta = 1.0  # rang thang

# He so Y_eps (Sinh vien tinh = 1 / Z_eps^2 hoac tuong tu)
# Theo Trinh Chat: Y_eps = 1 / epsilon_alpha
eps_alpha = 1.88 - 3.2 * (1/z1 + 1/z2)
Y_eps = 1.0 / eps_alpha
# Nhieu sinh vien hoac sach dung CT: Y_eps = 1 (hoac bo qua)
# Nhung trong thuyet minh ghi: Y_eps = 0.577

sigma_F1 = 2 * T1 * K_F * 0.577 * Y_F1 * Y_beta / (b_w * d_w1 * m)
sigma_F2 = 2 * T1 * K_F * 0.577 * Y_F2 * Y_beta / (b_w * d_w1 * m)

print("="*70)
print("SO SANH UNG SUAT VOI THUYET MINH")
print("="*70)
print(f"1. He so Z_H : Engine = {Z_H:.3f} | Thuyet minh = 1.76")
print(f"2. He so Z_eps: Engine = {Z_eps:.3f} | Thuyet minh = 0.869")
print(f"3. Ung suat H : Engine = {sigma_H:.1f} MPa | Thuyet minh = 394.5 MPa")
print(f"   (Sai so: {abs(sigma_H - 394.5):.2f} MPa)")
print("-" * 50)
print(f"4. He so Y_F1 : Engine = {Y_F1:.2f} | Thuyet minh = 3.94")
print(f"5. He so Y_F2 : Engine = {Y_F2:.2f} | Thuyet minh = 3.602")
print(f"6. Ung suat F1: Engine = {sigma_F1:.1f} MPa | Thuyet minh = 40.3 MPa")
print(f"7. Ung suat F2: Engine = {sigma_F2:.1f} MPa | Thuyet minh = 36.8 MPa")
print(f"   (Sai so: {abs(sigma_F1 - 40.3):.2f} MPa, {abs(sigma_F2 - 36.8):.2f} MPa)")
print("="*70)
