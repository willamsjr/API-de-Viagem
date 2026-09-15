from datetime import datetime
from typing import List  
from pydantic import BaseModel

class OrigemDestino(BaseModel):
    cidade: str
    uf: str

class Preco(BaseModel):
    valor: float
    moeda: str = "BRL"

class ViagemNormalizada(BaseModel):
    id_viagem: str
    empresa: str
    origem: OrigemDestino
    destino: OrigemDestino
    partida: datetime
    chegada: datetime
    duracao_minutos: int
    preco: Preco
    categoria: str
    assentos_disponiveis: int

class RespostaNormalizada(BaseModel):
    total: int
    viagens: List[ViagemNormalizada]