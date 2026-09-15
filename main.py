from typing import List, Dict, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from models import RespostaNormalizada
from registry import IntegracaoRegistry

# Importação dos 4 adaptadores
from adapters.progresso import ProgressoAdapter
from adapters.rota import RotaAdapter
from adapters.gontijo import GontijoAdapter
from adapters.guanabara import GuanabaraAdapter

# 1. Criação da instância da aplicação (O Uvicorn procura por este nome "app")
app = FastAPI(
    title="API de Normalização de Passagens",
    description="Plataforma de unificação de contratos de viagens",
    version="1.0.0"
)

# 2. Configuração e Registro das Estratégias (Inversão de Controle)
registry = IntegracaoRegistry()
registry.registrar(ProgressoAdapter())
registry.registrar(RotaAdapter())
registry.registrar(GontijoAdapter())
registry.registrar(GuanabaraAdapter())


# 3. Endpoint Principal
@app.post("/api/v1/viagens/normalizar", response_model=RespostaNormalizada)
async def normalizar_viagens(payloads: List[Dict[str, Any]]):
    viagens_normalizadas = []

    for indice, payload in enumerate(payloads):
        # Tenta identificar qual companhia consegue processar o payload
        adapter = registry.encontrar_adapter(payload)
        
        # Regra: Formato não reconhecido por nenhuma empresa registrada
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

        # Tenta normalizar e validar os dados da empresa encontrada
        try:
            viagem = adapter.normalizar(payload)
            viagens_normalizadas.append(viagem)
            
        except ValueError as erro:
            # Regra: Dados inválidos interrompem toda a requisição (status 422)
            mensagem_erro = str(erro)
            
            # Tenta identificar se o erro informou qual campo falhou
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