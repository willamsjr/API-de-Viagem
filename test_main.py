from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

PAYLOAD_VALIDO = [
    {
        "codigoViagem": "PRG-2026-001",
        "cidadeOrigem": "Salvador",
        "ufOrigem": "BA",
        "cidadeDestino": "Feira de Santana",
        "ufDestino": "BA",
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
        "origem": {"municipio": "Vitória da Conquista", "estado": "BA"},
        "destino": {"municipio": "Ilhéus", "estado": "BA"},
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
        "from": {"city": "Petrolina", "state": "PE"},
        "to": {"city": "Recife", "state": "PE"},
        "departure": "2026-10-15T19:30:00Z",
        "arrival": "2026-10-16T12:10:00Z",
        "estimatedDurationSeconds": 60000,
        "fare": {"amount": "289.50", "currency": "BRL"},
        "serviceClass": "SEMI_SLEEPER",
        "availableSeats": 9
    },
    {
        "codigo_servico": "GUA-2026-100",
        "origem_destino": {
            "ponto_partida": "Fortaleza - CE",
            "ponto_chegada": "Sobral - CE"
        },
        "data_saida": "2026-10-16 08:00:00",
        "data_chegada": "2026-10-16 11:30:00",
        "valor_ticket": 65.50,
        "classe_bus": "LEITO",
        "assentos_vazios": 15
    }
]

def test_deve_normalizar_payload_de_todas_as_empresas_com_sucesso():
    response = client.post("/api/v1/viagens/normalizar", json=PAYLOAD_VALIDO)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    
    # Validação do nome oficial de cada empresa
    assert data["viagens"][0]["empresa"] == "Auto Viação Progresso"
    assert data["viagens"][1]["empresa"] == "Rota Transportes"
    assert data["viagens"][2]["empresa"] == "Gontijo"
    assert data["viagens"][3]["empresa"] == "Expresso Guanabara"  

def test_deve_retornar_422_quando_formato_for_desconhecido():
    payload_invalido = [{"campo_invalido": "teste"}]
    response = client.post("/api/v1/viagens/normalizar", json=payload_invalido)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"]["empresa_identificada"] is None

def test_deve_retornar_422_quando_chegada_for_anterior_a_saida():
    payload_erro = [
        {
            "codigo_servico": "GUA-2026-100",
            "origem_destino": {
                "ponto_partida": "Fortaleza - CE",
                "ponto_chegada": "Sobral - CE"
            },
            "data_saida": "2026-10-16 12:00:00",
            "data_chegada": "2026-10-16 08:00:00",  
            "valor_ticket": 65.50,
            "classe_bus": "LEITO",
            "assentos_vazios": 15
        }
    ]
    response = client.post("/api/v1/viagens/normalizar", json=payload_erro)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"]["empresa_identificada"] == "Expresso Guanabara"