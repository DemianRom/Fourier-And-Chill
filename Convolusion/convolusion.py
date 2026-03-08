# =============================================================================
# PROGRAMA PARA VISUALIZAR LA CONVOLUCIÓN DE DOS FUNCIONES
# Procesamiento Digital de Señales
# =============================================================================

# Importamos las librerías necesarias
import numpy as np                  # Para operaciones matemáticas y arrays
import matplotlib.pyplot as plt     # Para graficar
from matplotlib.widgets import Slider       # Para el deslizador interactivo
from matplotlib.animation import FuncAnimation  # Para la animación

# =============================================================================
# 1. ENTRADA DE FUNCIONES POR EL USUARIO (con manejo seguro de eval)
# =============================================================================

print("Ingresa las funciones usando t como variable.")
print("Puedes usar: exp(t), sin(t), cos(t), sqrt(t), abs(t), heaviside(t,1), etc.")
print("Ejemplos: exp(-t), sin(2*pi*t), t**2, heaviside(t,1)")

# Solicitamos las expresiones al usuario
f_str = input("f(t) = ")
g_str = input("g(t) = ")

# Construimos un entorno de evaluación seguro:
# Tomamos todas las funciones y constantes de numpy (sin las internas)
allowed_names = {k: v for k, v in np.__dict__.items() if not k.startswith('__')}
# Añadimos la función abs (built-in) y heaviside (que en numpy requiere dos argumentos)
allowed_names.update({'abs': abs, 'heaviside': lambda x, y: np.heaviside(x, y)})

def safe_eval(expr, t_val):
    """
    Evalúa la expresión expr con la variable t = t_val,
    usando únicamente las funciones permitidas (numpy + abs + heaviside).
    Se deshabilitan todas las funciones built-in peligrosas.
    """
    # El segundo argumento de eval son los globales, aquí vacío excepto __builtins__ vacío
    # El tercer argumento son los locales: incluimos las funciones permitidas y la variable t
    return eval(expr, {"__builtins__": {}}, {**allowed_names, 't': t_val})

# Creamos funciones lambda que usan safe_eval para un valor escalar de t
f = lambda t_val: safe_eval(f_str, t_val)
g = lambda t_val: safe_eval(g_str, t_val)

# =============================================================================
# 2. DEFINIR EL EJE TEMPORAL Y EVALUAR LAS FUNCIONES
# =============================================================================

# Rango de tiempo y número de puntos (resolución)
t_min, t_max = -5, 5
num_points = 1000
t = np.linspace(t_min, t_max, num_points)  # Vector de tiempo

# Evaluamos las funciones en cada punto de t (usando listas por comprensión)
f_vals = np.array([f(ti) for ti in t])     # Valores de f(t)
g_vals = np.array([g(ti) for ti in t])     # Valores de g(t)

# =============================================================================
# 3. CALCULAR LA CONVOLUCIÓN USANDO numpy.convolve
# =============================================================================

# Espaciado entre puntos (necesario para escalar la convolución discreta)
dt = t[1] - t[0]

# convolve calcula la suma de productos. mode='same' devuelve un array del mismo tamaño que t
# Multiplicamos por dt para aproximar la integral continua
conv = np.convolve(f_vals, g_vals, mode='same') * dt

# =============================================================================
# 4. SELECCIÓN DEL TIPO DE VISUALIZACIÓN
# =============================================================================

print("\nElige el tipo de visualización:")
print("1. Animación automática (película)")
print("2. Deslizador interactivo")
opcion = input("Opción (1 o 2): ")

# =============================================================================
# 5. ANIMACIÓN (OPCIÓN 1)
# =============================================================================

