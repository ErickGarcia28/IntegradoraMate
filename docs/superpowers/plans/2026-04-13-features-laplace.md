# Features Laplace — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar 4 features al solver Django: interpretador de texto, exportación a PDF (ReportLab), comparación RK4 en la gráfica, y animaciones de pasos en acordeón.

**Architecture:** Todas las features se integran en los archivos existentes (math_engine.py, views.py, urls.py, index.html) sin crear nuevas apps Django. RK4 se calcula dentro de `generate_plot()` como segunda línea en la misma gráfica matplotlib. El PDF se genera server-side con ReportLab en una vista dedicada. El parser de texto es JS puro en el frontend.

**Tech Stack:** Django, SymPy, NumPy, Matplotlib, ReportLab, HTML/CSS/JS vanilla

---

### Task 1: RK4 en generate_plot()

**Files:**
- Modify: `solver/math_engine.py` — función `generate_plot()` y `solve_ode()`

- [ ] **Step 1: Modificar firma de `generate_plot()`** para aceptar parámetros de la EDO y trazar RK4:

```python
def generate_plot(y_expr: sp.Expr, t_max: float = 10.0,
                  order: int = 1,
                  a0=None, a1=None, a2=None,
                  f_t: sp.Expr = None,
                  y0=0.0, dy0=0.0) -> str:
```

- [ ] **Step 2: Implementar RK4 1er orden** dentro de `generate_plot()`, antes de la sección de estilo:

```python
    CYAN = '#22d3ee'
    rk4_y = None
    if f_t is not None and a1 is not None and a0 is not None:
        try:
            f_num_rhs = sp.lambdify(t, f_t, modules=['numpy'])
            a0f, a1f = float(a0), float(a1)
            h = t_num[1] - t_num[0]
            if order == 1 and a1f != 0:
                rk = np.zeros(len(t_num))
                rk[0] = float(y0)
                def ode1(ti, yi):
                    return (float(f_num_rhs(ti)) - a0f * yi) / a1f
                for i in range(len(t_num) - 1):
                    k1 = ode1(t_num[i], rk[i])
                    k2 = ode1(t_num[i] + h/2, rk[i] + h*k1/2)
                    k3 = ode1(t_num[i] + h/2, rk[i] + h*k2/2)
                    k4 = ode1(t_num[i] + h,   rk[i] + h*k3)
                    rk[i+1] = rk[i] + h*(k1 + 2*k2 + 2*k3 + k4)/6
                rk4_y = rk
            elif order == 2 and a2 is not None:
                a2f = float(a2)
                if a2f != 0:
                    yrk  = np.zeros(len(t_num))
                    dyrk = np.zeros(len(t_num))
                    yrk[0]  = float(y0)
                    dyrk[0] = float(dy0)
                    a1f2 = float(a1) if a1 is not None else 0.0
                    def ode2(ti, yi, dyi):
                        return (float(f_num_rhs(ti)) - a1f2*dyi - a0f*yi) / a2f
                    for i in range(len(t_num) - 1):
                        k1y = dyrk[i];              k1d = ode2(t_num[i], yrk[i], dyrk[i])
                        k2y = dyrk[i]+h*k1d/2;     k2d = ode2(t_num[i]+h/2, yrk[i]+h*k1y/2, dyrk[i]+h*k1d/2)
                        k3y = dyrk[i]+h*k2d/2;     k3d = ode2(t_num[i]+h/2, yrk[i]+h*k2y/2, dyrk[i]+h*k2d/2)
                        k4y = dyrk[i]+h*k3d;        k4d = ode2(t_num[i]+h, yrk[i]+h*k3y, dyrk[i]+h*k3d)
                        yrk[i+1]  = yrk[i]  + h*(k1y+2*k2y+2*k3y+k4y)/6
                        dyrk[i+1] = dyrk[i] + h*(k1d+2*k2d+2*k3d+k4d)/6
                    rk4_y = yrk
        except Exception:
            rk4_y = None
```

- [ ] **Step 3: Dibujar la línea RK4** en el gráfico (después de `ax.plot(t_num, y_num, ...)`):

```python
    if rk4_y is not None:
        rk4_clipped = np.clip(rk4_y, -clip, clip)
        ax.plot(t_num, rk4_clipped, color=CYAN, linewidth=1.6,
                linestyle='--', alpha=0.75, zorder=4, label='RK4 numérico')
        ax.plot(t_num, y_num, color=AMBER, linewidth=2.2, zorder=3, label='Laplace exacto')
        ax.legend(loc='upper right', fontsize=9,
                  facecolor='#111827', edgecolor='#1e2d3d',
                  labelcolor=[AMBER, CYAN])
```

