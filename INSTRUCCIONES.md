# Instrucciones de Ejecución

Aplicación Django — Transformada de Laplace · UTEZ 8vo Cuatrimestre

---

## Requisitos previos

- **Python 3.10 o superior** instalado y en el PATH
- **pip** disponible (viene incluido con Python)
- Conexión a internet (solo para la primera instalación de dependencias)

Verificar instalación:

```bash
python --version
pip --version
```

---

## Instalación

### 1. Navegar al directorio del proyecto

```bash
cd C:\ERICK\UTEZ\8VO\IntegradoraMate
```

### 2. (Opcional pero recomendado) Crear un entorno virtual

```bash
python -m venv venv
venv\Scripts\activate
```

> Si usas Git Bash o WSL reemplaza `venv\Scripts\activate` por `source venv/Scripts/activate`

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instala:

| Paquete | Para qué se usa |
|---------|----------------|
| `Django` | Framework web |
| `sympy` | Cómputo simbólico de Laplace |
| `numpy` | Evaluación numérica de y(t) para graficar |
| `matplotlib` | Generación de gráficas |

---

## Ejecución

```bash
python manage.py runserver
```

Salida esperada:

```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
March 25, 2026 - 16:27:40
Django version 5.x, using settings 'laplace_project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Abrir en el navegador:** http://127.0.0.1:8000

Para detener el servidor: `Ctrl + C`

---

## Uso de la aplicación

### 1. Seleccionar el orden de la EDO

Usa los botones **"Segundo Orden"** / **"Primer Orden"** en la parte superior del formulario.
- Primer orden: aparece `a₁y' + a₀y = f(t)`
- Segundo orden: aparece `a₂y'' + a₁y' + a₀y = f(t)`

### 2. Ingresar coeficientes

Escribe el valor numérico de cada coeficiente en los campos del constructor visual.
Acepta enteros, negativos y decimales (ej. `1`, `-2`, `0.5`).

### 3. Elegir f(t)

Selecciona el tipo de función del lado derecho:

| Opción | Función | Campo "param" |
|--------|---------|---------------|
| 0 (homogénea) | `f(t) = 0` | No aplica |
| Constante C | `f(t) = C` | Valor de C |
| eᵃᵗ | `f(t) = e^(at)` | Valor de a |
| sin(bt) | `f(t) = sin(bt)` | Valor de b |
| cos(bt) | `f(t) = cos(bt)` | Valor de b |
| t·eᵃᵗ | `f(t) = t·e^(at)` | Valor de a |
| t·sin(bt) | `f(t) = t·sin(bt)` | Valor de b |

### 4. Ingresar condiciones iniciales

- `y(0)` — valor de la función en t=0
- `y'(0)` — valor de la derivada en t=0 (solo para 2do orden)

### 5. Resolver

Clic en **"Resolver con Transformada de Laplace →"**

### 6. Ver resultados

- **Solución final** `y(t)` resaltada en verde al inicio
- **6 pasos expandibles** con la derivación completa:
  - Ecuación original
  - Propiedades de Laplace aplicadas
  - Transformada de f(t)
  - Ecuación algebraica resultante
  - Despeje de Y(s)
  - Fracciones parciales (si aplica)
  - Transformada Inversa → y(t)
- **Gráfica** de y(t) en el intervalo [0, 10]

> Pasa el cursor sobre los íconos `[?]` para ver la teoría de cada concepto.

---

## Cargar casos de prueba del 

En la sección **"Casos de Prueba del "** hay 4 botones que cargan automáticamente los datos:

| Botón | Ecuación |
|-------|----------|
| Caso 1 | `y' + 2y = 0`, `y(0)=1` |
| Caso 2 | `y'' + 3y' + 2y = 0`, `y(0)=0`, `y'(0)=1` |
| Caso 3 | `y' − y = eᵗ`, `y(0)=1` |
| Caso 4 | `y'' + y = sin(t)`, `y(0)=0`, `y'(0)=0` |

---

## Solución de problemas comunes

**`ModuleNotFoundError: No module named 'sympy'`**
```bash
pip install sympy numpy matplotlib
```

**`python` no reconocido en la terminal**
Asegúrate de que Python esté en el PATH del sistema, o usa `py` en lugar de `python`.

**El servidor inicia pero la página no carga**
Verifica que la URL sea exactamente `http://127.0.0.1:8000/` (con la barra final o sin ella).

**La gráfica no aparece**
Asegúrate de que matplotlib esté instalado: `pip install matplotlib`. La gráfica se genera internamente y no requiere ninguna ventana del sistema.

**Error `[Errno 98] Address already in use`**
El puerto 8000 está ocupado. Usa otro puerto:
```bash
python manage.py runserver 8080
# Luego abrir: http://127.0.0.1:8080
```

**Los símbolos matemáticos no se renderizan**
La app usa KaTeX cargado desde CDN. Necesitas conexión a internet activa la primera vez; después queda en caché del navegador.

---

## Estructura de archivos

```
IntegradoraMate/
├── manage.py              ← Comando principal de Django
├── requirements.txt       ← Lista de dependencias
├── PROYECTO.md            ← Documentación del proyecto
├── INSTRUCCIONES.md       ← Este archivo
├── PI-ED.pdf              ← Enunciado original de la tarea
│
├── laplace_project/
│   ├── settings.py        ← Configuración Django
│   ├── urls.py            ← Rutas de la aplicación
│   └── wsgi.py
│
└── solver/
    ├── math_engine.py     ← Motor matemático (SymPy)
    ├── views.py           ← Lógica de la vista
    ├── urls.py
    └── templates/solver/
        └── index.html     ← Interfaz completa
```
