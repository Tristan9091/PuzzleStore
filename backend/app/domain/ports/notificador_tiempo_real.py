from abc import ABC, abstractmethod

from backend.app.domain.entities.mensaje_chat import MensajeChat


class NotificadorTiempoReal(ABC):
    @abstractmethod
    async def notificar(self, conversacion_id: str, mensaje: MensajeChat) -> None:
        pass
