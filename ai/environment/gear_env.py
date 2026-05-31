"""
MechDrive AI — Gear Environment
=================================
Môi trường Q-Learning cho tối ưu hóa bộ truyền bánh răng.
Mỗi step: nhận (state, action) → trả (reward, info).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment.formulas import (
    gear_helical_design,
    gear_straight_design,
    select_motor,
    is_expensive_material,
)
from config import (
    ETA_TOTAL,
    PENALTY_FAILURE,
    PENALTY_WASTE,
    REWARD_VOLUME_SCALE,
    REWARD_SWEET_SPOT,
    UX_VALUES,
    SCHEME_NUMBER,
    ACCURACY_GRADE,
)


class GearEnvironment:
    """
    Mechanical environment for gear transmission Q-Learning.
    
    State: (P_dc, n_dc, load_type)
    Action: (gear_type, u_d, psi_ba, z_g1, matID)
    """

    def __init__(self, scheme: int = SCHEME_NUMBER, grade: int = ACCURACY_GRADE):
        self.scheme = scheme
        self.grade = grade

    def step(self, state: tuple, action: tuple) -> tuple[float, dict]:
        """
        Execute one environment step.
        
        Args:
            state: (P_dc_kw, n_dc_rpm, load_type)
                P_dc_kw: Công suất trục công tác (kW)
                n_dc_rpm: Vòng quay trục công tác (v/p)
                load_type: 0=Tĩnh, 1=Va đập nhẹ, 2=Va đập mạnh
            action: (gear_type, u_d, psi_ba, z_g1, matID)
                gear_type: "tru_thang" hoặc "tru_nghieng"
                u_d: Tỉ số truyền cấp chậm
                psi_ba: Hệ số chiều rộng vành răng
                z_g1: Số răng sơ bộ bánh chủ động
                matID: Mã vật liệu
        
        Returns:
            (reward, info_dict)
        """
        P_dc, n_dc, load_type = state
        gear_type, u_d, psi_ba, z_g1, matID = action

        # 1. Tính công suất cần thiết & chọn motor
        P_ct = P_dc / ETA_TOTAL

        # Giả sử u_x mặc định = 2.5, u_h = u_total / u_x
        # u_total = n_dc_motor / n_dc → cần motor trước
        # Nhưng motor phụ thuộc u_total → dùng ước lượng
        u_x_default = 2.5
        u_h = u_d * 3.15  # ước lượng u_h ≈ u_d × u_côn (u_côn ≈ 3.15 cho HGT 2 cấp)
        u_total = u_h * u_x_default
        n_sb = n_dc * u_total

        motor = select_motor(P_ct, n_sb)
        if motor is None:
            return PENALTY_FAILURE, {"error": "No motor found", "pass": False}

        n_motor = motor["n_dm"]
        P_motor = motor["P_dm"]

        # Tính u_total thực tế
        u_total_real = n_motor / n_dc if n_dc > 0 else u_total

        # Tỉ số truyền cấp nhanh ước lượng (côn)
        u_con = u_total_real / (u_d * u_x_default) if (u_d * u_x_default) > 0 else 3.0
        u_con = max(1.0, min(6.3, u_con))

        # Công suất và vòng quay trục bánh răng cấp chậm
        # Trục II (sau cấp côn): n₂ = n_motor / u_côn, P₂ = P_motor × η_côn × η_ổ_lăn
        eta_con = 0.97
        eta_ol = 0.99
        n_gear = n_motor / u_con
        P_gear = P_motor * eta_con * eta_ol

        # 2. Tính toán bánh răng
        if gear_type == "tru_nghieng":
            result = gear_helical_design(
                P_kw=P_gear, n_rpm=n_gear, u_d=u_d,
                psi_ba=psi_ba, z1=z_g1, matID=matID,
                scheme=self.scheme, grade=self.grade,
            )
        else:
            result = gear_straight_design(
                P_kw=P_gear, n_rpm=n_gear, u_d=u_d,
                psi_ba=psi_ba, z1=z_g1, matID=matID,
                scheme=self.scheme, grade=self.grade,
            )

        if "error" in result:
            return PENALTY_FAILURE, result

        # 3. Tính reward
        pass_H = result["pass_H"]
        pass_F = result["pass_F"]

        if not pass_H or not pass_F:
            # Phạt nặng nếu không đạt kiểm bền
            # Phạt nhẹ hơn nếu chỉ hơi vượt (khuyến khích khám phá gần biên)
            sigma_H_ratio = result["sigma_H"] / result["sigma_H_allow"] if result["sigma_H_allow"] > 0 else 2.0
            sigma_F_ratio = result["sigma_F"] / result["sigma_F_allow"] if result["sigma_F_allow"] > 0 else 2.0
            overshoot = max(sigma_H_ratio - 1, sigma_F_ratio - 1, 0)
            reward = PENALTY_FAILURE * (0.5 + 0.5 * min(overshoot, 1.0))
            result["pass"] = False
            return reward, result

        # Phạt lãng phí: thép đắt cho tải nhỏ
        if is_expensive_material(matID) and load_type == 0:
            reward = PENALTY_WASTE
            result["pass"] = True
            result["penalty"] = "waste"
            return reward, result

        # 4. Thưởng theo kích thước tối ưu
        volume = result["volume"]
        if volume <= 0:
            return PENALTY_FAILURE, result

        reward = REWARD_VOLUME_SCALE / (volume ** 0.5)  # √volume thay vì volume để normalize

        # Bonus: σ_H / [σ_H] ∈ [0.85, 0.98] → "sát mép an toàn" = tối ưu
        sigma_H_ratio = result["sigma_H"] / result["sigma_H_allow"]
        if 0.85 <= sigma_H_ratio <= 0.98:
            reward += REWARD_SWEET_SPOT

        # Bonus nhẹ cho răng nghiêng (êm hơn, tải trọng đều hơn)
        if gear_type == "tru_nghieng":
            reward += 20

        result["pass"] = True
        return reward, result
