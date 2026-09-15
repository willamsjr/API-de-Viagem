from typing import List, Dict, Any, Optional
from interfaces import CompanhiaAdapter

class IntegracaoRegistry:
    def __init__(self):
        self._adapters: List[CompanhiaAdapter] = []

    def registrar(self, adapter: CompanhiaAdapter) -> None:
        """Registra um novo adaptador de companhia."""
        self._adapters.append(adapter)

    def encontrar_adapter(self, payload: Dict[str, Any]) -> Optional[CompanhiaAdapter]:
        """
        Percorre todos os adaptadores registrados e retorna o primeiro
        que reconhecer a estrutura do payload (polimorfismo sem if/elif).
        """
        for adapter in self._adapters:
            if adapter.consegue_processar(payload):
                return adapter
        return None