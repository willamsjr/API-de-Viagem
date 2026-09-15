from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from interfaces import CompanhiaAdapter
from models import ViagemNormalizada

class GontijoAdapter(CompanhiaAdapter):
    @property
    def nome_empresa(self) -> str:
        return "Gontijo"

    def consegue_processar(self, payload: Dict[str, Any]) -> bool:
        return "serviceCode" in payload

    def normalizar(self, payload: Dict[str, Any]) -> ViagemNormalizada:
        try:
            fuso_bahia = ZoneInfo("America/Bahia")
            
            # Substitui o 'Z' (UTC) por '+00:00' para o Python entender, e converte para o fuso da Bahia
            partida_utc = datetime.fromisoformat(payload["departure"].replace("Z", "+00:00"))
            partida = partida_utc.astimezone(fuso_bahia)
            
            chegada_utc = datetime.fromisoformat(payload["arrival"].replace("Z", "+00:00"))
            chegada = chegada_utc.astimezone(fuso_bahia)

            if chegada <= partida:
                raise ValueError("A data de chegada deve ser posterior à data de saída.")

            # Duração vem em segundos
            duracao_minutos = int(payload["estimatedDurationSeconds"]) // 60
            if duracao_minutos <= 0:
                raise ValueError("A duração deve ser maior que zero.")

            valor_float = float(payload["fare"]["amount"])
            if valor_float <= 0:
                raise ValueError("O preço deve ser maior que zero.")

            # Normalização da categoria
            cat_original = payload["serviceClass"].upper()
            if cat_original == "SEMI_SLEEPER":
                categoria = "semileito"
            elif cat_original == "SLEEPER":
                categoria = "leito"
            else:
                categoria = "convencional"

            return ViagemNormalizada(
                id_viagem=payload["serviceCode"],
                empresa=self.nome_empresa,
                origem={"cidade": payload["from"]["city"], "uf": payload["from"]["state"]},
                destino={"cidade": payload["to"]["city"], "uf": payload["to"]["state"]},
                partida=partida,
                chegada=chegada,
                duracao_minutos=duracao_minutos,
                preco={"valor": valor_float, "moeda": payload["fare"].get("currency", "BRL")},
                categoria=categoria,
                assentos_disponiveis=int(payload["availableSeats"])
            )
        except Exception as e:
            raise ValueError(str(e))