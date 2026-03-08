"""
main.py - Calculadora de Series de Fourier Trigonométricas (PyQt6).

Ventana principal dividida en panel de controles y panel de visualización.
Integra: fourier_engine, piecewise_widget, parser_funcion, ejemplos.

Equipo 7 - 5CM1 - ESCOM
    1. Romero Bautista Demian
    2. Linares Ojeda Carlos Elias
    3. Aparicio Arenas Victor Eduardo
    4. Gutiérrez Romero Omar José Eduardo
    5. Cardenaz Hernández Ximena
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QTextEdit, QGroupBox,
    QGridLayout, QSplitter, QMessageBox, QLineEdit, QSpinBox,
    QDoubleSpinBox, QRadioButton, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor

import numpy as np
import sympy as sp
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('QtAgg')

from fourier_engine import (
    calcular_coeficientes, construir_serie_simbolica,
    vectorizar_funcion, evaluar_coeficiente
)
from parser_funcion import parsear_funcion, validar_funcion
from ejemplos import obtener_nombres, obtener_ejemplo
from piecewise_widget import PiecewiseWidget


class VentanaPrincipal(QMainWindow):
    """Ventana principal. Gestiona la interfaz, el flujo de cálculo y la graficación."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Series de Fourier — Equipo 7, 5CM1 — ESCOM")
        self.setGeometry(100, 100, 1400, 900)
        
        self.resultado_actual = None
        self.timer_slider = QTimer()
        self.timer_slider.setSingleShot(True)
        self.timer_slider.timeout.connect(self.recalcular_grafica_rapido)
        
        self.aplicar_tema_oscuro()
        self.init_ui()
    
    def aplicar_tema_oscuro(self):
        """Aplica el stylesheet global de tema oscuro."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QLabel {
                color: #e6edf3;
                font-size: 10pt;
            }
            QGroupBox {
                color: #58a6ff;
                font-size: 11pt;
                font-weight: bold;
                border: 1px solid #21262d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1a7f37;
            }
            QLineEdit, QTextEdit {
                background-color: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New', monospace;
                font-size: 10pt;
            }
            QComboBox {
                background-color: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 3px;
                padding: 5px;
                font-size: 10pt;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #58a6ff;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                selection-background-color: #21262d;
                selection-color: #58a6ff;
                outline: none;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #21262d;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #58a6ff;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #79c0ff;
            }
            QSpinBox, QDoubleSpinBox {
                background-color: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 3px;
                padding: 5px;
            }
        """)
    
    def init_ui(self):
        """Construye el layout principal: panel de controles (izq.) y visualización (der.)."""
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        
        layout_principal = QHBoxLayout()
        widget_central.setLayout(layout_principal)
        
        # ── Panel izquierdo: Controles ────────────────────────────────────────
        panel_controles = self.crear_panel_controles()
        layout_principal.addWidget(panel_controles, 1)
        
        # ── Panel derecho: Gráfica y resultados ───────────────────────────────
        panel_derecho = self.crear_panel_derecho()
        layout_principal.addWidget(panel_derecho, 3)
    
    def crear_panel_controles(self) -> QWidget:
        """Panel izquierdo: ejemplos, función a trozos, teclado matemático y parámetros."""
        panel_scroll = QScrollArea()
        panel_scroll.setWidgetResizable(True)
        panel_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        panel_scroll.setStyleSheet("""
            QScrollArea { background-color: #0d1117; border: none; }
            QScrollArea > QWidget > QWidget { background-color: #0d1117; }
            QScrollBar:vertical {
                background: #161b22; width: 8px; border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #30363d; border-radius: 4px; min-height: 20px;
            }
        """)
        panel = QWidget()
        panel.setStyleSheet("background-color: #0d1117;")
        layout = QVBoxLayout()
        panel.setLayout(layout)
        
        # ── Selector de ejemplos predefinidos ─────────────────────────────────
        grupo_ejemplos = QGroupBox("Ejemplos Predefinidos")
        layout_ejemplos = QVBoxLayout()
        
        self.combo_ejemplos = QComboBox()
        self.combo_ejemplos.addItem("-- Seleccionar ejemplo --")
        self.combo_ejemplos.addItems(obtener_nombres())
        self.combo_ejemplos.addItem("Personalizada")
        self.combo_ejemplos.setCurrentIndex(0)
        self.combo_ejemplos.currentTextChanged.connect(self.cargar_ejemplo)
        layout_ejemplos.addWidget(self.combo_ejemplos)
        
        self.label_desc_ejemplo = QLabel()
        self.label_desc_ejemplo.setWordWrap(True)
        self.label_desc_ejemplo.setStyleSheet("color: #8b949e; font-size: 9pt;")
        layout_ejemplos.addWidget(self.label_desc_ejemplo)
        
        grupo_ejemplos.setLayout(layout_ejemplos)
        layout.addWidget(grupo_ejemplos)
        
        # ── Widget de función a trozos ────────────────────────────────────────
        grupo_funcion = QGroupBox("Definición de Función")
        layout_funcion = QVBoxLayout()
        
        self.piecewise_widget = PiecewiseWidget()
        layout_funcion.addWidget(self.piecewise_widget)
        
        # Botón para aplicar la función del widget al QTextEdit
        btn_aplicar_widget = QPushButton("Aplicar funcion definida arriba")
        btn_aplicar_widget.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                padding: 6px;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        btn_aplicar_widget.clicked.connect(self.aplicar_funcion_widget)
        layout_funcion.addWidget(btn_aplicar_widget)
        
        # Campo de texto alternativo (para edición manual)
        label_sintaxis = QLabel("Sintaxis SymPy generada:")
        label_sintaxis.setStyleSheet("color: #8b949e; font-size: 9pt; margin-top: 5px;")
        layout_funcion.addWidget(label_sintaxis)
        
        self.texto_funcion = QTextEdit()
        self.texto_funcion.setMaximumHeight(60)
        self.texto_funcion.setPlaceholderText("Piecewise((expr1, cond1), (expr2, cond2), ...)")
        self.texto_funcion.textChanged.connect(self.validar_funcion_tiempo_real)
        layout_funcion.addWidget(self.texto_funcion)
        
        # Label de validación
        self.label_validacion = QLabel("")
        self.label_validacion.setStyleSheet("font-size: 9pt; padding: 3px;")
        layout_funcion.addWidget(self.label_validacion)
        
        grupo_funcion.setLayout(layout_funcion)
        layout.addWidget(grupo_funcion)
        
        # ── Teclado matemático ────────────────────────────────────────────────
        grupo_teclado = QGroupBox("Teclado Matemático")
        layout_teclado = QGridLayout()
        
        simbolos = [
            ("π", "pi"), ("e", "E"), ("sin", "sin("),
            ("cos", "cos("), ("tan", "tan("), ("exp", "exp("),
            ("√", "sqrt("), ("ln", "log("), ("|x|", "Abs("),
            ("x²", "x**2"), ("**", "**"), ("&", " & "),
        ]
        
        fila, col = 0, 0
        for texto, insercion in simbolos:
            btn = QPushButton(texto)
            btn.setMaximumWidth(70)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #21262d;
                    color: #e6edf3;
                    padding: 5px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #30363d;
                }
            """)
            btn.clicked.connect(lambda checked, ins=insercion: self.insertar_simbolo(ins))
            layout_teclado.addWidget(btn, fila, col)
            col += 1
            if col > 2:
                col = 0
                fila += 1
        
        grupo_teclado.setLayout(layout_teclado)
        layout.addWidget(grupo_teclado)
        
        # ── Parámetros: periodo personalizable y N ───────────────────────────
        grupo_parametros = QGroupBox("Parámetros")
        layout_params = QVBoxLayout()
        
        # Control de periodo
        label_periodo = QLabel("Periodo de extensión:")
        label_periodo.setStyleSheet("color: #e6edf3; font-size: 10pt; font-weight: bold;")
        layout_params.addWidget(label_periodo)
        
        # Radio: Periodo = dominio (extensión periódica normal)
        self.radio_periodo_dominio = QRadioButton("Mismo periodo que el dominio (periódica clásica)")
        self.radio_periodo_dominio.setChecked(True)  # Por defecto
        self.radio_periodo_dominio.setStyleSheet("color: #e6edf3; font-size: 9pt;")
        self.radio_periodo_dominio.toggled.connect(self.actualizar_estado_periodo)
        layout_params.addWidget(self.radio_periodo_dominio)
        
        # Radio: Periodo infinito
        self.radio_periodo_infinito = QRadioButton("Periodo infinito (f(x) = 0 fuera del dominio)")
        self.radio_periodo_infinito.setStyleSheet("color: #e6edf3; font-size: 9pt;")
        self.radio_periodo_infinito.toggled.connect(self.actualizar_estado_periodo)
        layout_params.addWidget(self.radio_periodo_infinito)
        
        # Radio: Periodo personalizado
        layout_custom = QHBoxLayout()
        self.radio_periodo_custom = QRadioButton("Periodo personalizado:")
        self.radio_periodo_custom.setStyleSheet("color: #e6edf3; font-size: 9pt;")
        self.radio_periodo_custom.toggled.connect(self.actualizar_estado_periodo)
        layout_custom.addWidget(self.radio_periodo_custom)
        
        self.spin_periodo_custom = QDoubleSpinBox()
        self.spin_periodo_custom.setRange(0.01, 1000.0)
        self.spin_periodo_custom.setValue(6.28318531)  # 2π por defecto
        self.spin_periodo_custom.setDecimals(8)
        self.spin_periodo_custom.setSingleStep(0.1)
        self.spin_periodo_custom.setEnabled(False)  # Deshabilitado inicialmente
        self.spin_periodo_custom.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #161b22;
                color: #e6edf3;
                border: 1px solid #30363d;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        layout_custom.addWidget(self.spin_periodo_custom)
        layout_params.addLayout(layout_custom)
        
        # Número de armónicos N
        label_n = QLabel("Número de armónicos N:")
        layout_params.addWidget(label_n)
        
        self.slider_n = QSlider(Qt.Orientation.Horizontal)
        self.slider_n.setRange(1, 100)
        self.slider_n.setValue(5)
        self.slider_n.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_n.setTickInterval(10)
        self.slider_n.valueChanged.connect(self.slider_n_cambiado)
        layout_params.addWidget(self.slider_n)
        
        self.label_n_valor = QLabel("N = 5")
        self.label_n_valor.setStyleSheet("color: #58a6ff; font-size: 11pt; font-weight: bold;")
        self.label_n_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_params.addWidget(self.label_n_valor)
        
        grupo_parametros.setLayout(layout_params)
        layout.addWidget(grupo_parametros)
        
        # ── Botón calcular ────────────────────────────────────────────────────
        self.btn_calcular = QPushButton("Calcular Serie de Fourier")
        self.btn_calcular.setStyleSheet("""
            QPushButton {
                background-color: #1f6feb;
                padding: 12px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #388bfd;
            }
        """)
        self.btn_calcular.clicked.connect(self.calcular_fourier)
        layout.addWidget(self.btn_calcular)
        
        layout.addStretch()
        
        panel_scroll.setWidget(panel)
        return panel_scroll
    
    def crear_panel_derecho(self) -> QWidget:
        """Panel derecho: canvas matplotlib, slider de armónicos y área de coeficientes."""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # ── Área de gráfica ───────────────────────────────────────────────────
        grupo_grafica = QGroupBox("Visualización")
        layout_grafica = QVBoxLayout()
        
        self.figura = Figure(figsize=(10, 6), facecolor='#0d1117')
        self.canvas = FigureCanvasQTAgg(self.figura)
        self.canvas.setStyleSheet("background-color: #0d1117;")
        layout_grafica.addWidget(self.canvas)
        
        # Slider para ajuste dinámico de N en la gráfica
        layout_slider_grafica = QHBoxLayout()
        label_slider = QLabel("Armónicos en gráfica:")
        self.slider_n_grafica = QSlider(Qt.Orientation.Horizontal)
        self.slider_n_grafica.setRange(1, 100)
        self.slider_n_grafica.setValue(5)
        self.slider_n_grafica.setEnabled(False)
        self.slider_n_grafica.valueChanged.connect(self.slider_grafica_cambiado)
        self.label_n_grafica = QLabel("N = 5")
        self.label_n_grafica.setStyleSheet("color: #f78166; font-weight: bold;")
        
        layout_slider_grafica.addWidget(label_slider)
        layout_slider_grafica.addWidget(self.slider_n_grafica, 1)
        layout_slider_grafica.addWidget(self.label_n_grafica)
        layout_grafica.addLayout(layout_slider_grafica)
        
        grupo_grafica.setLayout(layout_grafica)
        layout.addWidget(grupo_grafica, 2)
        
        # ── Área de resultados (coeficientes) ─────────────────────────────────
        grupo_resultados = QGroupBox("Coeficientes de Fourier")
        layout_resultados = QVBoxLayout()
        
        self.texto_resultados = QTextEdit()
        self.texto_resultados.setReadOnly(True)
        self.texto_resultados.setStyleSheet("""
            QTextEdit {
                background-color: #161b22;
                color: #e6edf3;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        layout_resultados.addWidget(self.texto_resultados)
        
        grupo_resultados.setLayout(layout_resultados)
        layout.addWidget(grupo_resultados, 1)
        
        # Botón para ver armónicos detallados
        self.btn_ver_armonicos = QPushButton("Ver Armónicos Detallados")
        self.btn_ver_armonicos.setEnabled(False)
        self.btn_ver_armonicos.setStyleSheet("""
            QPushButton {
                background-color: #6e40aa;
                padding: 10px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #8c55d1;
            }
            QPushButton:disabled {
                background-color: #30363d;
                color: #6e7681;
            }
        """)
        self.btn_ver_armonicos.clicked.connect(self.abrir_ventana_armonicos)
        layout.addWidget(self.btn_ver_armonicos)
        
        return widget
    
    def abrir_ventana_armonicos(self):
        """Abre VentanaArmonicos con el resultado actual."""
        if not self.resultado_actual:
            return
        
        from visualizacion_armonicos import VentanaArmonicos
        ventana = VentanaArmonicos(self.resultado_actual, self)
        ventana.exec()
    
    def actualizar_estado_periodo(self):
        """Sincroniza el spinbox de periodo personalizado y el preview de trozos."""
        self.spin_periodo_custom.setEnabled(self.radio_periodo_custom.isChecked())
        self.piecewise_widget.actualizar_modo_periodo(self.radio_periodo_infinito.isChecked())
        self.actualizar_info_periodo()
    
    def actualizar_info_periodo(self):
        pass
    
    def insertar_simbolo(self, simbolo: str):
        """Inserta símbolo en el campo de tramo activo o en el QTextEdit de sintaxis."""
        if not self.piecewise_widget.insertar_en_campo_activo(simbolo):
            cursor = self.texto_funcion.textCursor()
            cursor.insertText(simbolo)
            self.texto_funcion.setFocus()
    
    def validar_funcion_tiempo_real(self):
        """Valida la sintaxis de la función y actualiza el indicador de estado."""
        texto = self.texto_funcion.toPlainText().strip()
        if not texto:
            self.label_validacion.setText("")
            return
        
        es_valida, msg_error = validar_funcion(texto)
        if es_valida:
            self.label_validacion.setText("[OK] Sintaxis válida")
            self.label_validacion.setStyleSheet("color: #3fb950; font-size: 9pt; padding: 3px;")
        else:
            self.label_validacion.setText(f"[ERROR] {msg_error[:80]}")
            self.label_validacion.setStyleSheet("color: #f85149; font-size: 9pt; padding: 3px;")
    
    def slider_n_cambiado(self, valor: int):
        """Actualiza la etiqueta N al mover el slider."""
        self.label_n_valor.setText(f"N = {valor}")
    
    def slider_grafica_cambiado(self, valor: int):
        """Actualiza la gráfica al mover el slider (debounce 200 ms)."""
        self.label_n_grafica.setText(f"N = {valor}")
        self.timer_slider.start(200)
    
    def aplicar_funcion_widget(self):
        """Genera la sintaxis Piecewise del widget y la vuelca en el QTextEdit."""
        periodo_infinito = self.radio_periodo_infinito.isChecked()
        sintaxis = self.piecewise_widget.generar_piecewise(periodo_infinito)
        
        if sintaxis:
            self.texto_funcion.blockSignals(True)
            self.texto_funcion.setPlainText(sintaxis)
            self.texto_funcion.blockSignals(False)
            self.validar_funcion_tiempo_real()
        else:
            QMessageBox.warning(self, "Advertencia", 
                              "Define al menos un tramo en el widget de arriba")
    
    def extraer_periodo_de_funcion(self, texto_func: str) -> tuple:
        """
        Infiere lim_inf, lim_sup y L = T/2 a partir de la sintaxis Piecewise.

        Busca los valores numéricos en las condiciones (x >= NUM) / (x < NUM),
        reemplazando 'pi' por su valor decimal. Si no encuentra al menos dos
        límites distintos, usa [-pi, pi] por defecto.

        Returns:
            (lim_inf, lim_sup, L)
        """
        import re

        PI = 3.14159265358979
        texto_analisis = texto_func.replace('pi', str(PI))

        patron_num = r'x\s*[<>]=?\s*(-?[0-9]+\.?[0-9]*)'
        valores = [float(m) for m in re.findall(patron_num, texto_analisis)]

        if len(valores) >= 2:
            lim_inf = min(valores)
            lim_sup = max(valores)
        elif len(valores) == 1:
            v = abs(valores[0])
            lim_inf, lim_sup = -v, v
        else:
            lim_inf, lim_sup = -PI, PI

        T = lim_sup - lim_inf
        if T < 1e-9:
            lim_inf, lim_sup, T = -PI, PI, 2 * PI

        return lim_inf, lim_sup, T / 2.0
    
    def actualizar_funcion_texto(self, sintaxis: str):
        pass  # Sin uso activo; la actualización la maneja aplicar_funcion_widget
    
    def cargar_ejemplo(self, nombre: str):
        """Carga un ejemplo predefinido en la interfaz."""
        if nombre == "-- Seleccionar ejemplo --" or not nombre:
            self.label_desc_ejemplo.setText("")
            return
        if nombre == "Personalizada":
            self.label_desc_ejemplo.setText("")
            self.piecewise_widget.setEnabled(True)
            return
        
        ejemplo = obtener_ejemplo(nombre)
        self.label_desc_ejemplo.setText(ejemplo["descripcion"])
        self.piecewise_widget.setEnabled(False)
        self.texto_funcion.blockSignals(True)
        self.texto_funcion.setPlainText(ejemplo["funcion"])
        self.texto_funcion.blockSignals(False)
        self.validar_funcion_tiempo_real()
    
    def calcular_fourier(self):
        """Ejecuta el cálculo completo de la Serie de Fourier."""
        # Validar función
        texto_func = self.texto_funcion.toPlainText().strip()
        if not texto_func:
            QMessageBox.warning(self, "Error", "Ingrese una función f(x)")
            return
        
        es_valida, msg_error = validar_funcion(texto_func)
        if not es_valida:
            QMessageBox.critical(self, "Error de Sintaxis", f"Función inválida:\n{msg_error}")
            return
        
        lim_inf, lim_sup, L = self.extraer_periodo_de_funcion(texto_func)
        N = self.slider_n.value()

        # Periodo de extensión: puede diferir del dominio de definición de f(x).
        # lim_inf/lim_sup siempre son los límites reales de f; T_periodo controla omega.
        if self.radio_periodo_custom.isChecked():
            T_periodo = self.spin_periodo_custom.value()
            L = T_periodo / 2.0
        else:
            T_periodo = None  # usar lim_sup - lim_inf por defecto
        
        self.btn_calcular.setText("Calculando...")
        self.btn_calcular.setEnabled(False)
        QApplication.processEvents()
        
        try:
            f_expr    = parsear_funcion(texto_func)
            # N evaluaciones inclusivas: conjunto {0,1,...,N}
            # calcular_coeficientes(N) -> range(1,N+1) = indices [1..N] + DC en n=0
            a0, lista_an, lista_bn, indices = calcular_coeficientes(f_expr, lim_inf, lim_sup, N, T_periodo)
            serie_expr    = construir_serie_simbolica(a0, lista_an, lista_bn, indices, lim_inf, lim_sup, T_periodo)
            func_serie    = vectorizar_funcion(serie_expr)
            func_original = vectorizar_funcion(f_expr)

            self.resultado_actual = {
                "f_expr":       f_expr,
                "serie_expr":   serie_expr,
                "a0":           a0,
                "lista_an":     lista_an,
                "lista_bn":     lista_bn,
                "indices":      indices,
                "func_serie":   func_serie,
                "func_original": func_original,
                "L":            L,
                "lim_inf":      lim_inf,
                "lim_sup":      lim_sup,
                "N":            N,       # N = número de evaluaciones (n=0..N-1)

                "T_periodo":    T_periodo,
            }
            
            self.mostrar_coeficientes()
            self.graficar_resultado()

            self.slider_n_grafica.setRange(1, N)
            self.slider_n_grafica.setValue(N)
            self.slider_n_grafica.setEnabled(True)
            self.btn_ver_armonicos.setEnabled(True)

            self.btn_calcular.setText(f"Serie calculada (N={N})")
            QTimer.singleShot(2000, lambda: self.btn_calcular.setText("Calcular Serie de Fourier"))
            
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Error de Cálculo", f"No se pudo calcular:\n{str(e)}\n\n{tb}")
        
        finally:
            self.btn_calcular.setText("Calcular Serie de Fourier")
            self.btn_calcular.setEnabled(True)
    
    def mostrar_coeficientes(self):
        """Tabla unificada: n=0 como primera fila, luego n=1,2,...,N (inclusive)."""
        if not self.resultado_actual:
            return

        a0       = self.resultado_actual["a0"]
        lista_an = self.resultado_actual["lista_an"]
        lista_bn = self.resultado_actual["lista_bn"]
        indices  = self.resultado_actual["indices"]   # [1, 2, ..., N-1]
        N        = self.resultado_actual["N"]

        val_a0   = evaluar_coeficiente(a0) or 0
        n_ultimo = indices[-1] if indices else 0   # = N-1

        html  = "<pre style='color: #e6edf3; font-size: 10pt;'>"
        html += "<b style='color: #58a6ff;'>COEFICIENTES DE EULER-FOURIER</b>\n"
        html += "=" * 60 + "\n"
        html += f"<span style='color: #8b949e;'>Conjunto evaluado: n ∈ {{0, 1, ..., {n_ultimo}}}  →  {N + 1} evaluaciones</span>\n"
        html += f"<span style='color: #8b949e;'>Valores en gris = nulos para esta señal</span>\n\n"

        # Cabecera
        html += f"  {'n':>4}  {'an':>12}  {'bn':>12}  <span style='color:#8b949e; font-size:9pt;'>nota</span>\n"
        html += "  " + "-" * 56 + "\n"

        # Fila n=0: término DC (solo an = a0, bn no aplica)
        c0 = "#8b949e" if abs(val_a0) < 1e-10 else "#f78166"
        html += (f"  <b>{'0':>4}</b>  "
                 f"<span style='color:{c0};'>{val_a0:>12.6f}</span>  "
                 f"<span style='color:#8b949e;'>{'---':>12}</span>  "
                 f"<span style='color:#8b949e; font-size:9pt;'>"
                 f"a₀  →  término DC = a₀/2 = {val_a0/2:.6f}</span>\n")

        # Filas n=1..N-1
        for k, an, bn in zip(indices, lista_an, lista_bn):
            van = evaluar_coeficiente(an) or 0
            vbn = evaluar_coeficiente(bn) or 0
            c_an = "#8b949e" if abs(van) < 1e-10 else "#58a6ff"
            c_bn = "#8b949e" if abs(vbn) < 1e-10 else "#bc8cff"
            html += (f"  <b>{k:>4}</b>  "
                     f"<span style='color:{c_an};'>{van:>12.6f}</span>  "
                     f"<span style='color:{c_bn};'>{vbn:>12.6f}</span>\n")

        html += "\n" + "=" * 60 + "\n"
        html += f"<b>N = {N}  |  n ∈ {{0, 1, ..., {n_ultimo}}}  (conjunto cerrado, inclusive)</b>\n"
        html += "</pre>"

        self.texto_resultados.setHtml(html)
    
    def graficar_resultado(self):
        """
        Grafica f(x) y su aproximación de Fourier S_N(x).

        La función original se extiende periódicamente mapeando x al dominio
        base mediante módulo. La serie se evalúa directamente y se restringe
        a cero fuera del dominio si el modo es 'periodo infinito'.
        """
        if not self.resultado_actual:
            return
        
        L            = self.resultado_actual["L"]
        N            = self.slider_n_grafica.value()
        lim_inf      = self.resultado_actual.get("lim_inf", 0.0)
        lim_sup      = self.resultado_actual.get("lim_sup", L)
        func_original = self.resultado_actual["func_original"]
        
        if self.radio_periodo_dominio.isChecked():
            T_extension = lim_sup - lim_inf
        elif self.radio_periodo_infinito.isChecked():
            T_extension = lim_sup - lim_inf
        else:
            T_extension = self.spin_periodo_custom.value()
        
        a0       = self.resultado_actual["a0"]
        lista_an = self.resultado_actual["lista_an"][:N]
        lista_bn = self.resultado_actual["lista_bn"][:N]
        indices  = self.resultado_actual["indices"][:N]
        
        try:
            T_periodo_gr  = self.resultado_actual.get("T_periodo")
            serie_parcial = construir_serie_simbolica(
                a0, lista_an, lista_bn, indices, lim_inf, lim_sup, T_periodo_gr
            )
            func_serie    = vectorizar_funcion(serie_parcial)
        except Exception:
            func_serie = self.resultado_actual["func_serie"]
        
        num_periodos = 4
        
        if self.radio_periodo_infinito.isChecked():
            margen = (lim_sup - lim_inf) * 0.5
            x_inicio = lim_inf - margen
            x_fin    = lim_sup + margen
        else:
            x_inicio = lim_inf - num_periodos / 2 * T_extension
            x_fin    = lim_sup + num_periodos / 2 * T_extension
        
        x_vals = np.linspace(x_inicio, x_fin, 3000)
        
        N_base = 1000
        x_base = np.linspace(lim_inf, lim_sup, N_base, endpoint=False)
        try:
            y_base = func_original(x_base)
            y_base = np.array(y_base, dtype=float)
        except Exception:
            y_base = np.array([float(func_original(xi)) for xi in x_base])
        
        if self.radio_periodo_infinito.isChecked():
            y_original = np.zeros_like(x_vals)
            mask = (x_vals >= lim_inf) & (x_vals < lim_sup)
            x_en_dominio = x_vals[mask]
            y_original[mask] = np.interp(x_en_dominio, x_base, y_base)
        else:
            x_mapped = np.mod(x_vals - lim_inf, T_extension) + lim_inf
            y_original = np.interp(x_mapped, x_base, y_base)
        
        try:
            raw = func_serie(x_vals)
            y_serie = np.real(np.asarray(raw, dtype=complex)).astype(float)
        except Exception:
            y_serie = np.array([float(np.real(complex(func_serie(xi)))) for xi in x_vals])
        
        # En modo aperiódico, la serie se restringe al dominio de definición.
        if self.radio_periodo_infinito.isChecked():
            mask_fuera = (x_vals < lim_inf) | (x_vals >= lim_sup)
            y_serie[mask_fuera] = 0.0
        
        self.figura.clear()
        ax1 = self.figura.add_subplot(211)
        ax2 = self.figura.add_subplot(212)
        
        for ax in [ax1, ax2]:
            ax.set_facecolor('#161b22')
            ax.tick_params(colors='#e6edf3', labelsize=8)
            for spine in ax.spines.values():
                spine.set_color('#30363d')
            ax.grid(True, color='#21262d', linewidth=0.5, linestyle='--', alpha=0.7)
            ax.axhline(0, color='#30363d', linewidth=0.8)
            ax.axvline(0, color='#30363d', linewidth=0.8)
        
        ax1.plot(x_vals, y_original, color='#58a6ff', linewidth=1.8,
                label='f(x) — Señal original', zorder=3)
        ax1.plot(x_vals, y_serie, color='#f78166', linewidth=1.4,
                linestyle='--', label=f'S_N(x) — Aproximación (N={N})', zorder=4)
        
        if not self.radio_periodo_infinito.isChecked():
            for k in range(-num_periodos, num_periodos + 1):
                x_line = lim_inf + k * T_extension
                if x_inicio <= x_line <= x_fin:
                    ax1.axvline(x_line, color='#3b434b',
                               linewidth=0.8, linestyle=':', alpha=0.6)
        else:
            ax1.axvline(lim_inf, color='#f78166', linewidth=1.2, linestyle='--', alpha=0.7, label='Límite del dominio')
            ax1.axvline(lim_sup, color='#f78166', linewidth=1.2, linestyle='--', alpha=0.7)
        
        ax1.set_xlabel('x', color='#e6edf3', fontsize=9)
        ax1.set_ylabel('Amplitud', color='#e6edf3', fontsize=9)
        
        if self.radio_periodo_infinito.isChecked():
            titulo_periodo = "Periodo infinito"
        elif self.radio_periodo_dominio.isChecked():
            titulo_periodo = f"Periódica (T = {T_extension:.4f})"
        else:
            titulo_periodo = f"Periodo personalizado (T = {T_extension:.4f})"
        
        ax1.set_title(f'Serie de Fourier — N = {N} armónicos — {titulo_periodo}',
                     color='#58a6ff', fontsize=11, fontweight='bold', pad=10)
        ax1.legend(facecolor='#161b22', edgecolor='#30363d',
                  labelcolor='#e6edf3', fontsize=8)
        ax1.set_xlim(x_inicio, x_fin)
        
        # Espectro unilateral de amplitudes: A0 = |a0/2|, An = sqrt(an^2 + bn^2)
        # Los índices reales (ej. [1,3,5,7,9] para onda cuadrada) se usan como eje x.
        N_display = self.resultado_actual["N"]
        a0_val = abs(evaluar_coeficiente(a0) or 0)
        A0     = a0_val / 2.0

        amplitudes_espectrales = [
            np.sqrt((evaluar_coeficiente(lista_an[k]) or 0)**2 +
                    (evaluar_coeficiente(lista_bn[k]) or 0)**2)
            for k in range(len(lista_an))
        ]

        frecuencias = [0] + indices
        magnitudes  = [A0] + amplitudes_espectrales

        max_freq           = min(30, len(frecuencias))
        frecuencias_display = frecuencias[:max_freq]
        magnitudes_display  = magnitudes[:max_freq]

        markerline, stemlines, baseline = ax2.stem(
            frecuencias_display, 
            magnitudes_display,
            linefmt='#bc8cff', 
            markerfmt='o', 
            basefmt=' '
        )
        markerline.set_markerfacecolor('#bc8cff')
        markerline.set_markeredgecolor('#bc8cff')
        markerline.set_markersize(6)
        
        if len(frecuencias_display) > 2:
            freq_continuo = np.linspace(0, frecuencias_display[-1], 300)
            
            from scipy.interpolate import interp1d
            try:
                if len(frecuencias_display) >= 4:
                    interpolador = interp1d(frecuencias_display, magnitudes_display,
                                          kind='cubic', fill_value='extrapolate')
                else:
                    interpolador = interp1d(frecuencias_display, magnitudes_display,
                                          kind='linear', fill_value='extrapolate')
                
                magnitudes_continuo = np.maximum(interpolador(freq_continuo), 0)
                ax2.plot(freq_continuo, magnitudes_continuo, 
                        color='#58a6ff', linewidth=1.5, alpha=0.4, 
                        linestyle='-', label='Envolvente espectral')
                
            except Exception:
                ax2.plot(frecuencias_display, magnitudes_display,
                        color='#58a6ff', linewidth=1.2, alpha=0.3,
                        linestyle='-', marker='')
        
        ax2.set_xlabel('Frecuencia (armónico n)', color='#e6edf3', fontsize=9)
        ax2.set_ylabel('Amplitud espectral |Aₙ|', color='#e6edf3', fontsize=9)
        ax2.set_title('Espectro de Frecuencias (forma compleja de Fourier)', 
                     color='#bc8cff', fontsize=10, fontweight='bold', pad=10)
        ax2.set_xlim(-0.5, max_freq - 0.5)
        ax2.legend(facecolor='#161b22', edgecolor='#30363d',
                  labelcolor='#e6edf3', fontsize=7, loc='upper right')
        
        # Anotación con fórmula
        formula_text = r'$A_0 = |a_0/2|$,  $A_n = \sqrt{a_n^2 + b_n^2}$'
        ax2.text(0.98, 0.95, formula_text, 
                transform=ax2.transAxes, 
                fontsize=8, 
                color='#8b949e',
                ha='right', 
                va='top',
                bbox=dict(boxstyle='round', facecolor='#161b22', edgecolor='#30363d', alpha=0.8))
        
        self.figura.tight_layout()
        self.canvas.draw()
    
    def recalcular_grafica_rapido(self):
        """Regenera la gráfica con el N actual del slider (sin recalcular coeficientes)."""
        if self.resultado_actual:
            self.graficar_resultado()


def main():
    """Punto de entrada de la aplicación."""
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    ventana = VentanaPrincipal()
    ventana.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()