if opcion == '1':
    # Crear figura con dos subplots verticales
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    plt.subplots_adjust(hspace=0.4)  # Espacio entre subplots

    # Configurar el subplot superior (ax1)
    ax1.set_xlim(t_min, t_max)
    # Establecer límites en y basados en los valores de f y g, con un margen
    ax1.set_ylim(min(f_vals.min(), g_vals.min()) - 1,
                 max(f_vals.max(), g_vals.max()) + 1)
    ax1.axhline(0, color='gray', linewidth=0.5)  # Línea horizontal en y=0
    ax1.set_ylabel('Amplitud')
    ax1.set_title('Producto f(τ) · g(t-τ)')

    # Configurar el subplot inferior (ax2) para la convolución
    ax2.set_xlim(t_min, t_max)
    ax2.set_ylim(conv.min() - 0.5, conv.max() + 0.5)
    ax2.axhline(0, color='gray', linewidth=0.5)
    ax2.set_xlabel('t')
    ax2.set_ylabel('Convolución (f * g)(t)')
    ax2.set_title('Resultado acumulado')

    # Crear objetos gráficos que se actualizarán en la animación
    # Línea para f(τ) (fija, azul)
    line_f, = ax1.plot([], [], 'b-', label='f(τ)')
    # Línea para g(t-τ) (se desplaza, roja)
    line_g_shifted, = ax1.plot([], [], 'r-', label='g(t-τ)')
    # Relleno del área bajo el producto (se actualizará)
    product_fill = ax1.fill_between([], [], [], alpha=0.3, color='purple', label='producto')
    # Línea de la convolución (verde, se construye progresivamente)
    line_conv, = ax2.plot([], [], 'g-', linewidth=2)
    # Punto que indica el valor actual de la convolución
    point_conv, = ax2.plot([], [], 'ro')

    ax1.legend(loc='upper right')  # Leyenda en ax1

    # Función de inicialización (se llama al principio de la animación)
    def init():
        line_f.set_data([], [])
        line_g_shifted.set_data([], [])
        line_conv.set_data([], [])
        point_conv.set_data([], [])
        return line_f, line_g_shifted, line_conv, point_conv

    # Función de animación: se ejecuta para cada fotograma (cada valor de t)
    def animate(frame):
        t_current = t[frame]  # Valor actual de t

        # Calcular g desplazada: g(t_current - τ) para cada τ en t
        # Usamos una lista por comprensión para evaluar g en cada punto
        g_shifted_vals = np.array([g(t_current - tau) for tau in t])

        # Producto punto a punto f(τ) * g(t_current - τ)
        product = f_vals * g_shifted_vals

        # Actualizar líneas en ax1
        line_f.set_data(t, f_vals)                     # f siempre igual
        line_g_shifted.set_data(t, g_shifted_vals)     # g desplazada

        # Actualizar relleno del producto
        global product_fill
        product_fill.remove()                           # Eliminar el relleno anterior
        product_fill = ax1.fill_between(t, 0, product, alpha=0.3, color='purple')

        # En ax2, mostrar la convolución acumulada hasta el instante actual
        line_conv.set_data(t[:frame+1], conv[:frame+1])
        point_conv.set_data([t_current], [conv[frame]])

        # Actualizar título con el valor actual de t
        ax1.set_title(f'Producto f(τ) · g({t_current:.2f} - τ)')

        # Devolver los objetos modificados (necesario para blit, aunque blit=False)
        return line_f, line_g_shifted, product_fill, line_conv, point_conv

    # Crear la animación
    ani = FuncAnimation(fig, animate, frames=len(t), init_func=init,
                        blit=False, interval=20)

    # Mostrar la ventana con la animación
    plt.show()

# =============================================================================
# 6. DESLIZADOR INTERACTIVO (OPCIÓN 2)
# =============================================================================

else:
    # Crear figura con dos subplots (similar a la animación)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    # Dejamos espacio abajo para el slider
    plt.subplots_adjust(bottom=0.2, hspace=0.4)

    # ---- Subplot superior ----
    # Graficamos f(τ) fija (línea azul)
    ax1.plot(t, f_vals, 'b-', label='f(τ)')
    # Línea para g desplazada (inicialmente en t=0)
    g_shifted_vals0 = np.array([g(0 - tau) for tau in t])
    g_shifted_line, = ax1.plot(t, g_shifted_vals0, 'r-', label='g(t-τ)')
    # Relleno del producto (inicialmente para t=0)
    product0 = f_vals * g_shifted_vals0
    product_fill = ax1.fill_between(t, 0, product0, alpha=0.3, color='purple', label='producto')
    ax1.axhline(0, color='gray', linewidth=0.5)
    ax1.set_xlim(t_min, t_max)
    ax1.set_ylim(min(f_vals.min(), g_vals.min()) - 1,
                 max(f_vals.max(), g_vals.max()) + 1)
    ax1.set_ylabel('Amplitud')
    ax1.set_title('Producto f(τ) · g(t-τ)')
    ax1.legend(loc='upper right')

    # ---- Subplot inferior ----
    # Graficamos la convolución completa (verde)
    ax2.plot(t, conv, 'g-', linewidth=2, label='(f*g)(t)')
    # Punto rojo que indica el valor para el t actual (inicial en t=0)
    idx0 = np.argmin(np.abs(t - 0))  # índice más cercano a 0
    point, = ax2.plot([0], [conv[idx0]], 'ro', markersize=8)
    ax2.axhline(0, color='gray', linewidth=0.5)
    ax2.set_xlim(t_min, t_max)
    ax2.set_ylim(conv.min() - 0.5, conv.max() + 0.5)
    ax2.set_xlabel('t')
    ax2.set_ylabel('Convolución')
    ax2.set_title('Resultado de la convolución')
    ax2.legend()

    # ---- Crear el deslizador ----
    # Posición del slider: [left, bottom, width, height] en coordenadas relativas a la figura
    ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
    slider = Slider(ax_slider, 'Desplazamiento t', t_min, t_max,
                    valinit=0.0, valfmt='%1.2f')

    # Función que se ejecuta al mover el slider
    def update(val):
        t_current = slider.val  # Valor actual del slider

        # Calcular g desplazada para este t
        g_shifted = np.array([g(t_current - tau) for tau in t])
        # Producto
        product = f_vals * g_shifted

        # Actualizar la línea roja
        g_shifted_line.set_ydata(g_shifted)

        # Actualizar relleno (eliminar anterior y crear nuevo)
        global product_fill
        product_fill.remove()
        product_fill = ax1.fill_between(t, 0, product, alpha=0.3, color='purple')

        # Encontrar el índice más cercano a t_current en el array t
        idx = np.argmin(np.abs(t - t_current))
        # Actualizar la posición del punto rojo en ax2
        point.set_data([t_current], [conv[idx]])

        # Actualizar título
        ax1.set_title(f'Producto f(τ) · g({t_current:.2f} - τ)')
        # Redibujar la figura
        fig.canvas.draw_idle()

    # Conectar el slider con la función de actualización
    slider.on_changed(update)

    # Mostrar la ventana interactiva
    plt.show()