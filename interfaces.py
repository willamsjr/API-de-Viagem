from abc import ABC, abstractmethod
from typing import Dict, Any
from models import ViagemNormalizada  

class CompanhiaAdapter(ABC):
    
    @property
    @abstractmethod
    def nome_empresa(self) -> str:
        """Retorna o nome da empresa."""
        pass

    @abstractmethod
    def consegue_processar(self, payload: Dict[str, Any]) -> bool:
        """Avalia pela estrutura do JSON se este adapter é o dono do payload."""
        pass

    @abstractmethod
    def normalizar(self, payload: Dict[str, Any]) -> ViagemNormalizada:
        """Converte o payload original no contrato normalizado e valida os dados."""
        pass