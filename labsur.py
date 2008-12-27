#!/usr/bin/env python
# vim: fileencoding=utf-8

try:
    from collections import namedtuple
except ImportError:
    from namedtuple import namedtuple
from string import Template
from datetime import datetime
from operator import attrgetter
import pygtk
pygtk.require20()
import gtk

CowStats = namedtuple('CowStats', ['nr_cow', 'mat', 'prot', 'nn', 'cells'])

TEMPLATE_FILE = r'template'

class CowStatsParseError(Exception):
    pass

def parse_cow_file(f):
    cows = list()
    for n, line in enumerate(f):
        if not line.strip():
            continue
        try:
           row = CowStats(*map(int, line.strip().split(',')))
        except:
           print 'Registro invalido en linea %d del archivo: "%s"' % (n+1, repr(line))
        else:
            cows.append(row)
    return cows


class Application:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('LabSur')
        self.window.connect('delete_event', self.quit)
        self.window.set_default_size(200, 500)

        self.vbox = gtk.VBox()
        self.vbox.show()
        self.window.add(self.vbox)

        self.button_box = gtk.HBox()
        self.button_box.show()
        self.vbox.pack_start(self.button_box, expand=False)

        self.load_button = gtk.Button('Cargar datos')
        self.load_button.connect('clicked', self.load, None)
        self.button_box.pack_start(self.load_button)
        self.load_button.show()

        self.export_button = gtk.Button('Exportar')
        self.export_button.connect('clicked', self.export, None)
        self.button_box.pack_start(self.export_button)
        self.export_button.show()

        self.print_button = gtk.Button('Crear version imprimible')
        self.print_button.connect('clicked', self.printable, None)
        self.button_box.pack_start(self.print_button)
        self.print_button.show()

        self.quit_button = gtk.Button('Salir')
        self.quit_button.connect('clicked', self.quit)
        self.button_box.pack_start(self.quit_button)
        self.quit_button.show()

        self.form = gtk.Table(8, 4, False)
        s = self.add_form_item
        self.fields = {
          'NUMEROSOLICITUD':s('Nro. solicitud', 0, 0),

          'PROPIETARIO':    s('Propietario',    1, 0),
          'RUT':            s('Rut',            2, 0),
          'DIRECCION':      s('Direccion',      3, 0),
          'COMUNA':         s('Comuna',         4, 0),
          'SOLICITANTE':    s('Solicitante',    5, 0),
          'NUMEROEXAMEN':   s('Nro. examen',    6, 0),
          'FECHARECEPCION': s('Fecha recepcion',   0, 1),
          'FECHAINFORME':   s('Fecha informe',     1, 1),
          'CANTMUESTRAS':   s('Cantidad muestras', 2, 1),
          'TECNICA':        s('Tecnica',           3, 1),
          'REACTIVO':       s('Reactivo',          4, 1),
          'CODIGOEXAMEN':   s('Codigo examen',     5, 1),

          'NOMBRE':         s('Firma', 6, 1),
          'CARGO':          s('Cargo', 7, 1),
        }
        tab_order = ['NUMEROSOLICITUD',
            'PROPIETARIO', 'RUT', 'DIRECCION', 'COMUNA',
            'SOLICITANTE', 'NUMEROEXAMEN', 
            'FECHARECEPCION', 'FECHAINFORME', 'CANTMUESTRAS',
            'TECNICA', 'REACTIVO', 'CODIGOEXAMEN', 
            'NOMBRE', 'CARGO']
        self.form.set_focus_chain([self.fields[key] for key in tab_order])
        self.form.show()
        self.vbox.pack_start(self.form, expand=False)

        self.data_box = gtk.ScrolledWindow()
        self.data_box.show()
        self.vbox.pack_start(self.data_box, expand=True)

        self.data_view = gtk.TreeView()
        self.data_view.show()
        self.data_box.add(self.data_view)

        v = self.data_view.get_vadjustment()
        self.data_box.set_vadjustment(v)
        self.data_box.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)

        self.cow_count_column = gtk.TreeViewColumn('#')
        self.data_view.append_column(self.cow_count_column)
        cell = gtk.CellRendererText()
        self.cow_count_column.pack_start(cell, True)
        self.cow_count_column.set_attributes(cell, text=0)

        self.nr_cow_column = gtk.TreeViewColumn('Nro. Vaca')
        self.data_view.append_column(self.nr_cow_column)
        cell = gtk.CellRendererText()
        self.nr_cow_column.pack_start(cell, True)
        self.nr_cow_column.set_attributes(cell, text=1)

        self.cells_column = gtk.TreeViewColumn('RCS')
        self.data_view.append_column(self.cells_column)
        cell = gtk.CellRendererText()
        self.cells_column.pack_start(cell, True)
        self.cells_column.set_attributes(cell, text=5)

        self.data = None

        self.window.show()


    def add_form_item(self, label, row, col):
        l = gtk.Label(label)
        l.show()
        self.form.attach(l, 2*col, 2*col+1, row, row+1)
        e = gtk.Entry()
        e.set_alignment(0.0)
        e.show()
        self.form.attach(e, 2*col+1, 2*col+2, row, row+1)
        return e

    def load(self, *args):
        self.list_store = gtk.ListStore(int, int, int, int, int, int)
        file_name = self.choose_data_source()
        self.data = []
        cow_file = open(file_name)
        for cow in parse_cow_file(cow_file):
            self.data.append(cow)
        self.data.sort(key=attrgetter('cells'), reverse=True)
        for i, cow in enumerate(self.data):
            self.list_store.append((i + 1,) + cow)
        self.data_view.set_model(self.list_store)

    def export(self, *args):
        if not self.data:
            print "No hay datos para exportar"
            return
        file_name = self.choose_export_name()
        data_file = open(file_name, 'w')
        for cow in self.data:
            reg = "%-8s%-4s%-4s%-4s%1s%3s" % (cow.nr_cow, cow.mat, cow.cells, cow.prot, chr(10), 3 * "\n")
            data_file.write(reg)
        data_file.write('9' * len(reg)) # registro con nueves para marcar final
        data_file.close()

    def printable(self, *args):
        if not self.data:
            print "No hay datos para imprimir"
            return
        report_template = Template(open(TEMPLATE_FILE).read())
        file_name = self.choose_report_name()
        report_file = open(file_name, 'w')

        report_data = {}
        for k, v in self.fields.items():
            report_data[k] = v.get_text()
        report_data['TABLA'] = self.data_to_html()

        report_file.write(report_template.substitute(report_data))
        report_file.close()

    
    def choose_data_source(self):
        return self.choose_file('Abrir archivo de datos',
                                gtk.FILE_CHOOSER_ACTION_OPEN,
                                extension='lab')
    def choose_report_name(self):
        return self.choose_file('Guardar informe como',
                                gtk.FILE_CHOOSER_ACTION_SAVE,
                                current_name='informe.html',
                                extension='html',
                                directory='Informes')
    def choose_export_name(self):
        return self.choose_file('Exportar datos como',
                                gtk.FILE_CHOOSER_ACTION_SAVE,
                                current_name='export.dat',
                                extension='dat',
                                directory='Datos')

    def choose_file(self, title, action, current_name=None, extension=None, directory=None):
        b = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
        chooser = gtk.FileChooserDialog(title=title, action=action, buttons=b)
        if current_name:
            chooser.set_current_name(current_name)
        if extension:
            f = gtk.FileFilter()
            f.add_pattern('*.%s' % extension)
            chooser.add_filter(f)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            name = chooser.get_filename()
        else:
            name = None
        chooser.destroy()
        return name

    def data_to_html(self):
        COLUMNS = 4
        headers = ('Corr', 'Nro. vaca', 'RCS')
        row_template = '<tr>' + 3 * '<td>%s</rd>' + '</tr>'
        fields = [(i+1, cow.nr_cow, cow.cells) for i, cow in enumerate(self.data)]
        rows = [row_template % field for field in fields]
        tables = [rows[i::COLUMNS] for i in range(COLUMNS)]
        for table in tables:
            table.insert(0, row_template % headers)
        tables = [''.join(table) for table in tables]
        tables = ['<table class="cell-table">%s</table>' % table for table in tables]
        return ''.join(tables)


    def main(self):
        gtk.main()
    def quit(self, *args):
        gtk.main_quit()
        return False


if __name__ == '__main__':
    app = Application()
    app.main()

