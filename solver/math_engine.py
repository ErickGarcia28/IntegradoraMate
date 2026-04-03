"""
Motor matemático para resolución de EDOs con Transformada de Laplace.
Usa sympy para cómputo simbólico paso a paso.
"""

import sympy as sp
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from io import BytesIO
import base64


# ── Símbolos globales ──────────────────────────────────────────────────────────
t = sp.Symbol('t', positive=True)
s = sp.Symbol('s')


def to_sym(value, default=0):
    """Convierte un string/número al tipo sympy más limpio."""
    try:
        v = float(str(value).strip())
        if v == int(v):
            return sp.Integer(int(v))
        return sp.nsimplify(v, rational=True, tolerance=1e-4)
    except (ValueError, TypeError):
        return sp.Integer(default)


def build_rhs(rhs_type: str, rhs_param: str) -> sp.Expr:
    """Construye la función f(t) del lado derecho de la EDO."""
    p = to_sym(rhs_param, default=1)
    rhs_map = {
        'zero':     sp.Integer(0),
        'constant': p,
        'exp':      sp.exp(p * t),
        'sin':      sp.sin(p * t),
        'cos':      sp.cos(p * t),
        'texp':     t * sp.exp(p * t),
        'tsin':     t * sp.sin(p * t),
    }
    return rhs_map.get(rhs_type, sp.Integer(0))


def laplace_of_rhs(f_expr: sp.Expr) -> sp.Expr:
    """Calcula la Transformada de Laplace de f(t)."""
    try:
        F = sp.laplace_transform(f_expr, t, s, noconds=True)
        return sp.simplify(F)
    except Exception:
        return sp.laplace_transform(f_expr, t, s, noconds=True)


def clean_result(expr: sp.Expr) -> sp.Expr:
    """Limpia la expresión: elimina Heaviside(t)=1 para t>0, extrae parte real."""
    expr = expr.subs(sp.Heaviside(t), 1)
    # Si sympy retornó partes imaginarias mínimas por error numérico, tomar parte real
    if expr.has(sp.I):
        expr = sp.re(expr)
    return sp.simplify(expr)


def generate_plot(y_expr: sp.Expr, t_max: float = 10.0) -> str:
    """
    Genera la gráfica de y(t) y retorna como string base64.
    Usa tema oscuro para coincidir con la UI.
    """
    t_num = np.linspace(0, t_max, 600)

    try:
        f_num = sp.lambdify(t, y_expr, modules=['numpy'])
        y_num = np.array(f_num(t_num), dtype=float)

        # Recortar valores extremos para mejor visualización
        y_abs_max = np.nanmax(np.abs(y_num))
        if y_abs_max > 1e6:
            clip = 1e6
        else:
            clip = y_abs_max * 2 + 1
        y_num = np.clip(y_num, -clip, clip)
    except Exception:
        return ''

    if not np.any(np.isfinite(y_num)):
        return ''

    # ── Estilo del gráfico ────────────────────────────────────────────────────
    BG_BASE   = '#0a0e17'
    BG_CARD   = '#111827'
    AMBER     = '#f59e0b'
    GREEN     = '#10b981'
    GRID_LINE = '#1e2d3d'
    TEXT_DIM  = '#64748b'
    TEXT_MED  = '#94a3b8'

    fig, ax = plt.subplots(figsize=(9, 4))
    fig.patch.set_facecolor(BG_BASE)
    ax.set_facecolor(BG_CARD)

    # Línea principal
    ax.plot(t_num, y_num, color=AMBER, linewidth=2.2, zorder=3)

    # Línea cero
    ax.axhline(y=0, color=GRID_LINE, linewidth=1.0, zorder=2)
    ax.axvline(x=0, color=GRID_LINE, linewidth=1.0, zorder=2)

    # Grid suave
    ax.set_facecolor(BG_CARD)
    ax.grid(True, color=GRID_LINE, linewidth=0.6, linestyle='--', alpha=0.6, zorder=1)

    # Ejes y etiquetas
    ax.set_xlabel('t', color=TEXT_MED, fontsize=12, labelpad=8)
    ax.set_ylabel('y(t)', color=TEXT_MED, fontsize=12, labelpad=8)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)

    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_LINE)

    # Área bajo la curva (sutil)
    ax.fill_between(t_num, y_num, 0,
                    alpha=0.08, color=GREEN, zorder=1)

    fig.tight_layout(pad=1.5)

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                facecolor=BG_BASE, edgecolor='none')
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_b64


