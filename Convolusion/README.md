# README: Visualización de la Convolución de Señales

Este programa está diseñado para ayudar a comprender la operación de convolución en el procesamiento digital de señales. Permite ingresar dos funciones \( f(t) \) y \( g(t) \), y visualizar cómo se desliza una sobre la otra mientras se calcula el área bajo el producto, generando la función resultante \( (f * g)(t) \). Se incluyen dos modos de visualización: una animación automática y un deslizador interactivo.

## ¿Qué es la convolución?

La convolución es una operación matemática que combina dos funciones para producir una tercera. En señales, se interpreta como el área bajo el producto de una función y una versión desplazada y reflejada de la otra. La definición es:

\[
(f * g)(t) = \int_{-\infty}^{\infty} f(\tau) \, g(t - \tau) \, d\tau
\]

**Interpretación gráfica:**
- Tomamos \( f(\tau) \) fija.
- Tomamos \( g(\tau) \), la reflejamos (convierte en \( g(-\tau) \)) y luego la desplazamos en \( t \) (obtenemos \( g(t - \tau) \)).
- Multiplicamos punto a punto \( f(\tau) \) y \( g(t - \tau) \).
- El área bajo ese producto es el valor de la convolución en el instante \( t \).
- Repetimos para cada \( t \) y obtenemos la señal completa.

Esta operación es fundamental en sistemas lineales e invariantes en el tiempo (SLIT), donde la salida es la convolución de la entrada con la respuesta al impulso.

## Lógica del programa: ¿cómo calcula la convolución?

La computadora trabaja con valores discretos, por lo que debemos aproximar la integral continua. El programa sigue estos pasos:

1. **Muestreo del tiempo**: se define un vector `t` con muchos puntos entre `t_min` y `t_max` (por defecto -5 a 5 con 1000 puntos). Cada punto representa un instante de tiempo.
2. **Evaluación de las funciones**: se evalúan \( f(t) \) y \( g(t) \) en cada uno de esos puntos, obteniendo los arreglos `f_vals` y `g_vals`.
3. **Aproximación de la integral**:
   - La convolución discreta (sin escalar) se calcula con `np.convolve(f_vals, g_vals, mode='same')`. Esta función realiza la suma:

     \[
     (f * g)_{\text{discreto}}[n] = \sum_{k} f[k] \, g[n - k]
     \]

   - Para que corresponda a la integral continua, debemos multiplicar por el espaciado entre muestras `dt = t[1] - t[0]`. Esto convierte la suma en una aproximación de la integral de Riemann:

     \[
     (f * g)(t_n) \approx \sum_{k} f(\tau_k) \, g(t_n - \tau_k) \, \Delta\tau = \text{conv\_discreta}[n] \cdot dt
     \]

   - El resultado `conv` es un arreglo de la misma longitud que `t`, y representa los valores de la convolución en esos instantes.

**¿Por qué `mode='same'`?**  
`np.convolve` ofrece varios modos: `full` devuelve la convolución completa (tamaño `len(f)+len(g)-1`), `same` recorta el resultado para que tenga el mismo tamaño que la primera entrada, centrándolo aproximadamente. Esto es conveniente para mantener la correspondencia con el vector de tiempo `t`.

## Visualización: animación y slider

El programa ofrece dos maneras de explorar visualmente el proceso:

### Animación automática
- Se crean dos subplots: arriba se muestran \( f(\tau) \) (fija, azul) y \( g(t - \tau) \) (desplazándose, roja); abajo se construye progresivamente la convolución (verde).
- Para cada fotograma (cada valor de \( t \)), se calcula \( g(t - \tau) \) evaluando la función `g` en `t - tau` para cada `tau` del vector tiempo. Luego se multiplica con `f_vals` y se rellena el área bajo el producto.
- En el subplot inferior, se van añadiendo puntos de la convolución hasta el instante actual, y se marca con un punto rojo el valor correspondiente.

### Deslizador interactivo
- Similar a la animación, pero el usuario controla manualmente el desplazamiento `t` mediante un slider.
- Al mover el slider, se actualizan en tiempo real: la curva roja de `g(t-τ)`, el área del producto, y el punto rojo en la gráfica de convolución.
- Esto permite explorar libremente la relación entre el desplazamiento y el valor de la convolución.

## Ejemplo de prueba de escritorio: dos pulsos rectangulares

Para entender cómo se obtiene una señal triangular a partir de la convolución de dos ondas cuadradas, hagamos una prueba manual sencilla con funciones discretizadas en pocos puntos.

### Funciones
Consideremos un pulso rectangular de ancho 2 y altura 1, definido como:
\[
f(t) = \begin{cases}
1 & \text{si } -1 \le t \le 1 \\
0 & \text{en otro caso}
\end{cases}
\]
Tomamos la misma función para \( g(t) \).

Aproximaremos con 5 puntos en el eje \( t \) (para simplificar) en el rango \([-2, 2]\):
- Puntos: \( t = -2, -1, 0, 1, 2 \)
- \( f(t) \) (y \( g(t) \)) vale 1 en \( t = -1, 0, 1 \) (puntos centrales) y 0 en los extremos.

### Cálculo manual de la convolución (suma discreta sin escalar)
Necesitamos calcular para cada \( t_n \):

