from pydantic import BaseModel

class MotorResponse(BaseModel):
    motorCode: str
    P_dm: float
    n_dm: float
    torqueRatio: float

class ChainResponse(BaseModel):
    chainID: str
    breakingLoad_Q: float
    massPerMeter_q: float
    pitch_p: float
    numStrands: int

class MaterialResponse(BaseModel):
    matID: str
    matName: str
    sigmaHlim_base: float
    sigmaFlim_base: float
    sigma_ch: float
    sigma_b: float
    hardnessHB_max: float
    hardnessHB_min: float
