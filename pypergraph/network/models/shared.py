from pydantic import BaseModel, constr


class Hash(BaseModel):
    hash: constr(pattern=r"^[a-fA-F0-9]{64}$")