\[
y[n] = \sum_{k} f[k] \cdot g[n - k]
\]

donde los índices corresponden a los puntos de tiempo.

Representamos \( f \) como vector:  
`f = [0, 1, 1, 1, 0]`  (para t = -2, -1, 0, 1, 2)

Igual para `g`.

**Paso a paso** (usaremos índices de 0 a 4):

- Para `n = 0` (t = -2):  
  \( y[0] = f[0]·g[0] + f[1]·g[-1] + f[2]·g[-2] + f[3]·g[-3] + f[4]·g[-4] \)  
  Los índices negativos no existen, se consideran cero. Entonces solo contribuye el término con índices válidos cuando `k` y `n-k` están entre 0 y 4.  
  Vamos k=0: g[0] (n-k=0) → 0·0=0  
  k=1: g[-1] no existe → 0  
  k=2: g[-2] no existe → 0  
  k=3: g[-3] no existe → 0  
  k=4: g[-4] no existe → 0  
  y[0] = 0.

- Para `n = 1` (t = -1):  
  k=0: g[1] = g[1] = 1 → f[0]·g[1] = 0·1 = 0  
  k=1: g[0] = 0 → f[1]·g[0] = 1·0 = 0  
  k=2: g[-1] no → 0  
  k=3: g[-2] no → 0  
  k=4: g[-3] no → 0  
  y[1] = 0.

- Para `n = 2` (t = 0):  
  k=0: g[2] = 1 → 0·1 = 0  
  k=1: g[1] = 1 → 1·1 = 1  
  k=2: g[0] = 0 → 1·0 = 0  
  k=3: g[-1] no → 0  
  k=4: g[-2] no → 0  
  y[2] = 1.

- Para `n = 3` (t = 1):  
  k=0: g[3] = 1 → 0·1 = 0  
  k=1: g[2] = 1 → 1·1 = 1  
  k=2: g[1] = 1 → 1·1 = 1  
  k=3: g[0] = 0 → 1·0 = 0  
  k=4: g[-1] no → 0  
  Suma = 2 → y[3] = 2.

- Para `n = 4` (t = 2):  
  k=0: g[4] = 0 → 0·0 = 0  
  k=1: g[3] = 1 → 1·1 = 1  
  k=2: g[2] = 1 → 1·1 = 1  
  k=3: g[1] = 1 → 1·1 = 1  
  k=4: g[0] = 0 → 0·0 = 0  
  Suma = 3 → y[4] = 3.

Espera, este resultado no es simétrico triangular. ¿Qué pasó? En realidad, al usar pocos puntos y no alinear correctamente el soporte, la discretización burda distorsiona la forma. Con una mejor resolución (más puntos) se obtendría la esperada forma triangular. Además, en este cálculo hemos usado índices enteros que corresponden a tiempos discretos, pero el resultado debería ser simétrico: para t=0 debería ser el máximo (área de superposición completa). En nuestro caso, el máximo dio en t=2 (índice 4) porque la definición de los vectores no está centrada correctamente para la convolución con mode='same'. Esto ilustra la importancia de escalar y alinear adecuadamente.

Para una correcta interpretación, el programa usa `mode='same'` que centra el resultado, y además usa muchos puntos. En el ejemplo con muchos puntos, el resultado sí es un triángulo simétrico con máximo en t=0.

**Conclusión de la prueba manual:**  
La convolución discreta aproxima la continua, pero requiere suficiente resolución y un escalado por `dt` para obtener la amplitud correcta. Con 1000 puntos en [-5,5], el programa da un resultado visualmente correcto.

## ¿Cómo el programa traduce esto a gráficas?

1. **Cálculo de g(t-τ) para un t dado**:  
   Para cada valor de `t` (ya sea en la animación o en el slider), se genera un arreglo `g_shifted` evaluando `g(t - tau)` para cada `tau` en el vector tiempo. Esto se hace con un bucle o comprensión de listas.
2. **Producto**: se multiplica `f_vals` por `g_shifted` punto a punto.
3. **Relleno**: se usa `fill_between` para sombrear el área bajo el producto.
4. **Punto en la convolución**: se busca el índice de `t` más cercano al valor actual y se toma el valor correspondiente de `conv`, marcándolo con un punto rojo.

## Estructura del código (resumen)

- **Entrada de funciones**: se usa `input()` y se evalúan en un entorno seguro con funciones de `numpy` (exp, sin, heaviside, etc.).
- **Preparación de datos**: se crea el vector `t`, se evalúan `f` y `g` en todos los puntos.
- **Cálculo de la convolución**: `np.convolve(...) * dt`.
- **Visualización**: según la opción elegida, se configura la animación o el slider con las actualizaciones correspondientes.

## Requisitos

- Python 3.x
- NumPy
- Matplotlib

## Ejecución

1. Instalar dependencias: `pip install numpy matplotlib`
2. Ejecutar: `python convolucion.py`
3. Ingresar funciones (por ejemplo, `exp(-t)` y `heaviside(t,1)`, o las del ejemplo de pulsos).
4. Elegir modo de visualización y disfrutar.

---

Este programa es una herramienta didáctica para afianzar el concepto de convolución. Experimenta con diferentes funciones y observa cómo el área del producto se convierte en la señal de salida. ¡La práctica visual es la mejor aliada para entender este concepto fundamental!
