from django.shortcuts import render
from django.http import HttpResponse
from io import BytesIO
from .math_engine import solve_ode, latex_to_text


# Casos de prueba predefinidos del PDF
EXAMPLES = [
    {
        'id': 1,
        'label': "y' + 2y = 0,  y(0)=1",
        'order': 1,
        'a2': '0', 'a1': '1', 'a0': '2',
        'rhs_type': 'zero', 'rhs_param': '0',
        'y0': '1', 'dy0': '0',
        'desc': 'Decaimiento exponencial puro (EDO homogénea de 1er orden)',
    },
    {
        'id': 2,
        'label': "y'' + 3y' + 2y = 0,  y(0)=0, y'(0)=1",
        'order': 2,
        'a2': '1', 'a1': '3', 'a0': '2',
        'rhs_type': 'zero', 'rhs_param': '0',
        'y0': '0', 'dy0': '1',
        'desc': 'Raíces reales distintas — sistema sobreamortiguado',
    },
    {
        'id': 3,
        'label': "y' − y = eᵗ,  y(0)=1",
        'order': 1,
        'a2': '0', 'a1': '1', 'a0': '-1',
        'rhs_type': 'exp', 'rhs_param': '1',
        'y0': '1', 'dy0': '0',
        'desc': 'EDO no homogénea con forzamiento exponencial',
    },
    {
        'id': 4,
        'label': "y'' + y = sin(t),  y(0)=0, y'(0)=0",
        'order': 2,
        'a2': '1', 'a1': '0', 'a0': '1',
        'rhs_type': 'sin', 'rhs_param': '1',
        'y0': '0', 'dy0': '0',
        'desc': 'Resonancia — frecuencia de forzamiento = frecuencia natural',
    },
]

RHS_LABELS = {
    'zero':     '0 (homogénea)',
    'constant': 'Constante C',
    'exp':      'eᵃᵗ',
    'sin':      'sin(bt)',
    'cos':      'cos(bt)',
    'texp':     't·eᵃᵗ',
    'tsin':     't·sin(bt)',
}


def index(request):
    context = {
        'examples': EXAMPLES,
        'rhs_labels': RHS_LABELS,
        'result': None,
        'error': None,
        'form': {},
    }

    if request.method == 'POST':
        form = dict(request.POST)
        # Flatten single-value lists
        flat = {k: v[0] if isinstance(v, list) and len(v) == 1 else v
                for k, v in form.items()}
        context['form'] = flat

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
            context['result'] = result
        except Exception as e:
            context['error'] = str(e)

    return render(request, 'solver/index.html', context)


def export_pdf(request):
    """Genera un reporte académico PDF con la solución completa de la EDO."""
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
        return HttpResponse(f'Error al generar PDF: {e}', status=400)

    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Image, HRFlowable
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
    C_AMBER  = colors.HexColor('#d97706')
    C_GREEN  = colors.HexColor('#059669')
    C_INDIGO = colors.HexColor('#6366f1')
    C_DARK   = colors.HexColor('#0f172a')
    C_TEXT   = colors.HexColor('#1e293b')
    C_MUTED  = colors.HexColor('#64748b')

    title_style = ParagraphStyle('Title', parent=styles['Heading1'],
        fontSize=20, textColor=C_DARK, spaceAfter=4,
        fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'],
        fontSize=10, textColor=C_MUTED, spaceAfter=14)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'],
        fontSize=13, textColor=C_AMBER, spaceBefore=14, spaceAfter=6,
        fontName='Helvetica-Bold')
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
        fontSize=11, textColor=C_TEXT, spaceAfter=4, leading=16)
    math_style = ParagraphStyle('Math', parent=styles['Normal'],
        fontSize=12, textColor=C_DARK, spaceAfter=8,
        fontName='Courier-Bold',
        backColor=colors.HexColor('#f1f5f9'),
        borderPadding=(6, 10, 6, 10),
        leftIndent=8, rightIndent=8)
    step_title_style = ParagraphStyle('StepTitle', parent=styles['Normal'],
        fontSize=11, textColor=C_INDIGO, spaceAfter=3,
        fontName='Helvetica-Bold', spaceBefore=10)
    theory_style = ParagraphStyle('Theory', parent=styles['Normal'],
        fontSize=9, textColor=C_MUTED, spaceAfter=6, leading=14,
        leftIndent=14)

    story = []

    # ── Encabezado ────────────────────────────────────────────────
    story.append(Paragraph('Transformada de Laplace — Solución de EDO', title_style))
    story.append(Paragraph(
        'Universidad Tecnológica Emiliano Zapata · UTEZ · 8vo Cuatrimestre',
        sub_style
    ))
    story.append(HRFlowable(width='100%', thickness=2, color=C_AMBER, spaceAfter=10))

    # ── Ecuación ingresada ────────────────────────────────────────
    story.append(Paragraph('Ecuación Diferencial', section_style))
    eq_text = latex_to_text(result['equation_latex'])
    ic_text = latex_to_text(result['ic_latex'])
    story.append(Paragraph(eq_text, math_style))
    story.append(Paragraph(f'Condiciones iniciales:  {ic_text}', body_style))
    story.append(Spacer(1, 6))

    # ── Solución final ────────────────────────────────────────────
    story.append(Paragraph('Solución Final', section_style))
    story.append(Paragraph(f"y(t)  =  {result['y_t_pretty']}", math_style))
    story.append(Spacer(1, 6))

    # ── Gráfica ───────────────────────────────────────────────────
    if result.get('plot_b64'):
        story.append(Paragraph('Gráfica de y(t)', section_style))
        img_data = base64.b64decode(result['plot_b64'])
        img_buf = BytesIO(img_data)
        img = Image(img_buf, width=5.8*inch, height=2.6*inch)
        story.append(img)
        story.append(Paragraph(
            'Línea ámbar: solución exacta (Laplace) · Línea cyan: RK4 numérico',
            theory_style
        ))
        story.append(Spacer(1, 8))

    # ── Pasos de derivación ───────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=C_INDIGO, spaceAfter=4))
    story.append(Paragraph('Derivación Paso a Paso', section_style))

    for step in result.get('steps_text', []):
        story.append(Paragraph(
            f"Paso {step['num']}: {step['title']}", step_title_style
        ))
        if step['math']:
            story.append(Paragraph(step['math'], math_style))
        story.append(Paragraph(step['theory'], theory_style))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="laplace_solucion.pdf"'
    return response
