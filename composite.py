"""
PATRÓN ESTRUCTURAL: Composite
================================
Contexto: Sistema de archivos con carpetas y archivos.

El Composite compone objetos en estructuras de árbol para
representar jerarquías parte-todo. Permite tratar objetos
individuales (hojas) y composiciones (ramas) de manera uniforme.

Componentes:
  - Componente (interfaz): Archivo
  - Hoja:       ArchivoSimple
  - Compuesto:  Carpeta  (puede contener ArchivoSimple y otras Carpeta)

Operaciones uniformes: mostrar(), tamaño(), buscar()
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


# ──────────────────────────────────────────────
# Componente base (interfaz)
# ──────────────────────────────────────────────
class Archivo(ABC):
    """
    Interfaz común para archivos simples y carpetas.
    Define las operaciones que aplican a ambos.
    """

    def __init__(self, nombre: str):
        self._nombre = nombre
        self._padre: Optional[Carpeta] = None

    @property
    def nombre(self) -> str:
        return self._nombre

    @abstractmethod
    def tamaño(self) -> int:
        """Tamaño en KB."""
        pass

    @abstractmethod
    def mostrar(self, nivel: int = 0):
        """Muestra la estructura con indentación."""
        pass

    @abstractmethod
    def buscar(self, nombre: str) -> list[Archivo]:
        """Busca recursivamente por nombre (parcial)."""
        pass

    def ruta(self) -> str:
        """Devuelve la ruta completa desde la raíz."""
        if self._padre is None:
            return self._nombre
        return f"{self._padre.ruta()}/{self._nombre}"

    def _indent(self, nivel: int) -> str:
        return "    " * nivel


# ──────────────────────────────────────────────
# Hoja: ArchivoSimple
# ──────────────────────────────────────────────
class ArchivoSimple(Archivo):
    """Nodo hoja — no puede contener otros componentes."""

    ICONOS = {
        ".py": "🐍", ".txt": "📄", ".jpg": "🖼️",
        ".png": "🖼️", ".pdf": "📕", ".mp3": "🎵",
        ".zip": "📦", ".exe": "⚙️",
    }

    def __init__(self, nombre: str, tamaño_kb: int):
        super().__init__(nombre)
        self._tamaño_kb = tamaño_kb

    def tamaño(self) -> int:
        return self._tamaño_kb

    def mostrar(self, nivel: int = 0):
        extension = "." + self._nombre.rsplit(".", 1)[-1] if "." in self._nombre else ""
        icono = self.ICONOS.get(extension, "📄")
        print(f"{self._indent(nivel)}{icono} {self._nombre}  ({self._tamaño_kb} KB)")

    def buscar(self, nombre: str) -> list[Archivo]:
        if nombre.lower() in self._nombre.lower():
            return [self]
        return []

    def __repr__(self):
        return f"ArchivoSimple('{self._nombre}', {self._tamaño_kb} KB)"


# ──────────────────────────────────────────────
# Compuesto: Carpeta
# ──────────────────────────────────────────────
class Carpeta(Archivo):
    """
    Nodo compuesto — puede contener ArchivoSimple y otras Carpetas.
    Implementa las mismas operaciones que ArchivoSimple,
    delegando a sus hijos de forma recursiva.
    """

    def __init__(self, nombre: str):
        super().__init__(nombre)
        self._hijos: list[Archivo] = []

    # ── Gestión de hijos ──────────────────────
    def agregar(self, componente: Archivo) -> Carpeta:
        componente._padre = self
        self._hijos.append(componente)
        return self  # permite encadenamiento fluido

    def eliminar(self, componente: Archivo):
        self._hijos.remove(componente)
        componente._padre = None

    def obtener_hijo(self, indice: int) -> Archivo:
        return self._hijos[indice]

    # ── Operaciones compuestas ────────────────
    def tamaño(self) -> int:
        """Suma recursiva del tamaño de todos los hijos."""
        return sum(hijo.tamaño() for hijo in self._hijos)

    def mostrar(self, nivel: int = 0):
        total = self.tamaño()
        print(f"{self._indent(nivel)}📁 {self._nombre}/  ({total} KB total)")
        for hijo in self._hijos:
            hijo.mostrar(nivel + 1)

    def buscar(self, nombre: str) -> list[Archivo]:
        """Busca en todos los hijos recursivamente."""
        resultados: list[Archivo] = []
        if nombre.lower() in self._nombre.lower():
            resultados.append(self)
        for hijo in self._hijos:
            resultados.extend(hijo.buscar(nombre))
        return resultados

    def contar_archivos(self) -> int:
        """Cuenta solo las hojas (archivos simples)."""
        total = 0
        for hijo in self._hijos:
            if isinstance(hijo, ArchivoSimple):
                total += 1
            elif isinstance(hijo, Carpeta):
                total += hijo.contar_archivos()
        return total

    def __repr__(self):
        return f"Carpeta('{self._nombre}', {len(self._hijos)} hijos)"


# ──────────────────────────────────────────────
# Demo
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("   PATRÓN COMPOSITE — Sistema de Archivos")
    print("=" * 60)

    # ── Construir árbol de directorios ────────
    raiz = Carpeta("Proyectos")

    # Carpeta: proyecto_web
    web = Carpeta("proyecto_web")
    web.agregar(ArchivoSimple("index.py", 12))
    web.agregar(ArchivoSimple("config.txt", 3))
    web.agregar(ArchivoSimple("logo.png", 120))

    static = Carpeta("static")
    static.agregar(ArchivoSimple("styles.txt", 25))
    static.agregar(ArchivoSimple("app.py", 48))
    web.agregar(static)

    # Carpeta: proyecto_ml
    ml = Carpeta("proyecto_ml")
    ml.agregar(ArchivoSimple("modelo.py", 85))
    ml.agregar(ArchivoSimple("dataset.zip", 2048))
    ml.agregar(ArchivoSimple("reporte.pdf", 310))

    data = Carpeta("data")
    data.agregar(ArchivoSimple("train.zip", 512))
    data.agregar(ArchivoSimple("test.zip", 128))
    ml.agregar(data)

    # Archivo suelto en raíz
    raiz.agregar(web)
    raiz.agregar(ml)
    raiz.agregar(ArchivoSimple("README.txt", 5))

    # ── Mostrar estructura completa 
    print("\n--- Estructura del sistema de archivos ---")
    raiz.mostrar()

    # ── Tamaños 
    print("\n--- Tamaños ---")
    print(f"  proyecto_web: {web.tamaño()} KB")
    print(f"  proyecto_ml:  {ml.tamaño()} KB")
    print(f"  Total raíz:   {raiz.tamaño()} KB")

    # ── Conteo 
    print(f"\n  Archivos en raíz (recursivo): {raiz.contar_archivos()}")

    # ── Búsqueda 
    print("\n--- Búsqueda: archivos con '.py' ---")
    resultados = raiz.buscar(".py")
    for r in resultados:
        print(f"  Encontrado: {r.ruta()}")

    print("\n--- Búsqueda: 'zip' ---")
    resultados2 = raiz.buscar("zip")
    for r in resultados2:
        print(f"  Encontrado: {r.ruta()}")

    # ── Operación uniforme: hoja vs compuesto ─
    print("\n--- Tratamiento uniforme (hoja vs compuesto) ---")
    componentes: list[Archivo] = [
        ArchivoSimple("suelto.txt", 10),
        web,
        ml,
    ]
    for c in componentes:
        print(f"  {c.nombre:20s} → {c.tamaño():>6} KB")