- [ ] **Step 4: Actualizar la llamada a `generate_plot()` en `solve_ode()`** — reemplazar la línea `plot_b64 = generate_plot(y_t)`:

```python
    plot_b64 = generate_plot(
        y_t, t_max=10.0,
        order=order, a0=a0, a1=a1, a2=a2,
        f_t=f_t, y0=float(y0), dy0=float(dy0)
    )
```

- [ ] **Step 5: Commit**

```bash
git add solver/math_engine.py
git commit -m "feat: agrega comparación RK4 en la gráfica de y(t)"
```

---

### Task 2: Exportación a PDF con ReportLab

**Files:**
- Modify: `requirements.txt`
- Modify: `solver/math_engine.py` — agregar helper `latex_to_text()` y campo `y_t_pretty` al resultado
- Modify: `solver/views.py` — agregar vista `export_pdf`
- Modify: `solver/urls.py` — agregar ruta `/pdf/`
- Modify: `solver/templates/solver/index.html` — agregar botón "Exportar PDF"

- [ ] **Step 1: Agregar reportlab a requirements.txt**

```
Django>=4.2
sympy>=1.12
matplotlib>=3.7
numpy>=1.24
reportlab>=4.0
```

- [ ] **Step 2: Instalar reportlab**

```bash
pip install reportlab
```

- [ ] **Step 3: Agregar helper `latex_to_text()` en math_engine.py** (después de los imports):

```python
import re

def latex_to_text(latex_str: str) -> str:
    """Convierte LaTeX simple a texto legible para PDF."""
    s = latex_str
    s = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', s)
    s = re.sub(r'\\mathcal\{[^}]+\}', 'L', s)
    s = re.sub(r'\^\{([^}]+)\}', r'^(\1)', s)
    s = re.sub(r'_\{([^}]+)\}', r'_\1', s)
    s = re.sub(r'\\left[\(\[\{]|\\right[\)\]\}]', '', s)
    s = re.sub(r'\\(quad|qquad)', '  ', s)
    s = re.sub(r'\\cdot', '·', s)
    s = re.sub(r'\\,', ' ', s)
    s = re.sub(r'\\[a-zA-Z]+', '', s)
    s = s.replace('{', '').replace('}', '')
    return s.strip()
```

- [ ] **Step 4: Agregar `y_t_pretty` y `steps_text` al return de `solve_ode()`** (dentro del bloque `return {...}`):

```python
        'y_t_pretty':      str(y_t),
        'steps_text': [
            {
                'num':   step['num'],
                'title': step['title'],
                'math':  latex_to_text(step.get('latex', '')),
                'theory': step['theory'],
            }
            for step in steps
        ],
```

- [ ] **Step 5: Agregar vista `export_pdf` en views.py**

