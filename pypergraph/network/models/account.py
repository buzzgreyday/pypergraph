from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from pypergraph.core.constants import DAG_MAX

class Balance(BaseModel):
    ordinal: int = Field(ge=0)
    balance: int = Field(ge=0, le=DAG_MAX)
    address: Optional[str] = Field(default=None, min_length=40, max_length=128)
    meta: Optional[Dict[str, Any]] = None

