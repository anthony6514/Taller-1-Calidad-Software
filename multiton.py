"""
PATRÓN CREACIONAL: Multiton
================================
Contexto: Sistema de loggers por categoría de módulo.

El Multiton es una generalización del Singleton: en lugar de
permitir UNA sola instancia, permite UNA instancia por cada
clave (key). La misma clave siempre devuelve el mismo objeto.

Aquí se aplica para que cada módulo de la aplicación (base_de_datos,
seguridad, pagos) tenga su propio Logger único y compartido.

Diferencia con Singleton: Singleton → 1 instancia global.
Multiton → 1 instancia por clave (N instancias controladas).
"""

import datetime
from typing import ClassVar


# ──────────────────────────────────────────────
# Multiton base (metaclase reutilizable)
# ──────────────────────────────────────────────
class MultitonMeta(type):
    """
    Metaclase que implementa el patrón Multiton.
    Cada subclase mantiene su propio diccionario de instancias.
    """
    _instancias: ClassVar[dict] = {}

    def __call__(cls, clave: str, *args, **kwargs):
        # Clave compuesta: (Clase, clave_usuario)
        llave = (cls, clave)
        if llave not in cls._instancias:
            instancia = super().__call__(clave, *args, **kwargs)
            cls._instancias[llave] = instancia
            print(f"[Multiton] Nueva instancia creada → {cls.__name__}('{clave}')")
        else:
            print(f"[Multiton] Instancia existente reutilizada → {cls.__name__}('{clave}')")
        return cls._instancias[llave]



# Producto: Logger por módulo

class Logger(metaclass=MultitonMeta):
    """
    Logger único por categoría/módulo.
    Se crea una sola vez por clave; llamadas posteriores
    devuelven la misma instancia.
    """

    NIVELES = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

    def __init__(self, modulo: str, nivel_minimo: str = "DEBUG"):
        self.modulo = modulo
        self.nivel_minimo = nivel_minimo
        self._historial: list[str] = []
        print(f"  Logger '{modulo}' inicializado (nivel mínimo: {nivel_minimo})")

    def _registrar(self, nivel: str, mensaje: str):
        if self.NIVELES.get(nivel, 0) >= self.NIVELES.get(self.nivel_minimo, 0):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            entrada = f"[{timestamp}] [{nivel}] [{self.modulo}] {mensaje}"
            self._historial.append(entrada)
            print(f"  {entrada}")

    def debug(self, mensaje: str):
        self._registrar("DEBUG", mensaje)

    def info(self, mensaje: str):
        self._registrar("INFO", mensaje)

    def warning(self, mensaje: str):
        self._registrar("WARNING", mensaje)

    def error(self, mensaje: str):
        self._registrar("ERROR", mensaje)

    def mostrar_historial(self):
        print(f"\n  --- Historial de '{self.modulo}' ({len(self._historial)} entradas) ---")
        for e in self._historial:
            print(f"    {e}")

    def __repr__(self):
        return f"Logger(modulo='{self.modulo}', id={id(self)})"


# ──────────────────────────────────────────────
# Simulación de módulos de la aplicación
# ──────────────────────────────────────────────
class ModuloBaseDeDatos:
    def __init__(self):
        self.log = Logger("base_de_datos", nivel_minimo="DEBUG")

    def conectar(self):
        self.log.info("Conectando a PostgreSQL...")

    def consultar(self, sql: str):
        self.log.debug(f"Query: {sql}")

    def error_conexion(self):
        self.log.error("Timeout al conectar con el servidor.")


class ModuloSeguridad:
    def __init__(self):
        self.log = Logger("seguridad", nivel_minimo="WARNING")

    def autenticar(self, usuario: str):
        self.log.info(f"Autenticando usuario '{usuario}'")  # filtrado por nivel
        self.log.warning(f"Intento de acceso con usuario '{usuario}'")

    def acceso_denegado(self, usuario: str):
        self.log.error(f"Acceso denegado a '{usuario}' — credenciales inválidas")


class ModuloPagos:
    def __init__(self):
        # Reutiliza el MISMO logger que ModuloBaseDeDatos
        self.log = Logger("base_de_datos")

    def procesar_pago(self, monto: float):
        self.log.info(f"Procesando pago de ${monto:.2f}")


if __name__ == "__main__":
    print("=" * 55)
    print("   PATRÓN MULTITON — Loggers por Módulo")
    print("=" * 55)

    print("\n--- Creación de módulos ---")
    db1 = ModuloBaseDeDatos()
    seg = ModuloSeguridad()
    pagos = ModuloPagos()   # comparte logger con db1

    print("\n--- Operaciones ---")
    db1.conectar()
    db1.consultar("SELECT * FROM clientes")
    seg.autenticar("ana_perez")
    seg.acceso_denegado("hacker_99")
    pagos.procesar_pago(150.00)
    db1.error_conexion()

    print("\n--- Verificación de identidad (Multiton) ---")
    logger_db_directo = Logger("base_de_datos")
    print(f"  db1.log es logger_db_directo: {db1.log is logger_db_directo}")
    print(f"  db1.log es pagos.log:          {db1.log is pagos.log}")
    print(f"  db1.log es seg.log:            {db1.log is seg.log}")

    print()
    db1.log.mostrar_historial()
    seg.log.mostrar_historial()