```python
from django.http import HttpResponse
from io import BytesIO

def export_pdf(request):
    if request.method != 'POST':
        from django.shortcuts import redirect
        return redirect('index')

    form = dict(request.POST)
    flat = {k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in form.items()}

    try:
        order = int(flat.get('order', 2))
        result = solve_ode(
            order=order,
            a2_str=flat.get('a2', '0'),
            a1_str=flat.get('a1', '1'),
            a0_str=flat.get('a0', '0'),
            rhs_type=flat.get('rhs_type', 'zero'),
            rhs_param=flat.get('rhs_param', '1'),
            y0_str=flat.get('y0', '0'),
            dy0_str=flat.get('dy0', '0'),
        )
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=400)

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable, Table, TableStyle
    )
    import base64

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=inch, bottomMargin=0.75*inch,
        title='Solución EDO — Transformada de Laplace'
    )

    styles = getSampleStyleSheet()
    C_DARK   = colors.HexColor('#0f1623')
    C_AMBER  = colors.HexColor('#f59e0b')
    C_GREEN  = colors.HexColor('#10b981')
    C_INDIGO = colors.HexColor('#818cf8')
    C_TEXT   = colors.HexColor('#1e293b')
    C_MUTED  = colors.HexColor('#475569')

    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=18, textColor=C_DARK, spaceAfter=4,
        fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=10, textColor=C_MUTED, spaceAfter=12)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'],
        fontSize=13, textColor=C_AMBER, spaceBefore=14, spaceAfter=6,
        fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=11, textColor=C_TEXT, spaceAfter=4, leading=16)
    math_style = ParagraphStyle('Math', parent=styles['Normal'],
        fontSize=12, textColor=C_DARK, spaceAfter=6,
        fontName='Courier-Bold', backColor=colors.HexColor('#f8fafc'),
        borderPadding=(6, 10, 6, 10))
    step_title_style = ParagraphStyle('StepTitle', parent=styles['Normal'],
        fontSize=11, textColor=C_INDIGO, spaceAfter=3, fontName='Helvetica-Bold')
    theory_style = ParagraphStyle('Theory', parent=styles['Normal'],
        fontSize=9, textColor=C_MUTED, spaceAfter=8, leading=14,
        leftIndent=12)

    story = []

    # ── Encabezado ────────────────────────────────────────────────
    story.append(Paragraph('Transformada de Laplace — Solución de EDO', title_style))
    story.append(Paragraph('Universidad Tecnológica Emiliano Zapata · UTEZ · 8vo Cuatrimestre', sub_style))
    story.append(HRFlowable(width='100%', thickness=2, color=C_AMBER, spaceAfter=10))

    # ── Ecuación ingresada ────────────────────────────────────────
    story.append(Paragraph('Ecuación diferencial', section_style))
    from .math_engine import latex_to_text
    eq_text = latex_to_text(result['equation_latex'])
    ic_text = latex_to_text(result['ic_latex'])
    story.append(Paragraph(eq_text, math_style))
    story.append(Paragraph(f'Condiciones iniciales: {ic_text}', body_style))
    story.append(Spacer(1, 8))

    # ── Solución final ────────────────────────────────────────────
    story.append(Paragraph('Solución final', section_style))
    y_sol = f"y(t) = {result['y_t_pretty']}"
    story.append(Paragraph(y_sol, math_style))
    story.append(Spacer(1, 8))

    # ── Gráfica ───────────────────────────────────────────────────
    if result.get('plot_b64'):
        story.append(Paragraph('Gráfica de y(t)', section_style))
        img_data = base64.b64decode(result['plot_b64'])
        img_buf = BytesIO(img_data)
        img = Image(img_buf, width=5.5*inch, height=2.5*inch)
        story.append(img)
        story.append(Spacer(1, 8))

    # ── Derivación paso a paso ────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=C_INDIGO, spaceAfter=6))
    story.append(Paragraph('Derivación paso a paso', section_style))

    for step in result.get('steps_text', []):
        story.append(Paragraph(f"Paso {step['num']}: {step['title']}", step_title_style))
        if step['math']:
            story.append(Paragraph(step['math'], math_style))
        story.append(Paragraph(step['theory'], theory_style))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laplace_solucion.pdf"'
    return response
```

- [ ] **Step 6: Agregar URL en solver/urls.py**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pdf/', views.export_pdf, name='export_pdf'),
]
```

- [ ] **Step 7: Agregar botón "Exportar PDF" en index.html** — dentro de `{% if result %}`, justo después del `answer-card` y antes de los pasos:

```html
    <!-- ── Botón Exportar PDF ── -->
    <form method="POST" action="{% url 'export_pdf' %}" style="margin:0">
      {% csrf_token %}
      <input type="hidden" name="order"     value="{{ form.order|default:'2' }}">
      <input type="hidden" name="a2"        value="{{ form.a2|default:'0' }}">
      <input type="hidden" name="a1"        value="{{ form.a1|default:'1' }}">
      <input type="hidden" name="a0"        value="{{ form.a0|default:'0' }}">
      <input type="hidden" name="rhs_type"  value="{{ form.rhs_type|default:'zero' }}">
      <input type="hidden" name="rhs_param" value="{{ form.rhs_param|default:'1' }}">
      <input type="hidden" name="y0"        value="{{ form.y0|default:'0' }}">
      <input type="hidden" name="dy0"       value="{{ form.dy0|default:'0' }}">
      <button type="submit" style="
        width:100%;padding:10px 16px;
        background:transparent;color:var(--green);
        border:1px solid rgba(16,185,129,0.4);
        border-radius:var(--radius-md);
        font-family:var(--font-head);font-weight:600;font-size:13px;
        cursor:pointer;transition:background 0.15s,border-color 0.15s;
        display:flex;align-items:center;justify-content:center;gap:8px;
      "
      onmouseover="this.style.background='rgba(16,185,129,0.08)'"
      onmouseout="this.style.background='transparent'">
        ↓ Exportar Reporte PDF
      </button>
    </form>