# ── Pasos de derivación simbólica ─────────────────────────────────────────────

def _fmt_coeff(c: sp.Expr) -> str:
    """Formatea un coeficiente para mostrar en LaTeX (omite '1·')."""
    if c == 1:
        return ''
    if c == -1:
        return '-'
    return sp.latex(c)


def build_step_strings(order, a2, a1, a0, y0, dy0, f_t, F_s, Y_s, Y_s_pf, y_t):
    """
    Genera los pasos de derivación como diccionarios con texto LaTeX.
    Cada paso incluye: título, contenido LaTeX, explicación teórica.
    """
    steps = []

    # ── PASO 0: Ecuación original ──────────────────────────────────────────────
    if order == 2:
        ode_latex = (
            f"{_fmt_coeff(a2)}y'' + {_fmt_coeff(a1)}y' + {sp.latex(a0)}y = {sp.latex(f_t)}"
            .replace("+ -", "- ")
        )
    else:
        ode_latex = (
            f"{_fmt_coeff(a1)}y' + {sp.latex(a0)}y = {sp.latex(f_t)}"
            .replace("+ -", "- ")
        )
    steps.append({
        'num': 0,
        'title': 'Ecuación Diferencial Original',
        'latex': ode_latex,
        'theory': (
            'Una Ecuación Diferencial Ordinaria (EDO) relaciona una función desconocida '
            'y(t) con sus derivadas. La idea de Laplace es transformar esta ecuación '
            'a un dominio algebraico donde sea más fácil resolver.'
        ),
        'color': 'amber',
    })

    # ── PASO 1: Propiedades de Laplace usadas ─────────────────────────────────
    props_lines = [
        r"\mathcal{L}\{y(t)\} = Y(s)",
        r"\mathcal{L}\{y'(t)\} = s\,Y(s) - y(0)",
    ]
    if order == 2:
        props_lines.append(r"\mathcal{L}\{y''(t)\} = s^2\,Y(s) - s\,y(0) - y'(0)")

    steps.append({
        'num': 1,
        'title': 'Propiedades de Transformada a Aplicar',
        'latex': r' \qquad '.join(props_lines),
        'theory': (
            'La clave del método: la Transformada de Laplace convierte derivadas en '
            'multiplicaciones por s. Cada derivada incorpora automáticamente las '
            'condiciones iniciales, eliminando el paso de "encontrar constantes" '
            'que requieren otros métodos.'
        ),
        'multiline': props_lines,
        'color': 'indigo',
    })

    # ── PASO 2: Transformada de f(t) ──────────────────────────────────────────
    steps.append({
        'num': 2,
        'title': 'Transformada del Lado Derecho',
        'latex': rf"\mathcal{{L}}\{{{sp.latex(f_t)}\}} = {sp.latex(F_s)}",
        'theory': (
            'Transformamos f(t) usando tablas de Laplace estándar. '
            'Por ejemplo: ℒ{eᵃᵗ} = 1/(s-a),  ℒ{sin(bt)} = b/(s²+b²),  '
            'ℒ{C} = C/s.  Esto nos da F(s), el término del lado derecho '
            'en el dominio s.'
        ),
        'color': 'indigo',
    })

    # ── PASO 3: Ecuación algebraica después de aplicar Laplace ───────────────
    y0_sym = to_sym(str(y0))
    dy0_sym = to_sym(str(dy0))

    if order == 2:
        # a2*(s²Y - s·y0 - dy0) + a1*(sY - y0) + a0·Y = F(s)
        ic_terms = a2 * (s * y0_sym + dy0_sym) + a1 * y0_sym
        char_poly = a2 * s**2 + a1 * s + a0
        alg_rhs = F_s + ic_terms
        alg_latex = (
            rf"\left({sp.latex(char_poly)}\right) Y(s) = "
            rf"{sp.latex(sp.simplify(alg_rhs))}"
        )
        expand_latex = (
            rf"{sp.latex(a2)}\bigl(s^2 Y(s) - {sp.latex(s*y0_sym)} - {sp.latex(dy0_sym)}\bigr)"
            rf" + {sp.latex(a1)}\bigl(s\,Y(s) - {sp.latex(y0_sym)}\bigr)"
            rf" + {sp.latex(a0)}\,Y(s) = {sp.latex(F_s)}"
        ).replace("+ -", "- ")
    else:
        ic_terms = a1 * y0_sym
        char_poly = a1 * s + a0
        alg_rhs = F_s + ic_terms
        alg_latex = (
            rf"\left({sp.latex(char_poly)}\right) Y(s) = "
            rf"{sp.latex(sp.simplify(alg_rhs))}"
        )
        expand_latex = (
            rf"{sp.latex(a1)}\bigl(s\,Y(s) - {sp.latex(y0_sym)}\bigr)"
            rf" + {sp.latex(a0)}\,Y(s) = {sp.latex(F_s)}"
        ).replace("+ -", "- ")

    steps.append({
        'num': 3,
        'title': 'Aplicar Transformada a Toda la Ecuación',
        'latex': expand_latex,
        'latex2': alg_latex,
        'theory': (
            'Aplicamos ℒ{·} a cada término de la EDO y sustituimos las condiciones '
            'iniciales. Los términos de Y(s) se agrupan en el polinomio '
            'característico P(s). Los términos de condiciones iniciales pasan al '
            'lado derecho. La EDO se convirtió en una ecuación algebraica lineal en Y(s).'
        ),
        'color': 'blue',
    })

    # ── PASO 4: Despejar Y(s) ─────────────────────────────────────────────────
    steps.append({
        'num': 4,
        'title': 'Despejar Y(s)',
        'latex': rf"Y(s) = {sp.latex(Y_s)}",
        'theory': (
            'Despejamos algebraicamente Y(s). Esta expresión racional en s '
            'es la Transformada de Laplace de la solución. '
            'Los polos de Y(s) (raíces del denominador) determinan el '
            'comportamiento cualitativo de y(t): raíces reales negativas → '
            'decaimiento exponencial; complejas conjugadas → oscilación amortiguada.'
        ),
        'color': 'blue',
    })

    # ── PASO 5: Fracciones parciales ──────────────────────────────────────────
    if sp.simplify(Y_s - Y_s_pf) != 0:
        steps.append({
            'num': 5,
            'title': 'Descomposición en Fracciones Parciales',
            'latex': rf"Y(s) = {sp.latex(Y_s_pf)}",
            'theory': (
                'Descomponemos Y(s) en fracciones simples cuya transformada inversa '
                'es inmediata desde tablas. Por ejemplo: '
                r'A/(s+a) → A·e^{-at},  B·ω/((s+α)²+ω²) → B·e^{-αt}sin(ωt). '
                'Este paso es equivalente a la resolución de integrales por fracciones '
                'parciales en Cálculo Integral.'
            ),
            'color': 'violet',
        })

    # ── PASO 6: Transformada Inversa → y(t) ──────────────────────────────────
    steps.append({
        'num': 6,
        'title': 'Transformada Inversa de Laplace',
        'latex': rf"\mathcal{{L}}^{{-1}}\left\{{ {sp.latex(Y_s_pf)} \right\}} = {sp.latex(y_t)}",
        'theory': (
            'Aplicamos ℒ⁻¹{·} usando tablas inversas de Laplace a cada fracción. '
            'El Teorema de Unicidad garantiza que si F(s) = ℒ{f(t)}, entonces '
            'ℒ⁻¹{F(s)} = f(t) (para funciones continuas por tramos de orden '
            'exponencial). La solución obtenida satisface tanto la EDO como '
            'las condiciones iniciales dadas.'
        ),
        'color': 'green',
    })

    return steps


