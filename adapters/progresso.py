from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from interfaces import CompanhiaAdapter
from models import ViagemNormalizada

class ProgressoAdapter(CompanhiaAdapter):
    @property
    def nome_empresa(self) -> str:
        return "Auto Viação Progresso"

    def consegue_processar(self, payload: Dict[str, Any]) -> bool:
        return "codigoViagem" in payload and "cidadeOrigem" in payload

    def normalizar(self, payload: Dict[str, Any]) -> ViagemNormalizada:
        try:
            fuso = ZoneInfo(payload.get("fusoHorario", "America/Bahia"))
            formato_data = "%d/%m/%Y %H:%M"

            partida = datetime.strptime(payload["dataHoraSaida"], formato_data).replace(tzinfo=fuso)
            chegada = datetime.strptime(payload["dataHoraChegada"], formato_data).replace(tzinfo=fuso)

            if chegada <= partida:
                raise ValueError("A data de chegada deve ser posterior à data de saída.")

            horas, min_val = map(int, payload["tempoEstimado"].split(":"))
            duracao = (horas * 60) + min_val

            valor_float = float(payload["valorPassagem"].replace(",", "."))
            if valor_float <= 0:
                raise ValueError("O preço deve ser maior que zero.")

            cat_original = payload["tipoServico"].lower()
            categoria_padrao = "executivo" if "executivo" in cat_original else "convencional"

            return ViagemNormalizada(
                id_viagem=payload["codigoViagem"],
                empresa=self.nome_empresa,
                origem={"cidade": payload["cidadeOrigem"], "uf": payload["ufOrigem"]},
                destino={"cidade": payload["cidadeDestino"], "uf": payload["ufDestino"]},
                partida=partida,
                chegada=chegada,
                duracao_minutos=duracao,
                preco={"valor": valor_float, "moeda": "BRL"},
                categoria=categoria_padrao,
                assentos_disponiveis=int(payload["assentosDisponiveis"])
            )
        except Exception as e:
            raise ValueError(str(e))