```

- [ ] **Step 8: Commit**

```bash
git add requirements.txt solver/math_engine.py solver/views.py solver/urls.py solver/templates/solver/index.html
git commit -m "feat: exportación a PDF con ReportLab (reporte académico completo)"
```

---

### Task 3: Interpretador de ecuaciones desde texto

**Files:**
- Modify: `solver/templates/solver/index.html` — agregar campo de texto + función JS `parseEquation()`

- [ ] **Step 1: Agregar el campo de texto en el formulario** — en `index.html`, justo antes del `<div class="order-tabs">`:

```html
          <!-- ── Parser de texto ── -->
          <div style="margin-bottom:18px">
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:8px">
              <label style="font-size:12px;font-weight:600;color:var(--text-secondary);
                            text-transform:uppercase;letter-spacing:0.5px">
                Escribir ecuación (texto)
              </label>
              <span class="tip">
                <span class="tip-icon">?</span>
                <span class="tip-bubble">
                  Escribe la ecuación directamente. Ejemplos:<br>
                  y'' + 3y' + 2y = 0<br>
                  y' - y = e^t<br>
                  y'' + y = sin(t)
                </span>
              </span>
            </div>
            <div style="display:flex;gap:8px">
              <input type="text" id="eq-text-input" placeholder="ej: y'' + 3y' + 2y = sin(t)"
                class="form-input" style="flex:1;font-family:var(--font-mono);font-size:13px">
              <button type="button" onclick="parseAndFill()"
                style="padding:8px 14px;background:var(--indigo-dim);color:var(--indigo);
                       border:1px solid rgba(129,140,248,0.3);border-radius:var(--radius-sm);
                       font-family:var(--font-head);font-size:13px;font-weight:600;
                       cursor:pointer;white-space:nowrap;transition:background 0.15s;"
                onmouseover="this.style.background='rgba(129,140,248,0.2)'"
                onmouseout="this.style.background='var(--indigo-dim)'">
                Parsear →
              </button>
            </div>
            <div id="parse-feedback" style="font-size:11px;margin-top:5px;min-height:16px;
                                            font-family:var(--font-mono);color:var(--text-muted)">
            </div>
          </div>
