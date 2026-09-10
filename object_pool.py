"""
PATRÓN CREACIONAL: Object Pool
================================
Contexto: Pool de conexiones a base de datos.

El Object Pool mantiene un conjunto de objetos reutilizables
(conexiones) para evitar el costo de crearlos y destruirlos
repetidamente. Cuando un cliente necesita un objeto, lo toma
del pool; al terminar, lo devuelve en lugar de destruirlo.

Diferencia con Singleton/Factory: no crea uno ni muchos objetos
bajo demanda, sino que RECICLA un número fijo de instancias.
"""

import time
import threading
from typing import Optional


# ──────────────────────────────────────────────
# Producto: objeto que el pool administra
# ──────────────────────────────────────────────
class ConexionDB:
    """Simula una conexión costosa a una base de datos."""

    _contador = 0  # para asignar IDs únicos

    def __init__(self, host: str, puerto: int):
        ConexionDB._contador += 1
        self.id = ConexionDB._contador
        self.host = host
        self.puerto = puerto
        self.en_uso = False
        self._conectar()

    def _conectar(self):
        """Simula el tiempo de establecer la conexión."""
        print(f"  [ConexionDB #{self.id}] Estableciendo conexión con {self.host}:{self.puerto}...")
        time.sleep(0.1)  # coste simulado
        print(f"  [ConexionDB #{self.id}] Conexión lista.")

    def ejecutar_query(self, sql: str) -> str:
        if not self.en_uso:
            raise RuntimeError("La conexión no está en uso activo.")
        print(f"  [ConexionDB #{self.id}] Ejecutando: {sql}")
        return f"Resultado de '{sql}'"

    def __repr__(self):
        estado = "EN USO" if self.en_uso else "disponible"
        return f"ConexionDB(id={self.id}, host={self.host}, estado={estado})"



# Object Pool

class PoolConexiones:
    """
    Administra un conjunto fijo de ConexionDB.
    Thread-safe gracias a un Lock.
    """

    def __init__(self, host: str, puerto: int, tamaño: int = 3):
        self._host = host
        self._puerto = puerto
        self._lock = threading.Lock()
        self._pool: list[ConexionDB] = []
        self._crear_pool(tamaño)

    def _crear_pool(self, tamaño: int):
        print(f"\n[Pool] Creando {tamaño} conexiones iniciales...")
        for _ in range(tamaño):
            self._pool.append(ConexionDB(self._host, self._puerto))
        print(f"[Pool] Pool listo con {tamaño} conexiones.\n")

    def adquirir(self) -> Optional[ConexionDB]:
        """Devuelve una conexión libre o None si todas están ocupadas."""
        with self._lock:
            for conexion in self._pool:
                if not conexion.en_uso:
                    conexion.en_uso = True
                    print(f"[Pool] Conexión #{conexion.id} adquirida.")
                    return conexion
        print("[Pool] ¡Sin conexiones disponibles!")
        return None

    def liberar(self, conexion: ConexionDB):
        """Devuelve una conexión al pool para ser reutilizada."""
        with self._lock:
            if conexion in self._pool:
                conexion.en_uso = False
                print(f"[Pool] Conexión #{conexion.id} liberada y disponible de nuevo.")

    def estado(self):
        print("\n[Pool] Estado actual:")
        for c in self._pool:
            print(f"  {c}")
        print()


# ──────────────────────────────────────────────
# Cliente
# ──────────────────────────────────────────────
def cliente_A(pool: PoolConexiones):
    conn = pool.adquirir()
    if conn:
        resultado = conn.ejecutar_query("SELECT * FROM usuarios")
        print(f"  Cliente A obtuvo: {resultado}")
        pool.liberar(conn)


def cliente_B(pool: PoolConexiones):
    conn = pool.adquirir()
    if conn:
        resultado = conn.ejecutar_query("SELECT * FROM productos")
        print(f"  Cliente B obtuvo: {resultado}")
        pool.liberar(conn)


if __name__ == "__main__":
    print("=" * 55)
    print("   PATRÓN OBJECT POOL — Pool de Conexiones DB")
    print("=" * 55)

    pool = PoolConexiones(host="localhost", puerto=5432, tamaño=3)

    # Tres clientes adquieren conexiones simultáneamente
    conn1 = pool.adquirir()
    conn2 = pool.adquirir()
    conn3 = pool.adquirir()

    # Intento de adquirir cuando el pool está lleno
    conn4 = pool.adquirir()  # debería fallar

    pool.estado()

    # Liberar una y reutilizarla
    pool.liberar(conn1)
    cliente_A(pool)   # reutiliza conn1
    cliente_B(pool)   # también debería poder adquirir

    pool.estado()
