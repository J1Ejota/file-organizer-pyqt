import sys
import os
import ctypes
from PyQt5 import QtWidgets, QtGui
from organizer_pyqt import organize_directory, deshacer_ultimo_ordenamiento

class OrganizadorArchivos(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Organizador de Archivos")
        self.setGeometry(200, 200, 560, 600)

        # Icono robusto (funciona también en modo PyInstaller)
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("organizador.archivos")

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        icon_path = os.path.join(base_path, "ico.ico")
        self.setWindowIcon(QtGui.QIcon(icon_path))

        # 🌒 Aplicar tema oscuro
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #dddddd;
                font-family: Segoe UI, sans-serif;
            }
            QPushButton {
                background-color: #3c3f41;
                border: 1px solid #5a5a5a;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #505357;
            }
            QLineEdit, QPlainTextEdit {
                background-color: #3c3f41;
                color: #dddddd;
                border: 1px solid #5a5a5a;
            }
            QCheckBox, QLabel {
                padding: 2px;
            }
            QGroupBox {
                border: 1px solid #555;
                margin-top: 10px;
            }
            QGroupBox:title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

        self.categorias = [
            "Documentos", "Imágenes", "Vídeos",
            "Audio", "Archivos comprimidos", "Ejecutables"
        ]

        self.init_ui()
        self.init_atajos()

    def init_atajos(self):
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self).activated.connect(self.organizar)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Z"), self).activated.connect(self.deshacer)
        QtWidgets.QShortcut(QtGui.QKeySequence("Escape"), self).activated.connect(self.close)

    def init_ui(self):
        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel("Selecciona el directorio a organizar:")
        layout.addWidget(self.label)

        self.entry = QtWidgets.QLineEdit()
        self.entry.setPlaceholderText("Ruta del directorio...")
        self.entry.setToolTip("Introduce manualmente la ruta o pulsa el botón para seleccionarla")
        layout.addWidget(self.entry)

        boton_buscar = QtWidgets.QPushButton("Buscar carpeta...")
        boton_buscar.setToolTip("Abrir un selector de carpetas")
        boton_buscar.clicked.connect(self.seleccionar_directorio)
        layout.addWidget(boton_buscar)

        # Opciones generales
        self.include_exe = QtWidgets.QCheckBox("Incluir archivos ejecutables (.exe, .msi)")
        self.include_exe.setToolTip("Activa esta opción si quieres organizar archivos ejecutables")
        self.preview_mode = QtWidgets.QCheckBox("Vista previa (no mover archivos)")
        self.preview_mode.setChecked(True)
        self.preview_mode.setToolTip("Simula la organización sin mover archivos")
        self.abrir_carpeta = QtWidgets.QCheckBox("Abrir carpeta al finalizar")
        self.abrir_carpeta.setChecked(True)
        self.abrir_carpeta.setToolTip("Abre la carpeta una vez finalice el proceso")

        layout.addWidget(self.include_exe)
        layout.addWidget(self.preview_mode)
        layout.addWidget(self.abrir_carpeta)

        # Filtros por categoría
        self.filtros = {}
        grupo_filtros = QtWidgets.QGroupBox("Tipos de archivo a organizar")
        layout_filtros = QtWidgets.QVBoxLayout()

        for cat in self.categorias:
            chk = QtWidgets.QCheckBox(cat)
            chk.setChecked(True)
            chk.setToolTip(f"Incluye archivos de tipo {cat.lower()}")
            layout_filtros.addWidget(chk)
            self.filtros[cat] = chk

        grupo_filtros.setLayout(layout_filtros)
        layout.addWidget(grupo_filtros)

        # Botones principales
        self.boton_organizar = QtWidgets.QPushButton("Organizar archivos")
        self.boton_organizar.setToolTip("Inicia el proceso de organización de archivos")
        self.boton_organizar.clicked.connect(self.organizar)
        layout.addWidget(self.boton_organizar)

        self.boton_deshacer = QtWidgets.QPushButton("Deshacer último ordenamiento")
        self.boton_deshacer.setToolTip("Revierte la última organización realizada")
        self.boton_deshacer.clicked.connect(self.deshacer)
        layout.addWidget(self.boton_deshacer)

        self.boton_ayuda = QtWidgets.QPushButton("Ayuda / Manual de usuario")
        self.boton_ayuda.setToolTip("Muestra el manual de uso y atajos")
        self.boton_ayuda.clicked.connect(self.mostrar_ayuda)
        layout.addWidget(self.boton_ayuda)

        self.estado = QtWidgets.QLabel("Listo")
        self.estado.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.estado)

        widget.setLayout(layout)

    def seleccionar_directorio(self):
        carpeta = QtWidgets.QFileDialog.getExistingDirectory(self, "Selecciona carpeta")
        if carpeta:
            self.entry.setText(carpeta)

    def mostrar_ayuda(self):
        texto = (
            "📘 MANUAL DE USUARIO\n\n"
            "Esta herramienta organiza archivos en subcarpetas por tipo.\n"
            "Selecciona un directorio, elige los tipos de archivo, y pulsa 'Organizar archivos'.\n\n"
            "🔧 OPCIONES:\n"
            "- Vista previa: simula sin mover archivos.\n"
            "- Ejecutables: incluye archivos .exe y .msi si se marca.\n"
            "- Abrir carpeta: abre el directorio al terminar (si no está en vista previa).\n\n"
            "🗂️ FILTROS:\n"
            "Puedes elegir qué tipos de archivo organizar (documentos, imágenes, vídeos, etc.).\n\n"
            "↩️ DESHACER:\n"
            "Usa 'Deshacer' para revertir el último ordenamiento. Solo afecta a la última acción.\n\n"
            "⌨️ ATAJOS DE TECLADO:\n"
            "- Ctrl + O → Organizar archivos\n"
            "- Ctrl + Z → Deshacer\n"
            "- Esc → Salir\n\n"
            "📂 Las imágenes y vídeos se agrupan además por fecha (dd-mm-aaaa).\n\n"
            "⚠️ Archivos protegidos del sistema o innecesarios se excluyen automáticamente.\n"
        )
        QtWidgets.QMessageBox.information(self, "Ayuda - Manual de usuario", texto)

    def organizar(self):
        carpeta = self.entry.text()
        incluir_exe = self.include_exe.isChecked()
        vista_previa = self.preview_mode.isChecked()
        abrir_carpeta = self.abrir_carpeta.isChecked()
        categorias_permitidas = [cat for cat, chk in self.filtros.items() if chk.isChecked()]

        if not carpeta or not os.path.isdir(carpeta):
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona un directorio válido.")
            return

        if not categorias_permitidas:
            QtWidgets.QMessageBox.warning(self, "Advertencia", "Debes seleccionar al menos una categoría.")
            return

        self.estado.setText("Organizando archivos...")
        self.boton_organizar.setDisabled(True)
        self.boton_deshacer.setDisabled(True)
        QtWidgets.QApplication.processEvents()

        try:
            resumen = organize_directory(
                carpeta,
                include_executables=incluir_exe,
                preview=vista_previa,
                categorias_permitidas=categorias_permitidas
            )

            if resumen:
                texto = ""
                for categoria, datos in resumen.items():
                    archivos = "\n    ".join(datos["archivos"])
                    texto += f"{categoria} ({datos['cuenta']} archivo/s):\n    {archivos}\n\n"
                self.mostrar_resumen("Vista previa de organización" if vista_previa else "Organización completada", texto)
            else:
                QtWidgets.QMessageBox.information(self, "Sin cambios", "No se movió ningún archivo.")

            if abrir_carpeta and not vista_previa:
                try:
                    os.startfile(carpeta)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Aviso", f"No se pudo abrir la carpeta:\n{e}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
        finally:
            self.estado.setText("Listo")
            self.boton_organizar.setDisabled(False)
            self.boton_deshacer.setDisabled(False)

    def deshacer(self):
        carpeta = self.entry.text()
        if not carpeta or not os.path.isdir(carpeta):
            QtWidgets.QMessageBox.warning(self, "Error", "Selecciona un directorio válido.")
            return

        confirmar = QtWidgets.QMessageBox.question(
            self, "Confirmar", "¿Deseas deshacer el último ordenamiento?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if confirmar == QtWidgets.QMessageBox.Yes:
            self.estado.setText("Deshaciendo ordenamiento...")
            self.boton_organizar.setDisabled(True)
            self.boton_deshacer.setDisabled(True)
            QtWidgets.QApplication.processEvents()

            exito = deshacer_ultimo_ordenamiento(carpeta)
            if exito:
                QtWidgets.QMessageBox.information(self, "Éxito", "Se ha deshecho el último ordenamiento.")
            else:
                QtWidgets.QMessageBox.warning(self, "Aviso", "No se encontró historial o ocurrió un error.")

            self.estado.setText("Listo")
            self.boton_organizar.setDisabled(False)
            self.boton_deshacer.setDisabled(False)

    def mostrar_resumen(self, titulo, contenido):
        ventana_resumen = QtWidgets.QDialog(self)
        ventana_resumen.setWindowTitle(titulo)
        ventana_resumen.resize(560, 400)

        layout = QtWidgets.QVBoxLayout()

        texto = QtWidgets.QPlainTextEdit()
        texto.setPlainText(contenido)
        texto.setReadOnly(True)
        layout.addWidget(texto)

        cerrar_btn = QtWidgets.QPushButton("Cerrar")
        cerrar_btn.clicked.connect(ventana_resumen.accept)
        layout.addWidget(cerrar_btn)

        ventana_resumen.setLayout(layout)
        ventana_resumen.exec_()

if __name__ == "__main__":
    from PyQt5 import QtCore
    app = QtWidgets.QApplication(sys.argv)
    ventana = OrganizadorArchivos()
    ventana.show()
    sys.exit(app.exec_())
