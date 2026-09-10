"""
PATRÓN ESTRUCTURAL: Decorator
================================
Contexto: Sistema de notificaciones con canales y filtros.

El Decorator adjunta responsabilidades adicionales a un objeto
de forma dinámica, sin modificar su clase. Los decoradores
envuelven al componente original y añaden comportamiento antes
o después de delegarle la llamada.

Aquí un Mensaje base puede ser decorado con:
  - Cifrado (EncriptadorDecorator)
  - Compresión (CompresorDecorator)
  - Marca de tiempo (TimestampDecorator)
  - Prioridad (PrioridadDecorator)

Los decoradores se apilan en cualquier orden y combinación.
"""

import base64
import zlib
import datetime
from abc import ABC, abstractmethod


# ──────────────────────────────────────────────
# Componente base (interfaz)
# ──────────────────────────────────────────────
class Notificacion(ABC):
    """Interfaz común para notificaciones y sus decoradores."""

    @abstractmethod
    def obtener_contenido(self) -> str:
        pass

    @abstractmethod
    def obtener_metadata(self) -> dict:
        pass

    def describir(self) -> str:
        meta = self.obtener_metadata()
        etiquetas = ", ".join(f"{k}={v}" for k, v in meta.items())
        return f"[{etiquetas}] {self.obtener_contenido()}"


# ──────────────────────────────────────────────
# Componente concreto
# ──────────────────────────────────────────────
class MensajeSimple(Notificacion):
    """Notificación básica sin ningún procesamiento extra."""

    def __init__(self, texto: str, destinatario: str):
        self._texto = texto
        self._destinatario = destinatario

    def obtener_contenido(self) -> str:
        return self._texto

    def obtener_metadata(self) -> dict:
        return {"destinatario": self._destinatario, "tipo": "simple"}



# Decorador base

class NotificacionDecorator(Notificacion, ABC):
    """
    Clase base para todos los decoradores.
    Mantiene una referencia al componente envuelto.
    """

    def __init__(self, notificacion: Notificacion):
        self._envuelto = notificacion

    def obtener_contenido(self) -> str:
        return self._envuelto.obtener_contenido()

    def obtener_metadata(self) -> dict:
        return self._envuelto.obtener_metadata().copy()



# Decoradores concretos

class EncriptadorDecorator(NotificacionDecorator):
    """Cifra el contenido del mensaje en Base64."""

    def obtener_contenido(self) -> str:
        original = super().obtener_contenido()
        cifrado = base64.b64encode(original.encode("utf-8")).decode("utf-8")
        return f"[ENC:{cifrado}]"

    def obtener_metadata(self) -> dict:
        meta = super().obtener_metadata()
        meta["cifrado"] = "base64"
        return meta


class CompresorDecorator(NotificacionDecorator):
    """Comprime el contenido con zlib y lo representa en hex."""

    def obtener_contenido(self) -> str:
        original = super().obtener_contenido()
        comprimido = zlib.compress(original.encode("utf-8"))
        return f"[ZIP:{comprimido.hex()[:20]}...]"

    def obtener_metadata(self) -> dict:
        meta = super().obtener_metadata()
        contenido = super().obtener_contenido()
        meta["tamaño_original"] = f"{len(contenido)} bytes"
        meta["compresion"] = "zlib"
        return meta


class TimestampDecorator(NotificacionDecorator):
    """Añade marca de tiempo al contenido."""

    def obtener_contenido(self) -> str:
        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{super().obtener_contenido()} @{ahora}"

    def obtener_metadata(self) -> dict:
        meta = super().obtener_metadata()
        meta["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d")
        return meta


class PrioridadDecorator(NotificacionDecorator):
    """Marca el mensaje con un nivel de prioridad."""

    ICONOS = {"alta": "🔴", "media": "🟡", "baja": "🟢"}

    def __init__(self, notificacion: Notificacion, nivel: str = "media"):
        super().__init__(notificacion)
        self._nivel = nivel.lower()

    def obtener_contenido(self) -> str:
        icono = self.ICONOS.get(self._nivel, "⚪")
        return f"{icono} {super().obtener_contenido()}"

    def obtener_metadata(self) -> dict:
        meta = super().obtener_metadata()
        meta["prioridad"] = self._nivel
        return meta


# ──────────────────────────────────────────────
# Servicio de envío (cliente)
# ──────────────────────────────────────────────
class ServicioNotificaciones:
    """Envía notificaciones (en este demo las imprime)."""

    def enviar(self, notificacion: Notificacion):
        print(f"  Enviando → {notificacion.describir()}\n")


if __name__ == "__main__":
    print("=" * 60)
    print("   PATRÓN DECORATOR — Sistema de Notificaciones")
    print("=" * 60)

    servicio = ServicioNotificaciones()

    # ── Caso 1: mensaje simple, sin decoradores
    print("\n--- Caso 1: Mensaje sin decoradores ---")
    msg1 = MensajeSimple("Bienvenido al sistema", "carlos@email.com")
    servicio.enviar(msg1)

    # ── Caso 2: mensaje con timestamp y prioridad alta
    print("--- Caso 2: Timestamp + Prioridad Alta ---")
    msg2 = MensajeSimple("Tu pedido fue enviado", "ana@email.com")
    msg2 = TimestampDecorator(msg2)
    msg2 = PrioridadDecorator(msg2, nivel="alta")
    servicio.enviar(msg2)

    # ── Caso 3: cifrado + timestamp
    print("--- Caso 3: Cifrado + Timestamp ---")
    msg3 = MensajeSimple("Código de verificación: 9284", "luis@email.com")
    msg3 = EncriptadorDecorator(msg3)
    msg3 = TimestampDecorator(msg3)
    servicio.enviar(msg3)

    # ── Caso 4: todos los decoradores apilados
    print("--- Caso 4: Prioridad + Compresión + Cifrado + Timestamp ---")
    msg4 = MensajeSimple("Alerta de seguridad: acceso inusual detectado", "admin@email.com")
    msg4 = PrioridadDecorator(msg4, nivel="alta")
    msg4 = CompresorDecorator(msg4)
    msg4 = EncriptadorDecorator(msg4)
    msg4 = TimestampDecorator(msg4)
    servicio.enviar(msg4)

    # ── Verificación: el objeto original no fue modificado
    print("--- Verificación: mensaje original intacto ---")
    original = MensajeSimple("Alerta de seguridad: acceso inusual detectado", "admin@email.com")
    print(f"  Original: {original.describir()}\n")
