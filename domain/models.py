import pydantic
from typing import Optional

class BloodGasData(pydantic.BaseModel):
    # Obrigatórios
    ph: float = pydantic.Field(..., description="pH arterial")
    pco2: float = pydantic.Field(..., description="pCO2 em mmHg")
    hco3: float = pydantic.Field(..., description="HCO3- em mEq/L")

    # Opcionais para AG e Delta/Delta
    na: Optional[float] = None
    cl: Optional[float] = None
    albumina: Optional[float] = pydantic.Field(4.5, description="Valor padrão 4.5 g/dL")

    @pydantic.model_validator(mode='after')
    def check_physiological_limits(self) -> 'BloodGasData':
        if self.ph < 6.8 or self.ph > 7.8:
            raise ValueError(f"pH {self.ph} incompatível com a vida.")
        if self.pco2 < 10 or self.pco2 > 130:
            raise ValueError(f"pCO2 {self.pco2} fora dos limites fisiológicos.")
        return self

    @property
    def has_ionogram(self) -> bool:
        return self.na is not None and self.cl is not None