```

- [ ] **Step 2: Agregar función `parseEquation()` en el bloque `<script>`**:

```javascript
function parseEquation(raw) {
  const s = raw.trim()
               .replace(/\s+/g, '')
               .replace(/−/g, '-')
               .replace(/\*/g, '');
  const parts = s.split('=');
  if (parts.length < 2) return null;
  const lhs = parts[0];
  const rhs = parts.slice(1).join('=');

  function extractCoeff(str, pattern) {
    const m = str.match(pattern);
    if (!m) return null;
    const c = m[1];
    if (c === '' || c === '+') return 1;
    if (c === '-') return -1;
    const v = parseFloat(c);
    return isNaN(v) ? null : v;
  }

  // a2: coeff of y''
  const a2 = extractCoeff(lhs, /([+\-]?\d*\.?\d*)y''/);
  // Remove y'' term then get a1
  const lhsNo2 = lhs.replace(/[+\-]?\d*\.?\d*y''/, '');
  const a1 = extractCoeff(lhsNo2, /([+\-]?\d*\.?\d*)y'/);
  // Remove y' term then get a0
  const lhsNo21 = lhsNo2.replace(/[+\-]?\d*\.?\d*y'/, '');
  const a0 = extractCoeff(lhsNo21, /([+\-]?\d*\.?\d*)y/);

  if (a1 === null && a2 === null) return null;

  // Parse RHS
  let rhs_type = 'zero', rhs_param = '1';
  if (rhs === '0' || rhs === '') {
    rhs_type = 'zero';
  } else if (/^[+\-]?\d+\.?\d*$/.test(rhs)) {
    rhs_type = 'constant'; rhs_param = rhs;
  } else if (/tsin\(|tsin/.test(rhs) || /t\*?sin\(/.test(rhs)) {
    rhs_type = 'tsin';
    const m = rhs.match(/sin\(([^)t]*)t\)/);
    rhs_param = (m && m[1] && m[1] !== '') ? m[1].replace(/[+\-]?/,'') || '1' : '1';
  } else if (/te\^|t\*?e\^/.test(rhs)) {
    rhs_type = 'texp';
    const m = rhs.match(/e\^[\(]?([^\)t\*,\s]+)/);
    rhs_param = m ? m[1] : '1';
  } else if (/sin\(/.test(rhs)) {
    rhs_type = 'sin';
    const m = rhs.match(/sin\(([^)]*?)t\)/);
    rhs_param = (m && m[1] && m[1] !== '' && m[1] !== '+') ? m[1] : '1';
  } else if (/cos\(/.test(rhs)) {
    rhs_type = 'cos';
    const m = rhs.match(/cos\(([^)]*?)t\)/);
    rhs_param = (m && m[1] && m[1] !== '' && m[1] !== '+') ? m[1] : '1';
  } else if (/e\^/.test(rhs)) {
    rhs_type = 'exp';
    const m = rhs.match(/e\^[\(]?([^\)t\*,\s]+)/);
    rhs_param = m ? m[1] : '1';
  }

  const order = (a2 !== null && a2 !== 0) ? 2 : 1;
  return {
    order,
    a2: (a2 ?? 0).toString(),
    a1: (a1 ?? (order===1 ? 1 : 0)).toString(),
    a0: (a0 ?? 0).toString(),
    rhs_type, rhs_param
  };
}

function parseAndFill() {
  const raw = document.getElementById('eq-text-input').value;
  const fb  = document.getElementById('parse-feedback');
  const parsed = parseEquation(raw);
  if (!parsed) {
    fb.style.color = 'var(--red)';
    fb.textContent = '✗ No se pudo parsear. Revisa el formato: y\'\' + 3y\' + 2y = sin(t)';
    return;
  }
  setOrder(parsed.order);
  document.querySelector('[name=a2]').value        = parsed.a2;
  document.querySelector('[name=a1]').value        = parsed.a1;
  document.querySelector('[name=a0]').value        = parsed.a0;
  document.querySelector('[name=rhs_type]').value  = parsed.rhs_type;
  document.querySelector('[name=rhs_param]').value = parsed.rhs_param;
  updateRhsParam();
  fb.style.color = 'var(--green)';
  fb.textContent = `✓ Orden ${parsed.order} detectado — f(t): ${parsed.rhs_type}`;
}
```

- [ ] **Step 3: Commit**

```bash
git add solver/templates/solver/index.html
git commit -m "feat: interpretador de ecuaciones desde texto con parser JS"
```

---

### Task 4: Animaciones de pasos (cascada al resolver)

**Files:**
- Modify: `solver/templates/solver/index.html` — CSS keyframes + clases de animación

- [ ] **Step 1: Agregar keyframes y animaciones en el `<style>`** (antes del cierre `</style>`):

```css
    /* ═══════════════════════════════════════════════════════════════
       ANIMACIONES — Pasos en cascada
    ═══════════════════════════════════════════════════════════════ */
    @keyframes fadeInSlide {
      from { opacity: 0; transform: translateY(14px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
      from { opacity: 0; }
      to   { opacity: 1; }
    }

    .anim-fade { animation: fadeInSlide 0.4s ease both; }

    /* Cascada para los step-cards dentro del resultado */
    .results-panel .eq-summary  { animation: fadeInSlide 0.35s ease both; animation-delay: 0.0s; }
    .results-panel .answer-card { animation: fadeInSlide 0.38s ease both; animation-delay: 0.05s; }
    .results-panel .pdf-export  { animation: fadeInSlide 0.38s ease both; animation-delay: 0.08s; }

    .results-panel .step-card:nth-child(1) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.10s; }
    .results-panel .step-card:nth-child(2) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.17s; }
    .results-panel .step-card:nth-child(3) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.24s; }
    .results-panel .step-card:nth-child(4) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.31s; }
    .results-panel .step-card:nth-child(5) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.38s; }
    .results-panel .step-card:nth-child(6) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.45s; }
    .results-panel .step-card:nth-child(7) { animation: fadeInSlide 0.35s ease both; animation-delay: 0.52s; }

    .results-panel .plot-card   { animation: fadeInSlide 0.4s ease both;  animation-delay: 0.60s; }
```

- [ ] **Step 2: Agregar clase `pdf-export` al div del botón PDF** — envolver el formulario del PDF en `<div class="pdf-export">`:

```html
    <div class="pdf-export">
      <!-- form del botón Exportar PDF -->
    </div>
```

- [ ] **Step 3: Commit final**

```bash
git add solver/templates/solver/index.html
git commit -m "feat: animaciones de pasos en cascada al resolver EDO"
```
