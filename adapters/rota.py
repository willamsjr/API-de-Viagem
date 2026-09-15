from typing import Dict, Any
from datetime import datetime
from interfaces import CompanhiaAdapter
from models import ViagemNormalizada

class RotaAdapter(CompanhiaAdapter):
    @property
    def nome_empresa(self) -> str:
        return "Rota Transportes"

    def consegue_processar(self, payload: Dict[str, Any]) -> bool:
        # Identifica unicamente pela chave 'trip_id'
        return "trip_id" in payload

    def normalizar(self, payload: Dict[str, Any]) -> ViagemNormalizada:
        try:
            # fromisoformat já entende o formato "2026-10-15T07:00:00-03:00"
            partida = datetime.fromisoformat(payload["partida_em"])
            chegada = datetime.fromisoformat(payload["chegada_em"])

            if chegada <= partida:
                raise ValueError("A data de chegada deve ser posterior à data de saída.")

            # Preço vem em centavos (8990 -> 89.90)
            valor_float = payload["tarifa_centavos"] / 100.0
            if valor_float <= 0:
                raise ValueError("O preço deve ser maior que zero.")

            duracao = int(payload["duracao_minutos"])
            if duracao <= 0:
                raise ValueError("A duração deve ser maior que zero.")

            return ViagemNormalizada(
                id_viagem=payload["trip_id"],
                empresa=self.nome_empresa,
                origem={"cidade": payload["origem"]["municipio"], "uf": payload["origem"]["estado"]},
                destino={"cidade": payload["destino"]["municipio"], "uf": payload["destino"]["estado"]},
                partida=partida,
                chegada=chegada,
                duracao_minutos=duracao,
                preco={"valor": valor_float, "moeda": payload.get("moeda", "BRL")},
                categoria=payload["classe"].lower(),
                assentos_disponiveis=int(payload["vagas"])
            )
        except Exception as e:
            raise ValueError(str(e))