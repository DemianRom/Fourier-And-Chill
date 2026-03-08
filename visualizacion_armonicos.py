"""
visualizacion_armonicos.py - Análisis detallado de armónicos.

La serie se evalúa comenzando en n=0 (término DC = a0/2) y acumulando
n=0, n=0..1, n=0..2, ... hasta N. Todas las pestañas respetan este orden.

Equipo 7 - 5CM1 - ESCOM
    1. Romero Bautista Demian
    2. Linares Ojeda Carlos Elias
    3. Aparicio Arenas Victor Eduardo
    4. Gutiérrez Romero Omar José Eduardo
    5. Cardenaz Hernández Ximena
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib

from fourier_engine import evaluar_coeficiente

matplotlib.use('QtAgg')


class VentanaArmonicos(QDialog):
    """Diálogo modal con análisis gráfico de los armónicos de la serie."""

    def __init__(self, resultado, parent=None):
        super().__init__(parent)
        self.resultado = resultado
        self.setWindowTitle("Visualización de Armónicos — Serie de Fourier")
        self.setGeometry(150, 150, 1200, 800)
        self.aplicar_tema()
        self.init_ui()

    def aplicar_tema(self):
        self.setStyleSheet("""
            QDialog { background-color: #0d1117; }
            QTabWidget::pane { border: 1px solid #21262d; background-color: #161b22; }
            QTabBar::tab {
                background-color: #161b22; color: #8b949e;
                padding: 8px 15px; border: 1px solid #21262d; margin-right: 2px;
            }
            QTabBar::tab:selected { background-color: #238636; color: #ffffff; font-weight: bold; }
            QTabBar::tab:hover { background-color: #30363d; }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        tabs = QTabWidget()
        tabs.setFont(QFont("Segoe UI", 10))
        tabs.addTab(self.crear_tab_coeficientes(),  "Coeficientes")
        tabs.addTab(self.crear_tab_armonicos(),     "Armónicos Individuales")
        tabs.addTab(self.crear_tab_construccion(),  "Construcción Progresiva")
        layout.addWidget(tabs)

    # ------------------------------------------------------------------
    # Pestaña 1: Barras de coeficientes — incluye n=0 explícito
    # ------------------------------------------------------------------
    def crear_tab_coeficientes(self) -> QWidget:
        """Gráfica de barras: a0 en n=0, luego an y bn para n=1..N."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        figura = Figure(figsize=(10, 6), facecolor='#0d1117')
        canvas = FigureCanvasQTAgg(figura)
        layout.addWidget(canvas)

        a0       = self.resultado["a0"]
        lista_an = self.resultado["lista_an"]
        lista_bn = self.resultado["lista_bn"]
        indices  = self.resultado.get("indices", list(range(1, len(lista_an)+1)))
        N        = len(lista_an)

        val_a0  = evaluar_coeficiente(a0) or 0
        vals_an = [evaluar_coeficiente(an) or 0 for an in lista_an]
        vals_bn = [evaluar_coeficiente(bn) or 0 for bn in lista_bn]

        ax1 = figura.add_subplot(311)
        ax2 = figura.add_subplot(312)
        ax3 = figura.add_subplot(313)

        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor('#161b22')
            ax.tick_params(colors='#e6edf3', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('#30363d')
            ax.grid(True, color='#21262d', linewidth=0.5, alpha=0.5)
            ax.axhline(0, color='#30363d', linewidth=0.8)

        # n=0: a0 y a0/2
        ax1.bar([0], [val_a0],     color='#f78166', width=0.4, label='a₀')
        ax1.bar([0.5], [val_a0/2], color='#ffa657', width=0.4, label='a₀/2 (DC)')
        ax1.set_ylabel('Valor', color='#e6edf3', fontsize=9)
        ax1.set_title(f'n=0  →  a₀ = {val_a0:.6f}   |   a₀/2 = {val_a0/2:.6f}',
                      color='#f78166', fontsize=10, fontweight='bold')
        ax1.set_xticks([0, 0.5])
        ax1.set_xticklabels(['a₀', 'a₀/2'])
        ax1.legend(fontsize=8, facecolor='#161b22', edgecolor='#30363d', labelcolor='#e6edf3')

        # n=1..N: an
        colores_an = ['#8b949e' if abs(v) < 1e-10 else '#58a6ff' for v in vals_an]
        ax2.bar(indices[:30], vals_an[:30], color=colores_an[:30], width=0.7, alpha=0.9)
        ax2.set_xlabel('n', color='#e6edf3', fontsize=9)
        ax2.set_ylabel('aₙ', color='#e6edf3', fontsize=9)
        ax2.set_title('Coeficientes aₙ  (coseno)  —  gris = nulo',
                      color='#58a6ff', fontsize=10, fontweight='bold')
        ax2.set_xticks(indices[:30])

        # n=1..N: bn
        colores_bn = ['#8b949e' if abs(v) < 1e-10 else '#bc8cff' for v in vals_bn]
        ax3.bar(indices[:30], vals_bn[:30], color=colores_bn[:30], width=0.7, alpha=0.9)
        ax3.set_xlabel('n', color='#e6edf3', fontsize=9)
        ax3.set_ylabel('bₙ', color='#e6edf3', fontsize=9)
        ax3.set_title('Coeficientes bₙ  (seno)  —  gris = nulo',
                      color='#bc8cff', fontsize=10, fontweight='bold')
        ax3.set_xticks(indices[:30])

        figura.tight_layout()
        canvas.draw()
        return widget

    # ------------------------------------------------------------------
    # Pestaña 2: Armónicos individuales — usa índices reales
    # ------------------------------------------------------------------
    def crear_tab_armonicos(self) -> QWidget:
        """Muestra cada armónico por separado usando los índices reales n."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        figura = Figure(figsize=(10, 8), facecolor='#0d1117')
        canvas = FigureCanvasQTAgg(figura)
        layout.addWidget(canvas)

        L        = self.resultado["L"]
        lista_an = self.resultado["lista_an"]
        lista_bn = self.resultado["lista_bn"]
        indices  = self.resultado.get("indices", list(range(1, len(lista_an)+1)))
        a0       = self.resultado["a0"]
        val_a0   = evaluar_coeficiente(a0) or 0

        # Mostrar: n=0 (DC) + primeros 4 armónicos
        num_armonicos_mostrar = min(4, len(lista_an))
        num_filas = 1 + num_armonicos_mostrar   # fila extra para n=0

        x_vals = np.linspace(-2*L, 2*L, 1000)
        omega  = np.pi / L   # 2pi/(2L) = pi/L

        def estilo_ax(ax, titulo, color):
            ax.set_facecolor('#161b22')
            ax.tick_params(colors='#e6edf3', labelsize=7)
            for spine in ax.spines.values():
                spine.set_color('#30363d')
            ax.grid(True, color='#21262d', linewidth=0.4, alpha=0.5)
            ax.axhline(0, color='#30363d', linewidth=0.6)
            ax.set_title(titulo, color=color, fontsize=8, fontweight='bold', pad=2)
            ax.set_xlim(-2*L, 2*L)

        # Fila 0: término DC (n=0)
        ax0 = figura.add_subplot(num_filas, 1, 1)
        y_dc = np.full_like(x_vals, val_a0 / 2)
        ax0.axhline(val_a0/2, color='#f78166', linewidth=2.0, label=f'a₀/2 = {val_a0/2:.4f}')
        ax0.fill_between(x_vals, 0, y_dc, alpha=0.15, color='#f78166')
        estilo_ax(ax0, f'n = 0  →  a₀/2 = {val_a0/2:.6f}  (término DC, línea constante)', '#f78166')
        ax0.legend(loc='upper right', fontsize=7, facecolor='#161b22',
                   edgecolor='#30363d', labelcolor='#e6edf3')
        ax0.set_ylabel('n=0', color='#e6edf3', fontsize=8, fontweight='bold')

        # Filas 1..num_armonicos_mostrar: n=1,2,...
        for fila, k in enumerate(range(num_armonicos_mostrar)):
            ax = figura.add_subplot(num_filas, 1, fila + 2)
            n  = indices[k]
            an = evaluar_coeficiente(lista_an[k]) or 0
            bn = evaluar_coeficiente(lista_bn[k]) or 0

            y_cos   = an * np.cos(n * omega * x_vals)
            y_sin   = bn * np.sin(n * omega * x_vals)
            y_total = y_cos + y_sin

            ax.plot(x_vals, y_cos,   color='#58a6ff', linewidth=1.0, alpha=0.7,
                    label=f'a{n}·cos({n}ωx) = {an:.3f}·cos({n}ωx)')
            ax.plot(x_vals, y_sin,   color='#bc8cff', linewidth=1.0, alpha=0.7,
                    label=f'b{n}·sin({n}ωx) = {bn:.3f}·sin({n}ωx)')
            ax.plot(x_vals, y_total, color='#f78166', linewidth=1.5, zorder=3, label='Suma')

            titulo = (f'n = {n}  →  a{n} = {an:.4f}  |  b{n} = {bn:.4f}')
            estilo_ax(ax, titulo, '#e6edf3')
            ax.set_ylabel(f'n={n}', color='#e6edf3', fontsize=8, fontweight='bold')
            ax.legend(loc='upper right', fontsize=6, facecolor='#161b22',
                      edgecolor='#30363d', labelcolor='#e6edf3')

            if fila == 0:
                ax.set_title(f'Armónicos Individuales — n = {n}  →  {titulo}',
                             color='#58a6ff', fontsize=9, fontweight='bold', pad=2)
            if fila == num_armonicos_mostrar - 1:
                ax.set_xlabel('x', color='#e6edf3', fontsize=8)

        figura.tight_layout(pad=0.6)
        canvas.draw()
        return widget

    # ------------------------------------------------------------------
    # Pestaña 3: Construcción progresiva — empieza en n=0
    # ------------------------------------------------------------------
    def crear_tab_construccion(self) -> QWidget:
        """
        Muestra la acumulación paso a paso:
            Paso 0: S(x) = a0/2
            Paso 1: S(x) = a0/2 + a1·cos + b1·sin
            Paso 2: S(x) = a0/2 + … + a2·cos + b2·sin
            …
        """
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        figura = Figure(figsize=(10, 9), facecolor='#0d1117')
        canvas = FigureCanvasQTAgg(figura)
        layout.addWidget(canvas)

        lim_inf       = self.resultado.get("lim_inf", 0.0)
        lim_sup       = self.resultado.get("lim_sup", 1.0)
        a0            = self.resultado["a0"]
        lista_an      = self.resultado["lista_an"]
        lista_bn      = self.resultado["lista_bn"]
        indices       = self.resultado.get("indices", list(range(1, len(lista_an)+1)))
        func_original = self.resultado["func_original"]
        T_periodo     = self.resultado.get("T_periodo")

        T     = float(T_periodo) if T_periodo is not None else (lim_sup - lim_inf)
        omega = 2 * np.pi / T

        x_vals = np.linspace(lim_inf - T, lim_sup + T, 1500)

        # Función original extendida periódicamente
        x_base = np.linspace(lim_inf, lim_sup, 1000, endpoint=False)
        try:
            y_base = func_original(x_base).astype(float)
        except Exception:
            y_base = np.array([float(func_original(xi)) for xi in x_base])
        x_mapped   = np.mod(x_vals - lim_inf, T) + lim_inf
        y_original = np.interp(x_mapped, x_base, y_base)

        val_a0 = evaluar_coeficiente(a0) or 0
        N_total = len(lista_an)  # = N-1 armónicos reales (sin el DC)

        # Pasos a mostrar: 0 (solo DC), luego índices dentro de {0..N-1}
        # El conjunto evaluado es {0,1,...,N-1}: el slider N indica cuántos
        # elementos tiene el conjunto, no el índice máximo.
        candidatos = sorted(set([0, 1, 3, 5, 10, N_total]))
        pasos      = [p for p in candidatos if p <= N_total]
        num_pasos  = len(pasos)

        for fila, N_paso in enumerate(pasos):
            ax = figura.add_subplot(num_pasos, 1, fila + 1)
            ax.set_facecolor('#161b22')
            ax.tick_params(colors='#e6edf3', labelsize=7)
            for spine in ax.spines.values():
                spine.set_color('#30363d')
            ax.grid(True, color='#21262d', linewidth=0.4, alpha=0.5)
            ax.axhline(0, color='#30363d', linewidth=0.6)

            # Construir suma hasta n = indices[N_paso-1]  (N_paso=0 → solo DC)
            y_serie = np.full_like(x_vals, val_a0 / 2)
            for k in range(N_paso):
                an = evaluar_coeficiente(lista_an[k]) or 0
                bn = evaluar_coeficiente(lista_bn[k]) or 0
                n  = indices[k]
                y_serie += an * np.cos(n * omega * x_vals)
                y_serie += bn * np.sin(n * omega * x_vals)

            ax.plot(x_vals, y_original, color='#58a6ff', linewidth=1.5,
                    alpha=0.45, label='f(x) original')
            ax.plot(x_vals, y_serie, color='#f78166', linewidth=1.5,
                    linestyle='--', label=f'S(x)  n=0…{indices[N_paso-1] if N_paso>0 else 0}')

            # Etiqueta del eje Y con la secuencia de n usados
            if N_paso == 0:
                label_y = 'n=0'
                titulo_paso = 'n = 0  →  S(x) = a₀/2  (solo término DC)'
            else:
                ns_usados = [0] + [indices[k] for k in range(N_paso)]
                label_y = f'n=0…{indices[N_paso-1]}'
                titulo_paso = f'n = 0, {", ".join(str(indices[k]) for k in range(N_paso))}'

            ax.set_ylabel(label_y, color='#e6edf3', fontsize=8, fontweight='bold')
            ax.legend(loc='upper right', fontsize=7, facecolor='#161b22',
                      edgecolor='#30363d', labelcolor='#e6edf3')
            ax.set_xlim(lim_inf - T, lim_sup + T)

            n_ultimo = indices[N_paso-1] if N_paso > 0 else 0
            titulo_completo = (f'n ∈ {{0}} → solo DC'
                               if N_paso == 0
                               else f'n ∈ {{0, 1, ..., {n_ultimo}}}  →  {N_paso} armónico(s) + DC')
            if fila == 0:
                ax.set_title(f'Construcción Progresiva  |  {titulo_completo}',
                             color='#f78166', fontsize=9, fontweight='bold')
            else:
                ax.set_title(titulo_completo, color='#8b949e', fontsize=8)

            if fila == num_pasos - 1:
                ax.set_xlabel('x', color='#e6edf3', fontsize=8)

        figura.tight_layout(pad=0.5)
        canvas.draw()
        return widget