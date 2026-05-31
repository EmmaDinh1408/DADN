from pydantic import BaseModel
from typing import Dict, Any

class AIRequest(BaseModel):
    P_yc: float
    n_yc: float
    u_total: float
    L_h: float
    load_type: int

class AIResponse(BaseModel):
    # Action tối ưu trả về từ Q-Table
    optimal_action: Dict[str, Any]
    # Toàn bộ thông số vật lý tính toán
    physics_details: Dict[str, Any]
