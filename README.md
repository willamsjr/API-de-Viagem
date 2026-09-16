🚍 API de Normalização de Passagens Rodoviárias
API REST desenvolvida em FastAPI para unificação e normalização de contratos de viagens de múltiplas empresas de transporte rodoviário. O sistema abstrai a heterogeneidade dos dados legados de cada provedor (formatos de data, fusos horários, moedas e nomenclatura de campos) e entrega uma resposta padronizada via modelo canônico.

🛠️ Decisões de Arquitetura e Projeto
O projeto foi desenhado focando em escalabilidade, desacoplamento e manutenibilidade (aplicando princípios SOLID):

Strategy Pattern (CompanhiaAdapter):

Cada empresa possui seu próprio adaptador desacoplado.

Elimina blocos extensos de if/elif no fluxo principal da aplicação.

Princípio Aberto/Fechado (OCP): Permite adicionar novas empresas sem alterar o código do endpoint principal.

Registry Pattern (IntegracaoRegistry):

Funciona como um gerenciador central de estratégias ativas.

Inverte o controle: a rota consulta o Registry, que identifica autonomamente qual adaptador é capaz de processar o payload recebido.

Modelo Canônico de Dados (ViagemNormalizada):

Unifica as divergências do mercado rodoviário em um modelo Pydantic rígido:

Datas/Horários: Alinhados ao fuso horário local (America/Bahia).

Duração: Convertida e padronizada em minutos.

Valores Monetários: Convertidos de centavos ou strings formatadas para float em BRL.

Tratamento de Exceções Resiliente (HTTP 422):

Requisições com falhas de validação, datas inconsistentes ou formatos desconhecidos retornam um 422 Unprocessable Content contendo o índice do item com erro, a empresa identificada, o campo afetado e uma mensagem amigável.

📋 Pré-requisitos
Python 3.10+

Git

🔧 Instalação
Clone o repositório:

Bash
git clone <https://github.com/willamsjr/API-de-Viagem>
cd api_passagens
Crie e ative o ambiente virtual (venv):

Linux/macOS:

Bash
python3 -m venv venv
source venv/bin/activate
Windows (PowerShell):

PowerShell
python -m venv venv
.\venv\Scripts\activate
Instale as dependências:

Bash
pip install -r requirements.txt
🚀 Execução do Servidor
Para iniciar o servidor de desenvolvimento com hot-reload:

Bash
uvicorn main:app --reload
Acesse no navegador:

Documentação Swagger UI (Interativa): http://127.0.0.1:8000/docs

Documentação Redoc: http://127.0.0.1:8000/redoc

🧪 Execução dos Testes Automatizados
A aplicação conta com uma suíte de testes integrados usando pytest cobrindo o fluxo principal e o tratamento de erros (HTTP 422).

Para rodar os testes:

Bash
pytest -W ignore
➕ Procedimento para Adicionar uma Nova Companhia
Graças à arquitetura baseada no Strategy Pattern, plugar uma nova empresa é um processo simples de 3 etapas:

1. Criar o novo Adaptador
Crie um arquivo dentro do diretório adapters/ (ex: adapters/nova_empresa.py) herdando de CompanhiaAdapter:

Python
from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from interfaces import CompanhiaAdapter
from models import ViagemNormalizada

class NovaEmpresaAdapter(CompanhiaAdapter):
    @property
    def nome_empresa(self) -> str:
        return "Nova Empresa Transportes"

    def consegue_processar(self, payload: Dict[str, Any]) -> bool:
        # Define a chave ou combinação de chaves única desta empresa
        return "id_nova_empresa" in payload

    def normalizar(self, payload: Dict[str, Any]) -> ViagemNormalizada:
        try:
            fuso = ZoneInfo("America/Bahia")
            
            # Aplique aqui as regras de parse de data, duração e preço
            partida = datetime.fromisoformat(payload["data_saida"]).replace(tzinfo=fuso)
            chegada = datetime.fromisoformat(payload["data_chegada"]).replace(tzinfo=fuso)

            if chegada <= partida:
                raise ValueError("A data de chegada deve ser posterior à data de saída.")

            return ViagemNormalizada(
                id_viagem=str(payload["id_nova_empresa"]),
                empresa=self.nome_empresa,
                origem={"cidade": payload["origem_cidade"], "uf": payload["origem_uf"]},
                destino={"cidade": payload["destino_cidade"], "uf": payload["destino_uf"]},
                partida=partida,
                chegada=chegada,
                duracao_minutos=int(payload["duracao_minutos"]),
                preco={"valor": float(payload["preco_brl"]), "moeda": "BRL"},
                categoria=payload.get("classe", "convencional").lower(),
                assentos_disponiveis=int(payload["vagas"])
            )
        except Exception as e:
            raise ValueError(str(e))

2. Registrar o novo Adaptador em main.py
Importe e instancie a nova classe no arquivo main.py:

Python
from adapters.nova_empresa import NovaEmpresaAdapter

# ...
registry.registrar(NovaEmpresaAdapter())

3. Criar Teste Unitário
Adicione um caso de teste em test_main.py validando o novo payload para garantir regressão zero.

PAYLOAD

[
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
    "origem": {
      "municipio": "Paulo Afonso",
      "estado": "BA"
    },
    "destino": {
      "municipio": "Aracaju",
      "estado": "SE"
    },
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
    "from": {
      "city": "Paulo Afonso",
      "state": "BA"
    },
    "to": {
      "city": "Belo Horizonte",
      "state": "MG"
    },
    "departure": "2026-10-15T19:30:00Z",
    "arrival": "2026-10-16T12:10:00Z",
    "estimatedDurationSeconds": 60000,
    "fare": {
      "amount": "289.50",
      "currency": "BRL"
    },
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

