"""
MechDrive AI Engine — 5-Step Inference Pipeline
==================================================
Buoc 1: Tiep nhan (Input Request)
Buoc 2: Luong tu hoa (Discretization)
Buoc 3: Tra cuu Nao bo (Q-Table Lookup O(1))
Buoc 4: Giai nen Kich thuoc (Physics Calculation — 5 Cum)
Buoc 5: Xuat xuong (Output Response)
"""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from models.ai_models import AIRequest, AIResponse
import sys

AI_CORE_PATH = Path(__file__).parent.parent / "ai_core"
sys.path.insert(0, str(AI_CORE_PATH))

from ai_core.formulas import gear_design, chain_design
from ai_core.config import state_to_key, discretize, P_YC_BINS, N_YC_BINS, U_TOTAL_BINS, LH_BINS

router = APIRouter(prefix="/ai", tags=["AI Engine"])

# ── BUOC 0: Load Q-Table vao RAM khi server khoi dong ──
Q_TABLE_PATH = AI_CORE_PATH / "q_table.json"
Q_TABLE = {}
if Q_TABLE_PATH.exists():
    with open(Q_TABLE_PATH, "r", encoding="utf-8") as f:
        Q_TABLE = json.load(f)
    print(f"[AI Engine] Q-Table loaded: {len(Q_TABLE)} states in RAM")
else:
    print(f"[WARNING] Q-Table not found at {Q_TABLE_PATH}")


@router.post("/optimize-design", response_model=AIResponse)
def optimize_design(req: AIRequest):
    """
    5-Step Inference Pipeline:
    1. Tiep nhan input tu Frontend
    2. Luong tu hoa (Discretize) ve moc tieu chuan
    3. Tra cuu Q-Table (O(1))
    4. Giai nen kich thuoc bang 5 Cum cong thuc co hoc
    5. Dong goi JSON tra ve Frontend
    """

    # ════════════════════════════════════════════════════════
    # BUOC 1: TIEP NHAN
    # ════════════════════════════════════════════════════════
    P_yc = req.P_yc
    n_yc = req.n_yc
    u_total = req.u_total
    L_h = req.L_h
    load_type = req.load_type

    # ════════════════════════════════════════════════════════
    # BUOC 2: LUONG TU HOA (Discretization)
    # Ep cac so le cua User ve cac moc tieu chuan
    # VD: P=5.2 -> 5.0, n=110 -> 100, u=11 -> 10
    # ════════════════════════════════════════════════════════
    P_disc = discretize(P_yc, P_YC_BINS)
    n_disc = discretize(n_yc, N_YC_BINS)
    u_disc = discretize(u_total, U_TOTAL_BINS)
    L_disc = discretize(L_h, LH_BINS)

    state_key = f"{P_disc}|{n_disc}|{u_disc}|{L_disc}|{load_type}"

    discretization_info = {
        "original": {"P_yc": P_yc, "n_yc": n_yc, "u_total": u_total, "L_h": L_h, "load_type": load_type},
        "discretized": {"P_yc": P_disc, "n_yc": n_disc, "u_total": u_disc, "L_h": L_disc, "load_type": load_type},
        "state_key": state_key,
    }

    # ════════════════════════════════════════════════════════
    # BUOC 3: TRA CUU NAO BO (Q-Table Lookup)
    # Lay state_key tra vao Q-Table (dang nam trong RAM)
    # Boc ra bo Hat giong AI: u_d, psi_ba, mac thep, loai rang, z1_chain
    # ════════════════════════════════════════════════════════
    entry = Q_TABLE.get(state_key)
    if not entry or "error" in entry:
        raise HTTPException(
            status_code=404,
            detail=f"Q-Table khong co loi giai cho state_key='{state_key}'. "
                   f"Hay kiem tra lai input hoac retrain model."
        )

    ai_seeds = entry["action"]  # Hat giong AI

    # ════════════════════════════════════════════════════════
    # BUOC 4: GIAI NEN KICH THUOC (Physics Calculation)
    # Nem hat giong vao 5 Cum cong thuc co hoc
    # ════════════════════════════════════════════════════════

    # CUM 1-4: Banh rang (gear_design tra ve MOI bien trung gian)
    gear_result = gear_design(
        P_yc=P_disc,
        n_yc=n_disc,
        u_total=u_disc,
        L_h=L_disc,
        load_type=load_type,
        u_d=ai_seeds["optimal_ud"],
        psi_ba=ai_seeds["optimal_psi_ba"],
        matID=ai_seeds["matID"],
        gear_type=ai_seeds["gear_type"],
    )

    if "error" in gear_result:
        raise HTTPException(
            status_code=400,
            detail=f"Loi tinh toan co hoc: {gear_result['error']}"
        )

    # CUM 5: Truyen dong xich
    chain_result = chain_design(
        P_kw=P_disc,
        n_rpm=gear_result["n_gear"],
        u_x=gear_result["u_x"],
        z1=int(ai_seeds["z1_chain"]),
        load_type=load_type,
    )

    # ════════════════════════════════════════════════════════
    # BUOC 5: XUAT XUONG (Output Response)
    # Dong goi toan bo thanh JSON cho Frontend
    # ════════════════════════════════════════════════════════
    return AIResponse(
        optimal_action=ai_seeds,
        physics_details={
            "discretization": discretization_info,
            "gear": gear_result,
            "chain": chain_result,
            "summary": {
                "a_w": gear_result["a_w"],
                "m": gear_result["m"],
                "z1": gear_result["z1"],
                "z2": gear_result["z2"],
                "b_w": gear_result["b_w"],
                "d_w1": gear_result["d_w1"],
                "d_w2": gear_result["d_w2"],
                "sigma_H": gear_result["sigma_H"],
                "sigma_H_allow": gear_result["sigma_H_allow"],
                "S_H": gear_result["S_H"],
                "sigma_F": gear_result["sigma_F"],
                "sigma_F_allow": gear_result["sigma_F_allow"],
                "S_F": gear_result["S_F"],
                "pass_undercut": gear_result["pass_undercut"],
                "pass_H": gear_result["pass_H"],
                "pass_F": gear_result["pass_F"],
                "chain_pass": chain_result.get("pass", False),
                "chain_safety_factor": chain_result.get("s", 0),
            }
        }
    )
