from django.shortcuts import render
from .math_engine import solve_ode


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
