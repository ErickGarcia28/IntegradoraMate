# Tarea Integradora — Resolución de EDOs con Transformada de Laplace

**Universidad Tecnológica Emiliano Zapata del Estado de Morelos (UTEZ)**
Academia de Ciencias · 8vo Cuatrimestre

---

## Descripción general

Aplicación web construida con **Django** que resuelve Ecuaciones Diferenciales Ordinarias (EDOs) de primer y segundo orden mediante el **método de la Transformada de Laplace**.

La app no solo entrega la solución final: muestra cada paso algebraico del proceso, la teoría detrás de cada operación (mediante tooltips interactivos), y genera automáticamente una gráfica de la solución `y(t)`.

---

## Problema que resuelve

Dada una EDO de la forma:

```
a₂ y''(t) + a₁ y'(t) + a₀ y(t) = f(t)
con  y(0) = c₁,  y'(0) = c₂
```

El sistema:

1. Aplica la Transformada de Laplace a cada término
2. Incorpora las condiciones iniciales automáticamente
3. Despeja `Y(s)` algebraicamente
4. Aplica fracciones parciales
5. Aplica la Transformada Inversa para obtener `y(t)`
6. Grafica la solución

---

## Fundamento matemático

### ¿Qué es la Transformada de Laplace?

La Transformada de Laplace convierte una función del dominio del tiempo `f(t)` al dominio de la frecuencia compleja `F(s)`:

```
L{f(t)} = ∫₀^∞ f(t) · e^(-st) dt
```

Su utilidad principal: **convierte derivadas en multiplicaciones por s**, transformando una EDO en una ecuación algebraica.

### Propiedades clave usadas

| Función | Transformada |
|---------|-------------|
| `y(t)` | `Y(s)` |
| `y'(t)` | `s·Y(s) − y(0)` |
| `y''(t)` | `s²·Y(s) − s·y(0) − y'(0)` |
| `1` | `1/s` |
| `eᵃᵗ` | `1/(s−a)` |
| `sin(bt)` | `b/(s²+b²)` |
| `cos(bt)` | `s/(s²+b²)` |
| `tⁿ` | `n!/s^(n+1)` |

Las condiciones iniciales `y(0)` y `y'(0)` se incorporan directamente al aplicar las propiedades de derivada. Esto elimina el paso de "resolver constantes de integración" que requieren otros métodos.

### Proceso algebraico completo

Para `a₂y'' + a₁y' + a₀y = f(t)`:

**Paso 1 — Aplicar L{·} a toda la ecuación:**

```
a₂[s²Y(s) − sy(0) − y'(0)] + a₁[sY(s) − y(0)] + a₀Y(s) = F(s)
```

**Paso 2 — Agrupar términos con Y(s):**

```
(a₂s² + a₁s + a₀) · Y(s) = F(s) + a₂[sy(0) + y'(0)] + a₁y(0)
```

**Paso 3 — Despejar Y(s):**

```
Y(s) = [F(s) + términos de condiciones iniciales] / (a₂s² + a₁s + a₀)
```

**Paso 4 — Fracciones parciales:**
Descomponemos Y(s) en fracciones simples cuya transformada inversa es inmediata desde tablas.

**Paso 5 — Transformada Inversa:**
Aplicamos `L⁻¹{·}` a cada fracción para obtener `y(t)`.

---

## Casos de prueba (del enunciado)

| # | Ecuación | Condiciones | Resultado | Tipo |
|---|----------|-------------|-----------|------|
| 1 | `y' + 2y = 0` | `y(0)=1` | `y(t) = e^{-2t}` | Decaimiento exponencial |
| 2 | `y'' + 3y' + 2y = 0` | `y(0)=0, y'(0)=1` | `y(t) = (eᵗ−1)e^{-2t}` | Sobreamortiguado |
| 3 | `y' − y = eᵗ` | `y(0)=1` | `y(t) = (t+1)eᵗ` | Forzamiento exponencial |
| 4 | `y'' + y = sin(t)` | `y(0)=0, y'(0)=0` | `y(t) = ½sin(t) − ½t·cos(t)` | **Resonancia** |

> El caso 4 es especialmente interesante: la frecuencia de forzamiento (ω=1) coincide con la frecuencia natural del sistema (ω_n=1), produciendo el fenómeno de resonancia donde la amplitud crece sin límite con el tiempo.

---

## Arquitectura del proyecto

