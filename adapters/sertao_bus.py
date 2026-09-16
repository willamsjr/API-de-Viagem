from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from interfaces import CompanhiaAdapter
from models import ViagemNormalizada

class SertaoBusAdapter(CompanhiaAdapter):
    @property
    def nome_empresa(self) -> str:
        return "Sertão Bus"

    def consegue_processar(self, payload: Dict[str, Any]) -> bool:
        return "numero" in payload and "rota" in payload and "duracao_horas" in payload

    def normalizar(self, payload: Dict[str, Any]) -> ViagemNormalizada:
        fuso = ZoneInfo("America/Bahia")

        # Parse de Origem/Destino ("Paulo Afonso/BA")
        origem_raw = payload["rota"]["partida"].split("/")
        destino_raw = payload["rota"]["chegada"].split("/")

        origem = {"cidade": origem_raw[0].strip(), "uf": origem_raw[1].strip()}
        destino = {"cidade": destino_raw[0].strip(), "uf": destino_raw[1].strip()}

        # Datas e Fuso
        partida = datetime.fromisoformat(payload["horarios"]["saida"]).astimezone(fuso)
        chegada = datetime.fromisoformat(payload["horarios"]["chegada"]).astimezone(fuso)

        if chegada <= partida:
            raise ValueError("chegada_em: A data de chegada deve ser posterior à data de saída.")

        # Duração (horas decimais para minutos inteiros: 5.5 -> 330)
        duracao_minutos = int(float(payload["duracao_horas"]) * 60)

        # Mapeamento de Categoria
        categoria_raw = str(payload.get("servico", "")).upper()
        mapeamento_categorias = {
            "CONV": "convencional",
            "EXEC": "executivo",
            "SEMI": "semileito",
            "LEITO": "leito"
        }
        categoria = mapeamento_categorias.get(categoria_raw, "executivo")

        return ViagemNormalizada(
            id_viagem=str(payload["numero"]),
            empresa=self.nome_empresa,
            origem=origem,
            destino=destino,
            partida=partida,
            chegada=chegada,
            duracao_minutos=duracao_minutos,
            preco={"valor": float(payload["preco_total"]), "moeda": payload.get("moeda", "BRL")},
            categoria=categoria,
            assentos_disponiveis=int(payload["lugares_livres"])
        )