# ── Función principal ──────────────────────────────────────────────────────────

def solve_ode(order: int,
              a2_str: str, a1_str: str, a0_str: str,
              rhs_type: str, rhs_param: str,
              y0_str: str, dy0_str: str) -> dict:
    """
    Resuelve la EDO usando Transformada de Laplace.
    Retorna un diccionario con todos los pasos, LaTeX y la gráfica.
    """
    # Convertir coeficientes
    a0 = to_sym(a0_str)
    a1 = to_sym(a1_str)
    a2 = to_sym(a2_str) if order == 2 else sp.Integer(0)
    y0 = to_sym(y0_str, default=0)
    dy0 = to_sym(dy0_str, default=0) if order == 2 else sp.Integer(0)

    # Validación básica
    leading = a2 if order == 2 else a1
    if leading == 0:
        raise ValueError(
            f"El coeficiente principal {'a₂' if order==2 else 'a₁'} no puede ser cero."
        )

    # Construir f(t) y F(s)
    f_t = build_rhs(rhs_type, rhs_param)
    F_s = laplace_of_rhs(f_t)

    # Símbolo Y(s)
    Y = sp.Symbol('Y')

    # Ecuación algebraica en Y
    if order == 2:
        lhs = a2 * (s**2 * Y - s * y0 - dy0) + a1 * (s * Y - y0) + a0 * Y
    else:
        lhs = a1 * (s * Y - y0) + a0 * Y

    eq = sp.Eq(lhs, F_s)
    solutions = sp.solve(eq, Y)
    if not solutions:
        raise ValueError("No se pudo resolver la ecuación algebraica para Y(s).")

    Y_s = sp.simplify(solutions[0])

    # Fracciones parciales
    try:
        Y_s_pf = sp.apart(Y_s, s)
    except Exception:
        Y_s_pf = Y_s

    # Transformada inversa
    try:
        y_t_raw = sp.inverse_laplace_transform(Y_s_pf, s, t)
        y_t = clean_result(y_t_raw)
    except Exception:
        # Fallback: usar dsolve de sympy directamente
        y_func = sp.Function('y')
        if order == 2:
            ode_eq = sp.Eq(
                a2 * y_func(t).diff(t, 2) + a1 * y_func(t).diff(t) + a0 * y_func(t),
                f_t
            )
            ics = {y_func(0): y0, y_func(t).diff(t).subs(t, 0): dy0}
        else:
            ode_eq = sp.Eq(
                a1 * y_func(t).diff(t) + a0 * y_func(t),
                f_t
            )
            ics = {y_func(0): y0}

        sol = sp.dsolve(ode_eq, y_func(t), ics=ics)
        y_t = clean_result(sol.rhs)

    # Generar pasos
    steps = build_step_strings(order, a2, a1, a0, y0, dy0, f_t, F_s, Y_s, Y_s_pf, y_t)

    # Gráfica
    plot_b64 = generate_plot(y_t)

    # Ecuación legible del input para mostrar al usuario
    def coeff_str(c, var):
        c = sp.simplify(c)
        if c == 0:
            return ''
        if c == 1:
            return f'+{var}'
        if c == -1:
            return f'-{var}'
        return f'+{sp.latex(c)}{var}'

    if order == 2:
        eq_display = (
            f"{sp.latex(a2)}y'' "
            + coeff_str(a1, "y' ")
            + coeff_str(a0, 'y')
            + f" = {sp.latex(f_t)}"
        ).replace('+-', '-').lstrip('+')
        ic_display = f"y(0)={sp.latex(y0)},\\quad y'(0)={sp.latex(dy0)}"
    else:
        eq_display = (
            f"{sp.latex(a1)}y' "
            + coeff_str(a0, 'y')
            + f" = {sp.latex(f_t)}"
        ).replace('+-', '-').lstrip('+')
        ic_display = f"y(0)={sp.latex(y0)}"

    return {
        'success': True,
        'order': order,
        'equation_latex': eq_display,
        'ic_latex': ic_display,
        'f_t_latex': sp.latex(f_t),
        'F_s_latex': sp.latex(F_s),
        'Y_s_latex': sp.latex(Y_s),
        'Y_s_pf_latex': sp.latex(Y_s_pf),
        'y_t_latex': sp.latex(y_t),
        'steps': steps,
        'plot_b64': plot_b64,
    }
