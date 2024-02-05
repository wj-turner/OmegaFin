from pydantic import BaseModel

class Symbol(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
