"""
MechDrive AI — Chain Environment
==================================
Môi trường Q-Learning cho tối ưu hóa bộ truyền xích.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.formulas import chain_design, select_motor
from config import (
    ETA_TOTAL, ETA_GEAR_CON, ETA_GEAR_TRU, ETA_OL,
    PENALTY_FAILURE,
)


class ChainEnvironment:
    """
    Mechanical environment for chain transmission Q-Learning.
    
    State: (P_dc, n_dc, load_type)
    Action: (u_x, z1)
    """

    def step(self, state: tuple, action: tuple) -> tuple[float, dict]:
        """
        Execute one environment step for chain.
        
        Args:
            state: (P_dc_kw, n_dc_rpm, load_type)
            action: (u_x, z1)
        
        Returns:
            (reward, info_dict)
        """
        P_dc, n_dc, load_type = state
        u_x, z1 = action

        # 1. Tính công suất cần thiết & ước lượng motor
        P_ct = P_dc / ETA_TOTAL

        # Ước lượng u_total → chọn motor
        u_h_est = 8.0  # ước lượng u_h cho HGT 2 cấp
        u_total = u_h_est * u_x
        n_sb = n_dc * u_total

        motor = select_motor(P_ct, n_sb)
        if motor is None:
            return PENALTY_FAILURE, {"error": "No motor", "pass": False}

        n_motor = motor["n_dm"]
        P_motor = motor["P_dm"]

        # Công suất trục xích = P_motor × η_hộp × η_ổ_lăn
        # (xích nằm sau HGT côn-trụ)
        eta_hgt = ETA_GEAR_CON * ETA_GEAR_TRU * (ETA_OL ** 3)
        P_chain = P_motor * eta_hgt

        # Vòng quay trục xích = n_motor / u_h
        u_total_real = n_motor / n_dc if n_dc > 0 else u_total
        u_h_real = u_total_real / u_x if u_x > 0 else u_h_est
        n_chain = n_motor / u_h_real if u_h_real > 0 else n_motor / u_h_est

        # 2. Tính toán bộ truyền xích
        result = chain_design(
            P_kw=P_chain,
            n_rpm=n_chain,
            u_x=u_x,
            z1=z1,
            load_type=load_type,
        )

        if not result.get("pass", False):
            return PENALTY_FAILURE, result

        # 3. Tính reward
        p_chosen = result["pitch_p"]
        s = result["s"]
        s_allow = result["s_allow"]
        F_r = result.get("F_r", 0)

        # Thưởng bước xích nhỏ (nhẹ hơn, rẻ hơn)
        reward = 5000 / p_chosen

        # Thưởng z₁ hợp lý (vùng vàng: 23-29)
        if 23 <= z1 <= 29:
            reward += 100
        elif 19 <= z1 <= 22:
            reward += 50

        # Thưởng hệ số an toàn vừa đủ (sát mép)
        s_ratio = s / s_allow if s_allow > 0 else 0
        if 1.0 <= s_ratio <= 1.3:
            reward += 80  # sát mép = tối ưu
        elif s_ratio > 2.0:
            reward -= 30  # quá dư = lãng phí

        # Phạt nhẹ nếu u_x quá lớn (xích to)
        if u_x > 4.0:
            reward -= 20

        result["pass"] = True
        return reward, result
