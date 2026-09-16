from typing import List, Dict, Any
from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse

from models import RespostaNormalizada
from registry import IntegracaoRegistry
from adapters.progresso import ProgressoAdapter
from adapters.rota import RotaAdapter
from adapters.gontijo import GontijoAdapter
from adapters.sertao_bus import SertaoBusAdapter

app = FastAPI(
    title="API de Normalização de Passagens",
    description="Plataforma de unificação de contratos de viagens",
    version="1.0.0"
)

# Inicialização e Registro das Estratégias
registry = IntegracaoRegistry()
registry.registrar(ProgressoAdapter())
registry.registrar(RotaAdapter())
registry.registrar(GontijoAdapter())
registry.registrar(SertaoBusAdapter())

PAYLOAD_EXEMPLO_COMPLETO = [
    {
        "codigoViagem": "PRG-2026-001",
        "cidadeOrigem": "Paulo Afonso",
        "ufOrigem": "BA",
        "cidadeDestino": "Recife",
        "ufDestino": "PE",
        "dataHoraSaida": "15/10/2026 06:30",
        "dataHoraChegada": "15/10/2026 12:50",
        "fusoHorario": "America/Bahia",
        "tempoEstimado": "06:20",
        "valorPassagem": "129,90",
        "tipoServico": "EXECUTIVO",
        "assentosDisponiveis": "18"
    },
    {
        "trip_id": "ROT-2026-872",
        "origem": {"municipio": "Paulo Afonso", "estado": "BA"},
        "destino": {"municipio": "Aracaju", "estado": "SE"},
        "partida_em": "2026-10-15T07:00:00-03:00",
        "chegada_em": "2026-10-15T12:10:00-03:00",
        "duracao_minutos": 310,
        "tarifa_centavos": 8990,
        "moeda": "BRL",
        "classe": "convencional",
        "vagas": 22
    },
    {
        "serviceCode": "GON-2026-554",
        "from": {"city": "Paulo Afonso", "state": "BA"},
        "to": {"city": "Belo Horizonte", "state": "MG"},
        "departure": "2026-10-15T19:30:00Z",
        "arrival": "2026-10-16T12:10:00Z",
        "estimatedDurationSeconds": 60000,
        "fare": {"amount": "289.50", "currency": "BRL"},
        "serviceClass": "SEMI_SLEEPER",
        "availableSeats": 9
    },
    {
        "numero": "SER-2026-100",
        "rota": {
            "partida": "Paulo Afonso/BA",
            "chegada": "Maceió/AL"
        },
        "horarios": {
            "saida": "2026-10-16T08:00:00-03:00",
            "chegada": "2026-10-16T13:30:00-03:00"
        },
        "duracao_horas": 5.5,
        "preco_total": 105.90,
        "moeda": "BRL",
        "servico": "EXEC",
        "lugares_livres": 14
    }
]

@app.post("/api/v1/viagens/normalizar", response_model=RespostaNormalizada)
async def normalizar_viagens(
    payloads: List[Dict[str, Any]] = Body(
        ...,
        openapi_examples={
            "lote_completo": {
                "summary": "Lote Completo (Progresso, Rota, Gontijo e Sertão Bus)",
                "description": "Envio dos contratos das 4 empresas suportadas.",
                "value": PAYLOAD_EXEMPLO_COMPLETO
            }
        }
    )
):
    viagens_normalizadas = []

    for indice, payload in enumerate(payloads):
        adapter = registry.encontrar_adapter(payload)
        
        if not adapter:
            return JSONResponse(
                status_code=422,
                content={
                    "detail": {
                        "indice": indice,
                        "empresa_identificada": None,
                        "campo": None,
                        "mensagem": "O formato do payload não corresponde a nenhuma companhia suportada."
                    }
                }
            )

        try:
            viagem = adapter.normalizar(payload)
            viagens_normalizadas.append(viagem)
        except Exception as erro:
            mensagem_erro = str(erro)
            campo_afetado = None
            if ":" in mensagem_erro:
                partes = mensagem_erro.split(":", 1)
                campo_afetado = partes[0].strip()
                mensagem_erro = partes[1].strip()

            return JSONResponse(
                status_code=422,
                content={
                    "detail": {
                        "indice": indice,
                        "empresa_identificada": adapter.nome_empresa,
                        "campo": campo_afetado,
                        "mensagem": mensagem_erro
                    }
                }
            )

    return RespostaNormalizada(
        total=len(viagens_normalizadas),
        viagens=viagens_normalizadas
    )