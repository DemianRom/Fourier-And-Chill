"""
fourier_engine.py - Cálculo simbólico de Series de Fourier.

Coeficientes trigonométricos mediante integración con SymPy:
    T = lim_sup - lim_inf,  omega = 2*pi/T
    a0 = (2/T) * integral(f, lim_inf, lim_sup)            [n = 0]
    an = (2/T) * integral(f*cos(n*w*x), lim_inf, lim_sup) [n = 1, 2, ..., N]
    bn = (2/T) * integral(f*sin(n*w*x), lim_inf, lim_sup) [n = 1, 2, ..., N]

La primera evaluación es siempre n=0 (término DC = a0/2).
Se retornan TODOS los coeficientes n=0..N (inclusive), incluyendo los nulos.

Equipo 7 - 5CM1 - ESCOM
    1. Romero Bautista Demian
    2. Linares Ojeda Carlos Elias
    3. Aparicio Arenas Victor Eduardo
    4. Gutiérrez Romero Omar José Eduardo
    5. Cardenaz Hernández Ximena
"""

import sympy as sp
import numpy as np
from sympy.utilities.lambdify import lambdify
from typing import Tuple, List, Optional

x = sp.Symbol('x')


def calcular_coeficientes(
    f_expr: sp.Expr,
    lim_inf: float,
    lim_sup: float,
    num_armonicos: int,
    T_periodo: float = None
) -> Tuple[sp.Expr, List[sp.Expr], List[sp.Expr], List[int]]:
    """
    Calcula los coeficientes de Fourier para n = 0, 1, 2, ..., N (inclusive).

    Usa integración simbólica con n como símbolo (fórmula cerrada),
    luego sustituye n = 1, 2, ..., N. Se retornan TODOS los términos,
    incluyendo los nulos, con índices consecutivos [1, 2, ..., N].

    Args:
        f_expr:        Expresión SymPy de la función f(x).
        lim_inf:       Límite inferior del intervalo.
        lim_sup:       Límite superior del intervalo.
        num_armonicos: N — número de armónicos; el conjunto evaluado es {a0, a1, ..., aN}.
        T_periodo:     Periodo de extensión. Si None, usa lim_sup - lim_inf.

    Returns:
        (a0, lista_an, lista_bn, indices)
        indices es siempre [1, 2, 3, ..., N].
        El conjunto evaluado completo es {n=0, 1, ..., N}.
    """
    T     = float(T_periodo) if T_periodo is not None else float(lim_sup - lim_inf)
    Ts    = sp.nsimplify(T, [sp.pi])
    omega = 2 * sp.pi / Ts

    # Límites exactos: SymPy produce nan al integrar Piecewise con floats.
    lim_inf_s = sp.nsimplify(lim_inf, [sp.pi])
    lim_sup_s = sp.nsimplify(lim_sup, [sp.pi])

    # Integración simbólica con n como símbolo -> fórmula cerrada an(n), bn(n)
    n_sym = sp.Symbol('n', integer=True, positive=True)

    integral_a0 = sp.integrate(f_expr, (x, lim_inf_s, lim_sup_s))
    a0 = sp.simplify(2 * integral_a0 / Ts)

    an_expr = sp.simplify(
        2 * sp.integrate(f_expr * sp.cos(n_sym * omega * x),
                         (x, lim_inf_s, lim_sup_s)) / Ts
    )
    bn_expr = sp.simplify(
        2 * sp.integrate(f_expr * sp.sin(n_sym * omega * x),
                         (x, lim_inf_s, lim_sup_s)) / Ts
    )

    # Sustituir n = 1, 2, ..., N (inclusive)
    # El conjunto evaluado es {0, 1, ..., N}: n=0 es el DC (a0/2),
    # los armónicos van de n=1 hasta n=N.
    lista_an = []
    lista_bn = []
    indices  = []

    for k in range(1, num_armonicos + 1):   # 1 .. N (inclusive)
        an = sp.re(an_expr.subs(n_sym, k))
        bn = sp.re(bn_expr.subs(n_sym, k))
        lista_an.append(an)
        lista_bn.append(bn)
        indices.append(k)

    return a0, lista_an, lista_bn, indices


def construir_serie_simbolica(
    a0: sp.Expr,
    lista_an: List[sp.Expr],
    lista_bn: List[sp.Expr],
    indices: List[int],
    lim_inf: float,
    lim_sup: float,
    T_periodo: float = None
) -> sp.Expr:
    """
    Construye la expresión simbólica:
        S(x) = a0/2 + sum_{n=1}^{N} ( an*cos(n*w*x) + bn*sin(n*w*x) )

    T_periodo permite especificar un periodo distinto al dominio de definición.
    """
    T     = float(T_periodo) if T_periodo is not None else float(lim_sup - lim_inf)
    Ts    = sp.nsimplify(T, [sp.pi])
    omega = 2 * sp.pi / Ts

    serie = a0 / 2
    for idx, (ak, bk) in enumerate(zip(lista_an, lista_bn)):
        n = indices[idx]
        serie += ak * sp.cos(n * omega * x)
        serie += bk * sp.sin(n * omega * x)

    return sp.expand(serie)


def vectorizar_funcion(expr: sp.Expr) -> callable:
    """
    Convierte una expresión SymPy en función NumPy vectorizada.

    Extrae la parte real del resultado para manejar residuos imaginarios
    que SymPy puede introducir al evaluar numéricamente.
    """
    try:
        f = lambdify(x, expr, modules=["numpy"])
        def f_real(xi):
            return float(np.real(f(xi)))
        return np.vectorize(f_real, otypes=[float])
    except Exception as e:
        raise ValueError(f"Error al vectorizar: {e}")


def evaluar_coeficiente(expr: sp.Expr) -> Optional[float]:
    """Evalúa una expresión SymPy a float. Retorna None si falla."""
    try:
        return float(complex(expr.evalf()).real)
    except Exception:
        return None