"""
MechDrive AI — Unified Environment
=====================================
Hàm Environment(State, Action) theo Phần II + III Spec.
Phán xét tính khả thi bằng 3 cửa ải phân cấp.

1 Agent duy nhất. 5 biến State × 5 biến Action.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.formulas import gear_design
from config import (
    ETA_TOTAL, SCHEME_NUMBER, ACCURACY_GRADE,
    EXPENSIVE_MATS,
    R_UNDERCUT, R_STRENGTH_BASE,
    R_VOLUME_SCALE, R_SWEET_SPOT_BONUS,
    R_OVER_DESIGN_PENALTY, R_WASTE_MATERIAL_PENALTY,
)


class MechEnvironment:
    """
    Môi trường vật lý cho Q-Learning.
    
    State = (P_yc, n_yc, u_total, L_h, load_type)
    Action = (u_d, psi_ba, matID, gear_type, z1_chain)
    
    Output: (reward, info_dict)
    
    Reward theo 3 cửa ải:
      Cửa 1: Cắt chân răng      → R = -2000
      Cửa 2: Vi phạm sức bền    → R = -1000 × max(S_H, S_F)
      Cửa 3: Tối ưu hóa toàn diện
    """

    def __init__(self, scheme: int = SCHEME_NUMBER, grade: int = ACCURACY_GRADE):
        self.scheme = scheme
        self.grade = grade

    def step(self, state: tuple, action: tuple) -> tuple[float, dict]:
        """
        Thực thi 1 bước môi trường.
        
        Args:
            state: (P_yc, n_yc, u_total, L_h, load_type)
            action: (u_d, psi_ba, matID, gear_type, z1_chain)
        
        Returns:
            (reward: float, info: dict)
        """
        P_yc, n_yc, u_total, L_h, load_type = state
        u_d, psi_ba, matID, gear_type, z1_chain = action

        # ── Validation cơ bản ──
        if u_d <= 0 or u_d > u_total:
            return R_UNDERCUT, {"gate": 0, "error": "u_d invalid"}

        # ── Chạy Physics Environment (Phần II) ──
        try:
            result = gear_design(
                P_yc=P_yc, n_yc=n_yc, u_total=u_total, L_h=L_h,
                load_type=load_type, u_d=u_d, psi_ba=psi_ba,
                matID=matID, gear_type=gear_type,
                scheme=self.scheme, grade=self.grade,
            )
        except (ValueError, KeyError) as e:
            # Trừng phạt sự ngu dốt của AI khi chạm vào lỗi vật lý nghiêm trọng
            return -10000, {"gate": 0, "error": f"Khủng hoảng Vật lý: {str(e)}"}

        if "error" in result:
            return R_UNDERCUT, {"gate": 0, "error": result["error"]}

        # ══════════════════════════════════════════════════════════════
        # CỬA ẢI 1: Vi phạm Hình học (Cắt chân răng)
        # z_min = 17 × cos³β, NẾU z₁ < z_min → R = -2000
        # ══════════════════════════════════════════════════════════════
        if not result["pass_undercut"]:
            result["gate"] = 1
            return R_UNDERCUT, result

        # ══════════════════════════════════════════════════════════════
        # CỬA ẢI 2: Vi phạm Sức bền (Gãy / Tróc rỗ)
        # S_H = σ_H / [σ_H], S_F = σ_F / [σ_F]
        # NẾU S_H > 1 HOẶC S_F > 1 → R = -1000 × max(S_H, S_F)
        # ══════════════════════════════════════════════════════════════
        S_H = result["S_H"]
        S_F = result["S_F"]

        if S_H > 1.0 or S_F > 1.0:
            reward = R_STRENGTH_BASE * max(S_H, S_F)
            result["gate"] = 2
            return reward, result

        # ══════════════════════════════════════════════════════════════
        # CỬA ẢI 3: Tối ưu hóa Toàn diện (Vùng An Toàn)
        # Chỉ đến đây khi S_H ≤ 1 VÀ S_F ≤ 1
        # ══════════════════════════════════════════════════════════════
        a_w = result["a_w"]
        b_w = result["b_w"]

        # 3a. Tối ưu không gian: R_vol = 5×10⁷ / (a_w² × b_w)
        volume = a_w ** 2 * b_w
        R_vol = R_VOLUME_SCALE / volume if volume > 0 else 0

        # 3b. Chống Over-engineering
        R_safe = 0
        if 0.90 <= S_H <= 0.98:
            R_safe = R_SWEET_SPOT_BONUS     # +500: vùng vàng tối ưu
        elif S_H < 0.80:
            R_safe = R_OVER_DESIGN_PENALTY  # -200: thiết kế thừa

        # 3c. Kinh tế học: thép đắt nhưng ứng suất thấp = lãng phí
        R_mat = 0
        if matID in EXPENSIVE_MATS and S_H < 0.75:
            R_mat = R_WASTE_MATERIAL_PENALTY  # -300

        reward = R_vol + R_safe + R_mat
        result["gate"] = 3
        result["R_vol"] = R_vol
        result["R_safe"] = R_safe
        result["R_mat"] = R_mat
        return reward, result
