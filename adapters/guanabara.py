from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import HTTPException  # <--- Import necessário
from interfaces import CompanhiaAdapter
from models import ViagemNormalizada, OrigemDestino, Preco

class GuanabaraAdapter(CompanhiaAdapter):
    @property
    def nome_empresa(self) -> str:
        return "Expresso Guanabara"

    def consegue_processar(self, payload: dict) -> bool:
        return "codigo_servico" in payload and "origem_destino" in payload

    def normalizar(self, payload: dict) -> ViagemNormalizada:
        origem_partes = payload["origem_destino"]["ponto_partida"].split("-")
        destino_partes = payload["origem_destino"]["ponto_chegada"].split("-")

        origem_cidade = origem_partes[0].strip()
        origem_uf = origem_partes[1].strip() if len(origem_partes) > 1 else ""
        
        destino_cidade = destino_partes[0].strip()
        destino_uf = destino_partes[1].strip() if len(destino_partes) > 1 else ""

        fuso_bahia = ZoneInfo("America/Bahia")
        dt_partida = datetime.strptime(payload["data_saida"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=fuso_bahia)
        dt_chegada = datetime.strptime(payload["data_chegada"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=fuso_bahia)

        # VALIDAÇÃO: Chegada deve ser posterior à saída
        if dt_chegada <= dt_partida:
            raise HTTPException(
                status_code=422,
                detail={
                    "empresa_identificada": self.nome_empresa,
                    "erro": "A data de chegada nao pode ser anterior ou igual a data de saida"
                }
            )

        duracao_minutos = int((dt_chegada - dt_partida).total_seconds() // 60)

        classe_map = {
            "CONVENCIONAL": "CONVENCIONAL",
            "EXECUTIVO": "EXECUTIVO",
            "LEITO": "LEITO"
        }
        categoria = classe_map.get(str(payload.get("classe_bus", "")).upper(), "CONVENCIONAL")

        return ViagemNormalizada(
            id_viagem=str(payload["codigo_servico"]),
            empresa=self.nome_empresa,
            origem=OrigemDestino(cidade=origem_cidade, uf=origem_uf),
            destino=OrigemDestino(cidade=destino_cidade, uf=destino_uf),
            partida=dt_partida,
            chegada=dt_chegada,
            duracao_minutos=duracao_minutos,
            preco=Preco(valor=float(payload["valor_ticket"]), moeda="BRL"),
            categoria=categoria,
            assentos_disponiveis=int(payload["assentos_vazios"])
        )