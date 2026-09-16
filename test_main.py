from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

PAYLOAD_TESTE_SUCESSO = [
    {
        "codigoViagem": "PROG-101",
        "cidadeOrigem": "Recife",
        "ufOrigem": "PE",
        "cidadeDestino": "Caruaru",
        "ufDestino": "PE",
        "dataHoraSaida": "20/10/2026 08:00",
        "dataHoraChegada": "20/10/2026 10:30",
        "tempoEstimado": "02:30",
        "valorPassagem": "45,00",
        "tipoServico": "CONVENCIONAL",
        "assentosDisponiveis": 20
    },
    {
        "trip_id": "ROTA-882",
        "origem": {"municipio": "Ilhéus", "estado": "BA"},
        "destino": {"municipio": "Itabuna", "estado": "BA"},
        "partida_em": "2026-10-20T09:00:00-03:00",
        "chegada_em": "2026-10-20T10:00:00-03:00",
        "duracao_minutos": 60,
        "tarifa_centavos": 2500,
        "moeda": "BRL",
        "classe": "EXECUTIVO",
        "vagas": 12
    },
    {
        "serviceCode": "GON-404",
        "from": {"city": "Salvador", "state": "BA"},
        "to": {"city": "Feira de Santana", "state": "BA"},
        "departure": "2026-10-20T14:00:00Z",
        "arrival": "2026-10-20T16:00:00Z",
        "estimatedDurationSeconds": 7200,
        "fare": {"amount": 38.50, "currency": "BRL"},
        "serviceClass": "SEMI_SLEEPER",
        "availableSeats": 18
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

def test_normalizar_viagens_lote_completo_sucesso():
    response = client.post("/api/v1/viagens/normalizar", json=PAYLOAD_TESTE_SUCESSO)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 4
    assert len(data["viagens"]) == 4
    
    empresas_retornadas = [v["empresa"] for v in data["viagens"]]
    assert "Auto Viação Progresso" in empresas_retornadas
    assert "Rota Transportes" in empresas_retornadas
    assert "Gontijo" in empresas_retornadas
    assert "Sertão Bus" in empresas_retornadas

def test_normalizar_viagens_empresa_desconhecida_retorna_422():
    payload_invalido = [{"campo_desconhecido": "valor"}]
    response = client.post("/api/v1/viagens/normalizar", json=payload_invalido)
    
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["empresa_identificada"] is None
    assert detail["mensagem"] == "O formato do payload não corresponde a nenhuma companhia suportada."