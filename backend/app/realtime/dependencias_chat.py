from sqlalchemy.orm import Session

from backend.app.application.use_cases.chat_use_cases import (
    IniciarConversacion,
    ObtenerHistorial,
    ProcesarMensajeCliente,
)
from backend.app.domain.ports.motor_respuestas import MotorRespuestas
from backend.app.infrastructure.motor.motor_faq_simple import MotorFaqSimple
from backend.app.infrastructure.repositories.conversacion_repository_sql import (
    ConversacionRepositorySQL,
)
from backend.app.infrastructure.repositories.faq_repository_sql import FaqRepositorySQL


def construir_motor(db: Session) -> MotorRespuestas:
    return MotorFaqSimple(FaqRepositorySQL(db))


def construir_procesar_mensaje(db: Session) -> ProcesarMensajeCliente:
    return ProcesarMensajeCliente(
        conversacion_repository=ConversacionRepositorySQL(db),
        motor_respuestas=construir_motor(db),
    )


def construir_iniciar_conversacion(db: Session) -> IniciarConversacion:
    return IniciarConversacion(ConversacionRepositorySQL(db))


def construir_obtener_historial(db: Session) -> ObtenerHistorial:
    return ObtenerHistorial(ConversacionRepositorySQL(db))
