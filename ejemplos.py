"""
ejemplos.py - Senales predefinidas para la calculadora de Fourier.

Incluye señales clasicas de procesamiento de señales y sistemas.

Equipo 7 - 5CM1 - ESCOM
    1. Romero Bautista Demian
    2. Linares Ojeda Carlos Elias
    3. Aparicio Arenas Victor Eduardo
    4. Gutiérrez Romero Omar José Eduardo
    5. Cardenaz Hernández Ximena
"""

from typing import Dict

EJEMPLOS: Dict[str, Dict] = {

    # ── Señales clásicas de simetría ─────────────────────────────────────────

    "Onda Cuadrada": {
        "funcion": "Piecewise((-1, (x >= -pi) & (x < 0)), (1, (x >= 0) & (x <= pi)), (0, True))",
        "descripcion": (
            "Amplitud unitaria, simetria impar. "
            "Solo armonicos impares de seno: bn = 4/(n*pi). "
            "Ejemplo clasico del Fenomeno de Gibbs (sobreimpulso ~9% en discontinuidades)."
        ),
    },

    "Diente de Sierra": {
        "funcion": "Piecewise((x, (x >= -pi) & (x <= pi)), (0, True))",
        "descripcion": (
            "f(x) = x, simetria impar. "
            "Coeficientes bn = 2*(-1)^(n+1)/n, decaen como 1/n (convergencia lenta). "
            "Contiene todos los armonicos impares y pares de seno."
        ),
    },

    "Triangular": {
        "funcion": "Piecewise((x + pi, (x >= -pi) & (x < 0)), (-x + pi, (x >= 0) & (x <= pi)), (0, True))",
        "descripcion": (
            "Simetria par. Solo armonicos coseno: an = -8/(pi^2 * n^2) para n impar. "
            "Coeficientes decaen como 1/n^2, convergencia mas rapida que la onda cuadrada. "
            "Derivada de la onda triangular es una onda cuadrada."
        ),
    },

    "Pulso Rectangular": {
        "funcion": "Piecewise((1, (x >= -1) & (x <= 1)), (0, True))",
        "descripcion": (
            "Pulso de duracion 2 centrado en el origen, ciclo de trabajo 50%. "
            "Funcion par, solo coeficientes an (bn = 0). "
            "Espectro tipo sinc: an = 2*sin(n*pi/2) / (n*pi)."
        ),
    },

    # ── Señales de rectificación ─────────────────────────────────────────────

    "Seno Media Onda": {
        "funcion": "Piecewise((sin(x), (x >= 0) & (x < pi)), (0, (x >= -pi) & (x <= 0)), (0, True))",
        "descripcion": (
            "Rectificador de media onda: solo el semiciclo positivo del seno. "
            "Periodo 2*pi. Contiene componente DC, armonico fundamental y "
            "solo armonicos pares de coseno. Modelo de rectificador monofasico."
        ),
    },

    "Seno Onda Completa": {
        "funcion": "Piecewise((sin(x), (x >= 0) & (x < pi)), (-sin(x), (x >= -pi) & (x <= 0)), (0, True))",
        "descripcion": (
            "Rectificador de onda completa: |sin(x)|. "
            "Periodo efectivo pi (mitad del seno). "
            "Solo armonicos pares de coseno, sin componente de seno. "
            "Modelo de rectificador de puente. a0 = 4/pi."
        ),
    },

    # ── Señales no sinusoidales importantes ─────────────────────────────────

    "Trapezoidal": {
        "funcion": "Piecewise((x+2, (x >= -2) & (x < -1)), (1, (x >= -1) & (x < 1)), (-x+2, (x >= 1) & (x <= 2)), (0, True))",
        "descripcion": (
            "Pulso trapezoidal: flancos lineales de duracion 1, tope plano de duracion 2. "
            "Funcion par, solo cosenos. Espectro decae como 1/n^2. "
            "Aproximacion realista de pulsos digitales con tiempos de subida finitos."
        ),
    },

    "Rampa Periodica": {
        "funcion": "Piecewise((x, (x >= 0) & (x <= 1)), (0, True))",
        "descripcion": (
            "Rampa lineal de [0,1) seguida de caida abrupta a 0. "
            "Contiene componente DC = 1/2 y todos los armonicos. "
            "bn = -1/(n*pi). Señal asimetrica sin simetria par ni impar."
        ),
    },

    "Exponencial Decreciente": {
        "funcion": "Piecewise((exp(-3*x), (x >= 0) & (x <= 1)), (0, True))",
        "descripcion": (
            "Pulso exponencial f(x) = e^(-3x) en [0,1). "
            "Modela respuesta al impulso de sistemas de primer orden (RC, RL). "
            "Espectro continuo y suave; util para ilustrar la relacion "
            "entre decaimiento temporal y ancho de banda espectral."
        ),
    },

    "Pulso Asimetrico": {
        "funcion": "Piecewise((1, (x >= 0) & (x < 1)), (0, (x >= -3) & (x <= 0)), (0, True))",
        "descripcion": (
            "Pulso unitario de ciclo de trabajo 25% (ancho 1 de periodo 4). "
            "Sin simetria par ni impar: contiene an y bn simultaneamente. "
            "Ilustra como el ciclo de trabajo afecta la distribucion espectral: "
            "nulos del espectro en multiplos de 1/d donde d es el ciclo de trabajo."
        ),
    },
}


def obtener_nombres() -> list:
    """Retorna lista de nombres de ejemplos disponibles."""
    return list(EJEMPLOS.keys())


def obtener_ejemplo(nombre: str) -> dict:
    """
    Obtiene los datos de un ejemplo por nombre.

    Args:
        nombre: Nombre de la señal (ej: 'Onda Cuadrada')

    Returns:
        Dict con keys 'funcion' y 'descripcion', o dict vacio si no existe.
    """
    return EJEMPLOS.get(nombre, {"funcion": "", "descripcion": ""})