from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from database import Base

from models import Usuario, Receita, Despesa
from schemas import (
    UsuarioCreate,
    ReceitaCreate,
    DespesaCreate
)

from score import calcular_score

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FinanIA")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "status": "FinanIA Online"
    }


@app.post("/usuarios")
def criar_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
):

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        salario=usuario.salario
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


@app.post("/receitas")
def criar_receita(
    receita: ReceitaCreate,
    db: Session = Depends(get_db)
):

    nova = Receita(**receita.dict())

    db.add(nova)
    db.commit()

    return {"mensagem": "Receita cadastrada"}


@app.post("/despesas")
def criar_despesa(
    despesa: DespesaCreate,
    db: Session = Depends(get_db)
):

    nova = Despesa(**despesa.dict())

    db.add(nova)
    db.commit()

    return {"mensagem": "Despesa cadastrada"}


@app.get("/dashboard/{usuario_id}")
def dashboard(
    usuario_id: int,
    db: Session = Depends(get_db)
):

    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id
    ).first()

    receitas = db.query(Receita).filter(
        Receita.usuario_id == usuario_id
    ).all()

    despesas = db.query(Despesa).filter(
        Despesa.usuario_id == usuario_id
    ).all()

    total_receitas = sum(r.valor for r in receitas)
    total_despesas = sum(d.valor for d in despesas)

    score = calcular_score(
        usuario.salario,
        total_receitas,
        total_despesas
    )

    return {
        "usuario": usuario.nome,
        "salario": usuario.salario,
        "receitas": total_receitas,
        "despesas": total_despesas,
        "saldo": total_receitas - total_despesas,
        "finanscore": score
    }