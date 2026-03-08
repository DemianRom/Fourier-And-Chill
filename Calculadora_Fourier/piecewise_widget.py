"""
piecewise_widget.py - Widget visual para funciones a trozos.

TramoWidget  : un tramo individual (expresión + límites).
PiecewiseWidget : contenedor de tramos que genera sintaxis Piecewise.

Equipo 7 - 5CM1 - ESCOM
    1. Romero Bautista Demian
    2. Linares Ojeda Carlos Elias
    3. Aparicio Arenas Victor Eduardo
    4. Gutiérrez Romero Omar José Eduardo
    5. Cardenaz Hernández Ximena
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class TramoWidget(QFrame):
    """
    Fila editable para un tramo: expresión y límites del intervalo.

    Señales:
        eliminado(TramoWidget): emitida al presionar el botón de eliminar.
    """

    eliminado = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            TramoWidget {
                background-color: #1e1e1e;
                border: 1px solid #3a3a3a;
                border-radius: 5px;
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(4, 3, 4, 3)

        self.expr_edit = QLineEdit()
        self.expr_edit.setPlaceholderText("Expresion (ej: x**2, sin(x), 1)")
        self.expr_edit.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d; color: #ffffff;
                border: 1px solid #404040; border-radius: 3px;
                padding: 4px; font-family: 'Courier New', monospace; font-size: 9pt;
            }
        """)
        layout.addWidget(self.expr_edit, 3)

        layout.addWidget(self._label(",", "color: #808080; font-size: 14pt; font-weight: bold;"))

        self.lim_inf_edit = QLineEdit()
        self.lim_inf_edit.setPlaceholderText("inf")
        self.lim_inf_edit.setFixedWidth(52)
        self.lim_inf_edit.setStyleSheet(self._estilo_limite())
        layout.addWidget(self.lim_inf_edit)

        layout.addWidget(self._label("≤", "color: #808080; font-size: 11pt;"))
        layout.addWidget(self._label("x",   "color: #f0f0f0; font-size: 12pt; font-style: italic;"))
        layout.addWidget(self._label("≤", "color: #808080; font-size: 11pt;"))

        self.lim_sup_edit = QLineEdit()
        self.lim_sup_edit.setPlaceholderText("sup")
        self.lim_sup_edit.setFixedWidth(52)
        self.lim_sup_edit.setStyleSheet(self._estilo_limite())
        layout.addWidget(self.lim_sup_edit)

        btn = QPushButton("−")
        btn.setFixedSize(24, 24)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #c62828; color: white; border: none;
                border-radius: 12px; font-size: 13pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #d32f2f; }
        """)
        btn.clicked.connect(lambda: self.eliminado.emit(self))
        layout.addWidget(btn)

        self.setLayout(layout)

    def _label(self, texto, estilo):
        lbl = QLabel(texto)
        lbl.setStyleSheet(estilo)
        return lbl

    def _estilo_limite(self):
        return """
            QLineEdit {
                background-color: #2d2d2d; color: #58a6ff;
                border: 1px solid #404040; border-radius: 3px;
                padding: 3px; font-family: 'Courier New', monospace; font-size: 9pt;
            }
        """

    def obtener_datos(self) -> dict:
        """Retorna {'expr', 'lim_inf', 'lim_sup'} del tramo."""
        return {
            "expr":    self.expr_edit.text().strip(),
            "lim_inf": self.lim_inf_edit.text().strip(),
            "lim_sup": self.lim_sup_edit.text().strip(),
        }

    def establecer_datos(self, expr: str, lim_inf: str, lim_sup: str):
        """Rellena los campos del tramo."""
        self.expr_edit.setText(expr)
        self.lim_inf_edit.setText(lim_inf)
        self.lim_sup_edit.setText(lim_sup)


class PiecewiseWidget(QWidget):
    """
    Interfaz visual para construir funciones a trozos.

    Gestiona una lista de TramoWidget y genera la sintaxis Piecewise
    correspondiente. Rastrea el campo con foco para inserción de símbolos
    desde el teclado matemático externo.
    """

    funcion_cambiada = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tramos        = []
        self.campo_activo  = None
        self.periodo_infinito = True
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a2e; color: #a8d8a8;
                border: 1px solid #2d5a2d; border-radius: 4px;
                padding: 6px; font-family: 'Courier New', monospace; font-size: 9pt;
            }
        """)
        self.preview_label.setWordWrap(False)
        self.preview_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.preview_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(100)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        scroll_widget = QWidget()
        self.tramos_layout = QVBoxLayout()
        self.tramos_layout.setSpacing(8)
        scroll_widget.setLayout(self.tramos_layout)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll, 1)

        btn_anadir = QPushButton("+ Añadir trozo")
        btn_anadir.setStyleSheet("""
            QPushButton {
                background-color: #1976d2; color: white; border: none;
                border-radius: 5px; padding: 10px; font-size: 10pt; font-weight: bold;
            }
            QPushButton:hover { background-color: #2196f3; }
        """)
        btn_anadir.clicked.connect(self.anadir_tramo)
        layout.addWidget(btn_anadir)

        self.setLayout(layout)

        self.anadir_tramo()
        self.anadir_tramo()
        self.actualizar_preview()

    def anadir_tramo(self):
        """Agrega un tramo vacío al widget."""
        tramo = TramoWidget()
        tramo.eliminado.connect(self.eliminar_tramo)

        tramo.expr_edit.textChanged.connect(self.actualizar_preview)
        tramo.lim_inf_edit.textChanged.connect(self.actualizar_preview)
        tramo.lim_sup_edit.textChanged.connect(self.actualizar_preview)

        for campo in (tramo.expr_edit, tramo.lim_inf_edit, tramo.lim_sup_edit):
            campo.focusInEvent = self._hacer_focus_handler(campo, campo.focusInEvent)

        self.tramos.append(tramo)
        self.tramos_layout.addWidget(tramo)
        self.actualizar_preview()

    def _hacer_focus_handler(self, campo, handler_original):
        def handler(event):
            self.campo_activo = campo
            handler_original(event)
        return handler

    def insertar_en_campo_activo(self, simbolo: str) -> bool:
        """Inserta un símbolo en el campo con foco. Retorna True si lo insertó."""
        if self.campo_activo is not None:
            pos   = self.campo_activo.cursorPosition()
            texto = self.campo_activo.text()
            self.campo_activo.setText(texto[:pos] + simbolo + texto[pos:])
            self.campo_activo.setCursorPosition(pos + len(simbolo))
            return True
        return False

    def eliminar_tramo(self, tramo: TramoWidget):
        """Elimina un tramo; mantiene al menos uno."""
        if len(self.tramos) > 1:
            self.tramos.remove(tramo)
            self.tramos_layout.removeWidget(tramo)
            tramo.deleteLater()
            self.actualizar_preview()

    def actualizar_modo_periodo(self, es_infinito: bool):
        """Actualiza el modo de extensión y redibuja la preview."""
        self.periodo_infinito = es_infinito
        self.actualizar_preview()

    def actualizar_preview(self):
        """Refresca la vista previa en texto plano."""
        lineas = []
        for tramo in self.tramos:
            d = tramo.obtener_datos()
            expr    = d["expr"]    or "□"
            lim_inf = d["lim_inf"] or "□"
            lim_sup = d["lim_sup"] or "□"
            lineas.append(f"  {expr}  ,  {lim_inf} <= x <= {lim_sup}")

        if self.periodo_infinito:
            lineas.append("  0  ,  fuera del dominio")
        else:
            lineas.append("  ...  (extension periodica)")

        self.preview_label.setText("f(x) = {\n" + "\n".join(lineas))

    def generar_piecewise(self, periodo_infinito: bool = True) -> str:
        """
        Genera la sintaxis Piecewise a partir de los tramos.

        Usa intervalos cerrados [lim_inf, lim_sup].
        Si periodo_infinito es True, agrega (0, True) al final.
        """
        # Recopilar tramos válidos primero
        tramos_validos = []
        for tramo in self.tramos:
            d = tramo.obtener_datos()
            expr, lim_inf, lim_sup = d["expr"], d["lim_inf"], d["lim_sup"]
            if not expr or not lim_inf or not lim_sup:
                continue
            tramos_validos.append((expr.replace("^", "**"), lim_inf, lim_sup))

        # Convención: tramos interiores son [a, b), el último es [a, b]
        # Esto evita que los puntos de frontera caigan en dos tramos a la vez.
        piezas = []
        for i, (expr, lim_inf, lim_sup) in enumerate(tramos_validos):
            es_ultimo = (i == len(tramos_validos) - 1)
            op = "<=" if es_ultimo else "<"
            piezas.append(f"({expr}, (x >= {lim_inf}) & (x {op} {lim_sup}))")

        if not piezas:
            return ""
        if periodo_infinito:
            piezas.append("(0, True)")

        return "Piecewise(" + ", ".join(piezas) + ")"

    def obtener_funcion(self) -> str:
        """Retorna la sintaxis Piecewise generada."""
        return self.generar_piecewise()

    def limpiar_tramos(self):
        """Elimina todos los tramos y deja dos vacíos."""
        for tramo in self.tramos[:]:
            self.tramos_layout.removeWidget(tramo)
            tramo.deleteLater()
        self.tramos.clear()
        self.anadir_tramo()
        self.anadir_tramo()
        self.actualizar_preview()

    def establecer_funcion(self, texto: str):
        """Intenta rellenar el primer tramo con una función no-Piecewise."""
        if not texto.startswith("Piecewise") and self.tramos:
            self.tramos[0].establecer_datos(texto, "-pi", "pi")
        self.actualizar_preview()