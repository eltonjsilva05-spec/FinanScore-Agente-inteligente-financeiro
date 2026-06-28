from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nome: str
    email: str
    salario: float


class ReceitaCreate(BaseModel):
    descricao: str
    valor: float
    usuario_id: int


class DespesaCreate(BaseModel):
    descricao: str
    categoria: str
    valor: float
    usuario_id: int