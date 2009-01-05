#!/usr/bin/python
# vim: set fileencoding=utf-8:

from __future__ import division
from reportlab.platypus import (
    Frame, SimpleDocTemplate, BaseDocTemplate,
    Table, LongTable, TableStyle,
    PageTemplate, Spacer, Paragraph,
    FrameBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.rl_config import defaultPageSize
from reportlab.lib.units import inch, cm
from reportlab.lib import colors, pagesizes, styles
from time import localtime
from random import randrange
from operator import itemgetter
from itertools import groupby, chain, repeat

def thousand_separated(number, separator='.'):
    if not number: return '0'
    parts = []
    while number:
        parts.append(number % 1000)
        number //= 1000
    parts = map(str, reversed(parts))
    parts[1:] = [x.zfill(3) for x in parts[1:]]
    return separator.join(parts)

ss = getSampleStyleSheet()

style_normal = ParagraphStyle('normal', fontName='Helvetica')
style_serial = ParagraphStyle('serial', parent=style_normal)
style_serial.alignment = 2
#style_normal = styles['Normal']
#style_normal.fontName = 'Helvetica'

style_title = ParagraphStyle('title')
style_title.fontName = 'Helvetica-Bold'
style_title.alignment = styles.TA_CENTER

style_labsur = ParagraphStyle('logo', parent=ss['h1'])
style_labsur.backColor = colors.silver
style_labsur.alignment = styles.TA_CENTER

style_address = ParagraphStyle('address', parent=style_normal)
#style_address.leftIndent = -0.5*cm

W, H = pagesizes.letter

class Report(BaseDocTemplate):
    _firstPageTemplateIndex = 0
    #_nextPageTemplateCycle = chain([0], repeat(1))
    def __init__(self, *args, **kwargs):
        x = 2*cm
        w_form1, w_form2 = W/2, W/2 - 4*cm
        h_form = 2.7*cm
        w_table, h_table = (W - 3.9*cm)/5, 17.5*cm
        y_logo = H - 2*cm
        y_form = H - 5*cm
        y_table = H - h_table - 6*cm
        w_title, h_title = 5 * w_table, 1*cm
        y_title = y_table + h_table 
        pad = dict(('%sPadding' % d, 0) for d in ['left', 'right', 'top', 'bottom'])
        t1 = PageTemplate(frames=[
            Frame(x, y_logo, 3.4*cm, 2.5*cm, id='logo', **pad),
            Frame(x,           y_form, w_form1, h_form, id='left',  **pad),
            Frame(x + w_form1, y_form, w_form2, h_form, id='right', **pad),
            Frame(x, y_title, w_title, h_title, id='title', **pad),
            Frame(x,             y_table, w_table, h_table, id='panel1', **pad),
            Frame(x + 1*w_table, y_table, w_table, h_table, id='panel2', **pad),
            Frame(x + 2*w_table, y_table, w_table, h_table, id='panel3', **pad),
            Frame(x + 3*w_table, y_table, w_table, h_table, id='panel4', **pad),
            Frame(x + 4*w_table, y_table, w_table, h_table, id='panel5', **pad),
        ])
        t2 = PageTemplate(frames=[
            Frame( 2*cm, 8*cm, 5*cm, H-2*cm, showBoundary=True, id='panel3'),
            Frame( 2*cm, 8*cm, 5*cm, H-2*cm, showBoundary=True, id='panel4'),
        ])
        kwargs['showBoundary'] = True
        BaseDocTemplate.__init__(self, *args, **kwargs)
        self.addPageTemplates([t1])
    #def handle_pageBegin(self):
    #    BaseDocTemplate.handle_pageBegin(self)

    def printPageNumber(self, canvas, document):
        pass

date = localtime()[:3]
#document = SimpleDocTemplate('%04d-%02d-%02d-labsur.pdf' % date,
filename = '%04d-%02d-%02d-labsur.pdf' % date 
document = Report(filename, pageSize=(W, H))
print filename

styles = getSampleStyleSheet()
styleNormal = styles['Normal']
styleHeading = styles['Heading1']

data = [(randrange(5000, 15000), randrange(5000, 15000)) for i in range(160)]
data.sort(key=itemgetter(1), reverse=True)

header = [(None, u'Número\nde vaca', u'RCS\n\u00d71000')]
rows = [(i+1,j,thousand_separated(k)) for i, (j, k) in enumerate(data)]

story = []

form_data_1 = [(u'Propietario:', u'Roberto Bonvallet'),
               (u'RUT:',         u'15274426-9'),
               (u'Dirección:',   u'Av. Matta 540'),
               (u'Comuna:',      u'Valparaíso'),
               (u'Solicitante:', u'Nicol Rafałowska'),
               (u'Nro. examen:', u'12345'),]
form_data_2 = [(u'Fecha recepción:',      u'03/01/2008'),
               (u'Fecha informe:',        u'05/01/2008'),
               (u'Cantidad de muestras:', u'274'),
               (u'Técnica:',              u''),
               (u'Reactivo:',             u''),
               (u'Código examen:',        u'49'),]
base_form_style = TableStyle([
    ('FACE', (0, 0), (0, -1), 'Helvetica-Bold'),
    ('FACE', (1, 0), (1, -1), 'Helvetica'),
    ('SIZE', (0, 0), (-1, -1), 10),
    #('LEFTPADDING',   (0, 0), (0, -1),  0),
    #('LEFTPADDING',   (1, 0), (1, -1),  cm/3),
    ('RIGHTPADDING',  (0, 0), (-1, -1),  0),
    ('TOPPADDING',    (0, 0), (-1, -1),  0),
    ('BOTTOMPADDING', (0, 0), (-1, -1),  0),
])
form_style_1 = TableStyle([
    ('ALIGN', (1, 0), (1, -1), 'LEFT')
], parent=base_form_style)
form_style_2 = TableStyle([
    ('ALIGN', (1, 0), (1, -1), 'RIGHT')
], parent=base_form_style)

form_table_1 = Table(form_data_1, hAlign='LEFT', style=form_style_1)
form_table_2 = Table(form_data_2, hAlign='RIGHT', style=form_style_2)

somatic_table_style = TableStyle([
    ('FACE',      (0, 0), (-1, -1), 'Helvetica'),
    ('ALIGN',     (0, 1), (-1, -1), 'RIGHT'),
    ('VALIGN',    (0, 1), (-1, -1), 'BOTTOM'),
    ('SIZE',      (0, 0), (-1, -1),  8),
    ('SIZE',      (0, 1), ( 0, -1),  6),
    ('BOX',       (1, 0), (-1, -1), 0.25, colors.black),
    ('INNERGRID', (1, 0), (-1, -1), 0.25, colors.black),
    ('TOPPADDING',    (0, 0), (-1, -1),  1),
    ('BOTTOMPADDING', (0, 0), (-1, -1),  0),
    # header
    ('SIZE',       (1, 0), (-1,  0),  6),
    ('ALIGN',      (1, 0), (-1,  0), 'CENTER'),
    ('VALIGN',     (1, 0), (-1,  0), 'MIDDLE'),
    #('TOPPADDING',    (1, 0), (-1,  0), 0),
    #('BOTTONPADDING', (1, 0), (-1,  0), 0),
    ('BACKGROUND', (1, 0), (-1,  0), colors.silver),
])
somatic_table = Table(header + rows, repeatRows=1,
                      hAlign='LEFT', style=somatic_table_style)

logo_labsur = Paragraph(u'LABSUR', style_labsur)
logo_address = Paragraph(u'García Hurtado 930<br />'
                         u'Fono: (64) 643043<br />'
                         u'Osorno', style_address)
title = Paragraph(u'Células somáticas', style_title)
    
story = [
    FrameBreak('logo'),
    logo_labsur,
    logo_address,
    FrameBreak('left'),
    form_table_1,
    FrameBreak('right'),
    form_table_2,
    FrameBreak('title'),
    title,
    FrameBreak('panel1'),
    somatic_table,
]

document.build(story)

