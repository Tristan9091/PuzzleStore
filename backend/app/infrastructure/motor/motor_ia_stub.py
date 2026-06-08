from backend.app.domain.entities.conversacion import Conversacion
from backend.app.domain.entities.respuesta_asistente import RespuestaAsistente
from backend.app.domain.ports.motor_respuestas import MotorRespuestas


class MotorIAStub(MotorRespuestas):
    def responder(self, pregunta: str, conversacion: Conversacion) -> RespuestaAsistente:
        raise NotImplementedError(
            "MotorIAStub es solo demostrativo. Implementar recuperacion "
            "(RAG) + llamada al LLM aqui y devolver un RespuestaAsistente."
        )
