#!/usr/bin/python
# vim: set fileencoding=utf-8:

from __future__ import division
from reportlab.platypus import (
    Frame, SimpleDocTemplate, BaseDocTemplate,
    Table, LongTable, TableStyle,
    PageTemplate, Spacer, Paragraph,
    FrameBreak, NextPageTemplate,
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

# Paragraph styles
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

# Table Styles
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

W, H = pagesizes.letter

class Report(BaseDocTemplate):
    _firstPageTemplateIndex = 0
    def __init__(self, *args, **kwargs):
        x = 2*cm
        w_form1, h_form1 = W/2, 2.7*cm
        w_form2, h_form2 = W/2 - 4*cm, h_form1
        y_form           = H - 5*cm
        w_table, h_table = (W - 3.9*cm)/5, 17.5*cm
        y_table          = H - h_table - 6*cm
        w_logo, h_logo   = 3.4*cm, 2.5*cm
        y_logo           = H - 2*cm
        w_title, h_title = 5 * w_table, 0.6*cm
        w_serial, h_serial = 5*cm, h_title
        x_serial, y_serial = W - w_serial - 2*cm, H - h_serial
        y_title = y_table + h_table 
        x_signature, y_signature = 2*cm, 2*cm
        w_signature, h_signature = 5*cm, 2*cm
        pad = dict(('%sPadding' % d, 0) for d in ['left', 'right', 'top', 'bottom'])
        t1 = PageTemplate(id='p1', frames=[
            Frame(x, y_logo, w_logo, h_logo, id='logo', **pad),
            Frame(x_serial, y_serial, w_serial, h_title, id='serial', **pad),
            Frame(x,           y_form, w_form1, h_form1, id='left',  **pad),
            Frame(x + w_form1, y_form, w_form2, h_form2, id='right', **pad),
            Frame(x, y_title, w_title, h_title, id='title', **pad),
            Frame(x,             y_table, w_table, h_table, id='panel1', **pad),
            Frame(x + 1*w_table, y_table, w_table, h_table, id='panel2', **pad),
            Frame(x + 2*w_table, y_table, w_table, h_table, id='panel3', **pad),
            Frame(x + 3*w_table, y_table, w_table, h_table, id='panel4', **pad),
            Frame(x + 4*w_table, y_table, w_table, h_table, id='panel5', **pad),
        ], onPage=self.printFooter)
        h_table = H - 4*cm
        t2 = PageTemplate(id='p2', frames=[
            Frame(x,             y_table, w_table, h_table, id='panel1', **pad),
            Frame(x + 1*w_table, y_table, w_table, h_table, id='panel2', **pad),
            Frame(x + 2*w_table, y_table, w_table, h_table, id='panel3', **pad),
            Frame(x + 3*w_table, y_table, w_table, h_table, id='panel4', **pad),
            Frame(x + 4*w_table, y_table, w_table, h_table, id='panel5', **pad),
        ], onPage=self.printFooter)
        #kwargs['showBoundary'] = True
        BaseDocTemplate.__init__(self, *args, **kwargs)
        self.addPageTemplates([t1, t2])

    def setNameAndJob(self, name, job):
        self.name = name
        self.job  = job

    def printFooter(self, canvas, document):
        canvas.saveState()
        # page number
        page_str = u'Página %d' % (document.page)
        canvas.drawRightString(W - 2*cm, 1.5*cm, page_str)
        # signature
        x, y = W/2 - 4*cm, 2.5*cm
        w = 6*cm
        canvas.drawCentredString(x, 2*cm, self.name)
        canvas.drawCentredString(x, 1.5*cm, self.job)
        canvas.line(x - w/2, y, x+w/2, y)

        canvas.restoreState()


def create_report(report_data, data, filename):
    document = Report(filename, pageSize=(W, H))

    header = [(None, u'Número\nde vaca', u'RCS\n\u00d71000')]
    rows = [(i+1, cow.nr_cow, thousand_separated(cow.cells))
            for i, cow in enumerate(data)]

    form_data_1 = [(u'Propietario:', report_data['PROPIETARIO']),
                   (u'RUT:',         report_data['RUT']),
                   (u'Dirección:',   report_data['DIRECCION']),
                   (u'Comuna:',      report_data['COMUNA']),
                   (u'Solicitante:', report_data['SOLICITANTE']),
                   (u'Nro. examen:', report_data['NUMEROEXAMEN']),]
    form_data_2 = [(u'Fecha recepción:',      report_data['FECHARECEPCION']),
                   (u'Fecha informe:',        report_data['FECHAINFORME']),
                   (u'Cantidad de muestras:', report_data['CANTMUESTRAS']),
                   (u'Técnica:',              report_data['TECNICA']),
                   (u'Reactivo:',             report_data['REACTIVO']),
                   (u'Código examen:',        report_data['CODIGOEXAMEN']),]
    form_table_1 = Table(form_data_1, hAlign='LEFT', style=form_style_1)
    form_table_2 = Table(form_data_2, hAlign='RIGHT', style=form_style_2)

    somatic_table = Table(header + rows, repeatRows=1,
                          hAlign='LEFT', style=somatic_table_style)

    logo_labsur = Paragraph(u'LABSUR', style_labsur)
    logo_address = Paragraph(u'García Hurtado 930<br />'
                             u'Fono: (64) 643043<br />'
                             u'Osorno', style_address)
    title = Paragraph(u'Células somáticas', style_title)
    serial = Paragraph(u'<b>Nro. solicitud:</b> %s' % report_data['NUMEROSOLICITUD'], style_serial)

    document.setNameAndJob(report_data['NOMBRE'], report_data['CARGO'])
        
    story = [
        FrameBreak('logo'),
        logo_labsur,
        logo_address,
        FrameBreak('serial'),
        serial,
        FrameBreak('left'),
        form_table_1,
        FrameBreak('right'),
        form_table_2,
        FrameBreak('title'),
        title,
        FrameBreak('panel1'),
        NextPageTemplate('p2'),
        somatic_table,
    ]

    document.build(story)