```
IntegradoraMate/
├── manage.py                         # Punto de entrada Django
├── requirements.txt                  # Dependencias Python
│
├── laplace_project/                  # Configuración del proyecto Django
│   ├── settings.py                   # Ajustes: apps, templates, idioma
│   ├── urls.py                       # Enrutamiento raíz
│   └── wsgi.py                       # Interfaz WSGI para producción
│
└── solver/                           # Aplicación principal
    ├── math_engine.py                # Motor matemático (sympy)
    ├── views.py                      # Lógica de vistas Django
    ├── urls.py                       # URLs de la app
    ├── apps.py                       # Configuración de la app
    └── templates/solver/
        └── index.html                # Interfaz completa (HTML/CSS/JS)
```

### Módulo `math_engine.py`

Contiene toda la lógica matemática, desacoplada de Django:

| Función | Responsabilidad |
|---------|----------------|
| `to_sym(value)` | Convierte strings/floats a expresiones sympy limpias |
| `build_rhs(type, param)` | Construye `f(t)` según el tipo seleccionado |
| `laplace_of_rhs(expr)` | Calcula `F(s) = L{f(t)}` con sympy |
| `clean_result(expr)` | Simplifica: elimina `Heaviside(t)`, extrae parte real |
| `generate_plot(expr)` | Genera la gráfica matplotlib como base64 |
| `build_step_strings(...)` | Genera los pasos de derivación en LaTeX |
| `solve_ode(...)` | **Función principal** — orquesta todo el proceso |

### Módulo `views.py`

Vista única `index`:
- `GET`: renderiza el formulario vacío con los 4 ejemplos del PDF
- `POST`: extrae parámetros, llama a `solve_ode()`, pasa resultado al template

### Template `index.html`

Diseño de "instrumento científico" con tema oscuro:

- **Pipeline visual** — muestra las 4 etapas del método de Laplace
- **Constructor de ecuación** — campos `a₂`, `a₁`, `a₀` con vista en línea
- **Selector de f(t)** — menú con 7 tipos de función
- **Pasos expandibles** — accordeón con 6 pasos + explicación teórica en cada uno
- **Tooltips** — al pasar el cursor sobre `[?]` aparece la teoría del concepto
- **Gráfica** — imagen matplotlib embebida como base64 (sin archivos temporales)
- **Tabla de transformadas** — referencia lateral siempre visible
- **KaTeX** — renderizado matemático profesional en el navegador

---

## Tecnologías utilizadas

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.x | Lenguaje base |
| Django | ≥4.2 | Framework web |
| SymPy | ≥1.12 | Cómputo simbólico (Laplace, álgebra, fracciones parciales) |
| NumPy | ≥1.24 | Evaluación numérica para gráficas |
| Matplotlib | ≥3.7 | Generación de gráficas |
| KaTeX | 0.16.9 | Renderizado LaTeX en el navegador |
| HTML/CSS/JS | — | Interfaz (sin frameworks frontend externos) |

---

## Funciones de f(t) soportadas

| Tipo | Función | Ejemplo de L{f(t)} |
|------|---------|-------------------|
| `zero` | `0` (homogénea) | `0` |
| `constant` | `C` | `C/s` |
| `exp` | `e^(at)` | `1/(s−a)` |
| `sin` | `sin(bt)` | `b/(s²+b²)` |
| `cos` | `cos(bt)` | `s/(s²+b²)` |
| `texp` | `t·e^(at)` | `1/(s−a)²` |
| `tsin` | `t·sin(bt)` | `2bs/(s²+b²)²` |

---

## Reflexión técnica

### Dificultades encontradas al implementar matemáticas en código

1. **Simplificación simbólica no determinista** — SymPy no siempre simplifica al mismo resultado equivalente; se requirió postprocesamiento con `clean_result()` para eliminar `Heaviside(t)` y extraer la parte real cuando aparecían residuos imaginarios numéricos.

2. **Fracciones parciales incompletas** — `sympy.apart()` a veces no descompone completamente expresiones con raíces complejas, lo que obliga a aplicar `inverse_laplace_transform` directamente sobre Y(s) simplificado.

3. **Fallback a dsolve** — Para casos donde `inverse_laplace_transform` falla (expresiones muy complejas), se implementó un fallback usando `sympy.dsolve()` con condiciones iniciales.

4. **Generación de gráficas sin sistema de archivos** — Matplotlib se configuró con backend `Agg` para operar sin pantalla, y las imágenes se convierten a base64 para embeberse directamente en HTML.

### ¿Cómo mejoraría el programa?

- Soporte para funciones de forzamiento más complejas: escalón unitario `u(t−a)`, impulso `δ(t)`, funciones periódicas
- Interpretador de texto libre: parsear "y'' + 3y' + 2y = sin(t)" directamente desde un campo de texto
- Comparación visual con método numérico (Runge-Kutta 4) superpuesto en la gráfica
- Exportación del reporte completo a PDF con todos los pasos y gráfica
- Animación de la "construcción" de y(t) en tiempo real
