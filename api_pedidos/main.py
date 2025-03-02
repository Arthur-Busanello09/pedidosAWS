from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import List, Literal
import uuid
import psycopg2
import json
from datetime import datetime

app = FastAPI()

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/postgres"

class Item(BaseModel):
    produto: str
    quantidade: int
    preco: float

class Pedido(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cliente: str
    email: EmailStr
    itens: List[Item]
    total: float
    status: Literal["pendente", "aprovado", "cancelado"] = "pendente"  # Define valores aceitos
    data_criacao: datetime = Field(default_factory=datetime.utcnow)
    data_atualizacao: datetime = Field(default_factory=datetime.utcnow)

@app.post("/pedidos/")
def criar_pedido(pedido: Pedido):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pedidos (id, cliente, email, itens, total, status, data_criacao, data_atualizacao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (pedido.id, pedido.cliente, pedido.email, json.dumps([item.model_dump() for item in pedido.itens]), 
                 pedido.total, pedido.status, pedido.data_criacao, pedido.data_atualizacao),
            )
            conn.commit()
    return {"id": pedido.id, "mensagem": "Pedido criado com sucesso!"}

# Listar pedidos
@app.get("/pedidos/")
def listar_pedidos():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pedidos")
            pedidos = cur.fetchall()

    return {"pedidos": pedidos}

# Obter detalhes de um pedido
@app.get("/pedidos/{pedido_id}")
def obter_pedido(pedido_id: str):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM pedidos WHERE id = %s", (pedido_id,))
            pedido = cur.fetchone()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    
    return {"pedido": pedido}

# Atualizar status do pedido
@app.put("/pedidos/{pedido_id}")
def atualizar_pedido(pedido_id: str, status: str):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE pedidos SET status = %s, data_atualizacao = NOW() WHERE id = %s", (status, pedido_id))
            conn.commit()

    return {"mensagem": "Pedido atualizado com sucesso!"}

# Deletar um pedido
@app.delete("/pedidos/{pedido_id}")
def deletar_pedido(pedido_id: str):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pedidos WHERE id = %s", (pedido_id,))
            conn.commit()

    return {"mensagem": "Pedido deletado com sucesso!"}
