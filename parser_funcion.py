"""
parser_funcion.py - Parser seguro de expresiones matematicas con SymPy.

Convierte cadenas de texto a expresiones SymPy usando eval() con entorno controlado.

Equipo 7 - 5CM1 - ESCOM
    1. Romero Bautista Demian
    2. Linares Ojeda Carlos Elias
    3. Aparicio Arenas Victor Eduardo
    4. Gutiérrez Romero Omar José Eduardo
    5. Cardenaz Hernández Ximena
"""

import sympy as sp
from sympy import (
    Symbol, pi, E, sin, cos, tan, exp, log, sqrt, Abs,
    Piecewise, And, Or, Rational, oo, Heaviside
)

x = Symbol('x')

ENTORNO_SYMPY = {
    "x": x,
    "pi": pi,
    "e": E,
    "E": E,
    "oo": oo,
    "sin": sin,
    "cos": cos,
    "tan": tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "exp": exp,
    "log": log,
    "ln": log,
    "sqrt": sqrt,
    "Abs": Abs,
    "abs": Abs,
    "Heaviside": Heaviside,
    "H": Heaviside,
    "Piecewise": Piecewise,
    "And": And,
    "Or": Or,
    "Rational": Rational,
}


def parsear_funcion(texto: str) -> sp.Expr:
    """
    Parsea string a expresión SymPy de forma segura.
    
    Args:
        texto: Expresión matemática como string (ej: "sin(pi*x)")
    
    Returns:
        Expresión SymPy
    
    Raises:
        SyntaxError: Si la sintaxis es inválida
        ValueError: Si contiene nombres no reconocidos
    
    Nota: Convierte ^ a ** automáticamente.
    """
    if not texto or not texto.strip():
        raise ValueError("La expresión está vacía")
    
    texto_procesado = texto.strip().replace("^", "**")
    
    try:
        expresion = eval(texto_procesado, {"__builtins__": {}}, ENTORNO_SYMPY)
    except SyntaxError as e:
        raise SyntaxError(f"Sintaxis inválida: {e}")
    except NameError as e:
        raise ValueError(f"Nombre no reconocido: {e}")
    except Exception as e:
        raise ValueError(f"Error al parsear: {e}")
    
    if not isinstance(expresion, (sp.Expr, sp.Basic)):
        raise ValueError("No es una expresión SymPy válida")
    
    return expresion


def validar_funcion(texto: str) -> tuple:
    """
    Valida si el texto es parseable sin lanzar excepciones.
    
    Args:
        texto: Expresión a validar
    
    Returns:
        (es_valida: bool, mensaje_error: str)
    """
    try:
        parsear_funcion(texto)
        return True, ""
    except Exception as e:
        return False, str(e)