from pydantic import BaseModel, Field

class GenericOutput(BaseModel):
    def __init__(self):
        print("Generic initialized")
    output: str
