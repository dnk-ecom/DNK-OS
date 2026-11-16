# --- DNK-MRH-HEADER ---
# mrh_id: "services/dnk_distribution/contracts/schemas.py"
# purpose: "Strict Pydantic v2 schemas for dnk_distribution"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# --- END DNK-MRH-HEADER ---
from pydantic import BaseModel, ConfigDict

class ServiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    query: str

class ServiceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    result: str
