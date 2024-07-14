from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import QDate, Qt
from PyQt6.uic.load_ui import loadUi

from modelos.usuario import Usuario
from modelos.cliente import Cliente
from modelos.transaccion import Transaccion

from utils.pdf_generador import generar_pdf
from bd.base_de_datos import BD

from datetime import datetime
import sys
import os


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super(VentanaPrincipal, self).__init__()

        # Creo las tablas
        self.bd = BD()
        self.bd.crear_tablas()

        # Instancias
        self.login_ui = loadUi(os.path.join("Front", "Login3", "loginUI3.ui"))
        self.main_ui = None
        self.modificar_cliente_ui = None
        self.modificar_transaccion_ui = None

        # Login buttons
        self.login_ui.bt_login_ingreso.clicked.connect(self.login)

        # Centro y muestro el login
        self.center_window(self.login_ui)
        self.login_ui.show()


    def inicializar_main_ui(self):
        if self.main_ui is None:
            self.main_ui = loadUi(os.path.join("Front", "Proyecto_Inmobiliaria.ui"))

        self.main_ui.stackedWidget.setCurrentWidget(self.main_ui.page_1gestion_clientes)
        self.main_ui.closeEvent = lambda event: self.custom_close_event(event)
        self.center_window(self.main_ui)

        # Main UI menu lateral buttons
        self.main_ui.bt_registrar_menulateral.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_1gestion_clientes))
        self.main_ui.bt_transacciones_menulateral.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_5gestion_transacciones))
        self.main_ui.bt_pagos_menulateral.clicked.connect(lambda: (
            self.cambiar_pestaña(self.main_ui.page_12lista_pagos),
            self.abrir_lista_pagos()
            ))
        self.main_ui.bt_salir_menulateral.clicked.connect(lambda: sys.exit())

        # Menu Clientes Buttons
        self.main_ui.bt_gestionar_cliente.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_2registrar_cliente))
        self.main_ui.bt_listar_cliente.clicked.connect(lambda: (
            self.cambiar_pestaña(self.main_ui.page_4eliminar_cliente), 
            self.actualizar_tabla_clientes(Cliente.get())
            ))

        # Listado de clientes
        self.main_ui.bt_eliminar_cliente_2.clicked.connect(lambda: self.eliminar_row(self.main_ui.tabla_cliente, Cliente))
        self.main_ui.bt_volver_menu.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_1gestion_clientes))
        self.main_ui.buscar_cliente.textChanged.connect(self.buscar_clientes)
        self.main_ui.bt_modificar_cliente_2.clicked.connect(self.abrir_modificar_cliente)

        # Agregar cliente
        self.main_ui.bt_Aceptar_Cliente.clicked.connect(self.agregar_cliente)
        self.main_ui.bt_volver_cliente.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_1gestion_clientes))

        # Menu Transacciones Buttons
        self.main_ui.bt_agregar_Transaccion.clicked.connect(self.abrir_agregar_transaccion)
        self.main_ui.bt_listar_Transaccion.clicked.connect(lambda: (
            self.cambiar_pestaña(self.main_ui.page_8lista_transacciones),
            self.actualizar_tabla_transacciones(Transaccion.get())
            ))
        
        # Listado de transacciones
        self.main_ui.buscar_transacciones.textChanged.connect(self.buscar_transacciones)
        self.main_ui.bt_eliminar_transaccion.clicked.connect(lambda: self.eliminar_row(self.main_ui.tabla_transacciones, Transaccion))
        self.main_ui.bt_Volver_Menu.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_5gestion_transacciones))
        self.main_ui.bt_pdf_transaccion.clicked.connect(self.generar_pdf)
        self.main_ui.bt_eliminar_transaccion_2.clicked.connect(self.abrir_modificar_transaccion)

        # Agregar transacciones
        self.main_ui.bt_guardar_transaccion.clicked.connect(self.agregar_transaccion)
        self.main_ui.bt_volver_menu_transaccion.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_5gestion_transacciones))        

        # Listado de Pagos
        self.main_ui.bt_buscar_lista_pagos.clicked.connect(self.actualizar_tabla_pagos)   
        self.main_ui.bt_modificar_pago.clicked.connect(lambda: self.modificar_pago(True))
        self.main_ui.pushButton_35.clicked.connect(lambda: self.modificar_pago(False)) 

    def inicializar_modificar_cliente(self):
        self.modificar_cliente_ui = loadUi(os.path.join("Front", "Modificar Cliente Ventana.ui"))

        # Botones
        self.modificar_cliente_ui.bt_actualizar_tabla.clicked.connect(self.actualizar_cliente)
        self.modificar_cliente_ui.bt_volver_modificar_cliente.clicked.connect(self.modificar_cliente_ui.hide)
        self.center_window(self.modificar_cliente_ui)

    def inicializar_modificar_transaccion(self):
        self.modificar_transaccion_ui = loadUi(os.path.join("Front", "Modificar Transaccion Ventana.ui"))

        # Botones
        self.modificar_transaccion_ui.bt_volver_modificar_transaccion.clicked.connect(self.modificar_transaccion_ui.hide)
        self.modificar_transaccion_ui.bt_guardar_modificar_transaccion.clicked.connect(self.actualizar_transaccion)

        # Centrar
        self.center_window(self.modificar_transaccion_ui)


    def login(self):
        # Inicio sesión
        contraseña = self.login_ui.bt_line_usuario.text()
        nombre = self.login_ui.bt_line_contrasenia.text()

        usuario = Usuario.login(nombre, contraseña)

        if usuario != None:
            self.login_ui.hide()

            self.inicializar_main_ui()
            self.main_ui.show()

            QMessageBox.information(self, "Éxito", f"Inicio de sesión exitoso\n Bienvenido/a {usuario.nombre}.")
        else:
            QMessageBox.warning(self, "Error de Inicio de Sesión", "Nombre de usuario o contraseña incorrectos.")


    def agregar_cliente(self):
        nombre = self.main_ui.line_nombre_registro_cliente
        apellido = self.main_ui.line_apellido_registro_cliente
        telefono = self.main_ui.line_telefono_registro_cliente
        cuit = self.main_ui.line_cuit_registro_cliente

        nuevo_cliente = Cliente(nombre.text(), apellido.text(), cuit.text(), telefono.text() if telefono.text() != "" else None)

        if nuevo_cliente.crear() == True:
            QMessageBox.information(self, "Éxito", f"{nuevo_cliente.nombre} {nuevo_cliente.apellido} ha sido agregado exitosamente.")
            nombre.clear()
            apellido.clear()
            telefono.clear()
            cuit.clear()
        else:
            QMessageBox.critical(self, "Error al crear cliente", "Un cliente con el CUIT proporcionado ya existe.")

    def abrir_modificar_cliente(self):
        if self.modificar_cliente_ui is None:
            self.inicializar_modificar_cliente()

        tabla = self.main_ui.tabla_cliente
        row_seleccionada = tabla.currentRow()

        # Si se selecciono una fila, extraigo cada columna
        if row_seleccionada >= 0:
            data = [tabla.item(row_seleccionada, col) for col in range(4)]
            self.cliente_modificado_id = data[0].data(Qt.ItemDataRole.UserRole)

            # Completo los campos de la ventana con los valores en la fila
            self.modificar_cliente_ui.line_nombre_modificarCliente.setText(data[0].text())
            self.modificar_cliente_ui.line_apellido_modificarCliente.setText(data[1].text())
            self.modificar_cliente_ui.line_email_modificarCliente.setText(data[2].text())
            self.modificar_cliente_ui.line_cuil_modificarCliente.setText(data[3].text())

            # Muestro la ventana
            self.modificar_cliente_ui.show()

    def actualizar_cliente(self):
        cliente = Cliente.get(self.cliente_modificado_id)

        cliente.nombre = self.modificar_cliente_ui.line_nombre_modificarCliente.text()
        cliente.apellido = self.modificar_cliente_ui.line_apellido_modificarCliente.text()
        cliente.telefono = self.modificar_cliente_ui.line_email_modificarCliente.text()
        cliente.cuit = int(self.modificar_cliente_ui.line_cuil_modificarCliente.text())
        
        if Cliente.modificar(cliente) == True:
            QMessageBox.information(self, "Éxito", "Se han actualizado los datos del cliente.")
            self.actualizar_tabla_clientes(Cliente.get())
            self.modificar_cliente_ui.hide()
        else:
            QMessageBox.critical(self, "Error", "Ha habido un error al intentar modificar el cliente.")

    def actualizar_tabla_clientes(self, clientes):
        # Tomo la tabla de clientes y elimino todas las filas
        tabla = self.main_ui.tabla_cliente
        tabla.setRowCount(0)

        # Por cada cliente actualizo de una en una las filas de la tabla
        for row, cliente in enumerate(clientes):
            data = [cliente.nombre, cliente.apellido, "-" if cliente.telefono == None else cliente.telefono, cliente.cuit]
            self.setRowData(row, data, tabla, cliente.id)

    def buscar_clientes(self):
        # Tomo todos los clientes, filtro por el texto de la barra de busqueda y actualizo la tabla
        clientes = Cliente.get()
        search_text = self.main_ui.buscar_cliente.text().lower()
        filtered_clients = [cliente for cliente in clientes if search_text in cliente.nombre.lower()]
        self.actualizar_tabla_clientes(filtered_clients)


    def abrir_agregar_transaccion(self):
        comboBox = self.main_ui.combobox_cliente
        comboBox.clear()
        # Rellenar ComboBox
        for cliente in Cliente.get():
            index = self.main_ui.combobox_cliente.count()
            comboBox.addItem(f"{cliente.nombre} {cliente.apellido}")
            comboBox.setItemData(index, cliente.id)

        # Setear campos de fecha a fecha actual
        self.main_ui.dateEdit_cliente1.setDate(QDate.currentDate())
        self.main_ui.dateEdit_cliente2.setDate(QDate.currentDate())

        self.cambiar_pestaña(self.main_ui.page_6agregar_transaccion)

    def agregar_transaccion(self):
        id_cliente = self.main_ui.combobox_cliente.itemData(self.main_ui.combobox_cliente.currentIndex())
        valor_final = self.main_ui.doubleSpinBox_cliente1
        cuotas = self.main_ui.spinBox_2_cliente
        valor_cuota = self.main_ui.doubleSpinBox_cliente2
        aumento = self.main_ui.doubleSpinBox_cliente3
        fecha_boleto = self.main_ui.dateEdit_cliente1
        fecha_primera_cuota = self.main_ui.dateEdit_cliente2

        nueva_transaccion = Transaccion(
            id_cliente, 
            valor_final.value(), 
            cuotas.value(), 
            valor_cuota.value(), 
            aumento.value(),
            fecha_boleto.date().toPyDate(),
            fecha_primera_cuota.date().toPyDate()
            )
        if nueva_transaccion.crear() == True:
            QMessageBox.information(self, "Éxito", "Se ha agregado la transacción exitosamente.")
            self.main_ui.combobox_cliente.setCurrentIndex(0)
            valor_final.setValue(0)
            cuotas.setValue(0)
            valor_cuota.setValue(0)
            aumento.setValue(0)
            fecha_boleto.setDate(QDate.currentDate())
            fecha_primera_cuota.setDate(QDate.currentDate())
        else:
            QMessageBox.critical(self, "Error", "El cliente seleccionado no existe.")

    def abrir_modificar_transaccion(self):
        if self.modificar_transaccion_ui is None:
            self.inicializar_modificar_transaccion()

        tabla = self.main_ui.tabla_transacciones
        row_seleccionada = tabla.currentRow()

        # Si se selecciono una fila, extraigo cada columna
        if row_seleccionada >= 0:
            data = [tabla.item(row_seleccionada, col) for col in range(5)]
            self.transaccion_modificada_id = data[0].data(Qt.ItemDataRole.UserRole)
            transaccion = Transaccion.get(self.transaccion_modificada_id)

            # Relleno el comboBox y selecciono la opcion acorde con el valor de la fila seleccionada
            comboBox = self.modificar_transaccion_ui.comboBox_cliente_modificar_transaccion
            comboBox.clear()

            for cliente in Cliente.get():
                index = comboBox.count()
                comboBox.addItem(f"{cliente.nombre} {cliente.apellido}")
                comboBox.setItemData(index, cliente.id)

            index = comboBox.findText(data[0].text())
            comboBox.setCurrentIndex(index)

            # Completo el resto de los campos con los valores de la fila seleccionada
            self.modificar_transaccion_ui.doubleSpinBox_valor_final_modificar_transaccion.setValue(transaccion.valor_final)
            self.modificar_transaccion_ui.spinBox_cuotas_modificar_transaccion.setValue(transaccion.cuotas)
            self.modificar_transaccion_ui.doubleSpinBox_2_valor_cuota_modificar_transaccion.setValue(transaccion.valor_cuota)
            self.modificar_transaccion_ui.doubleSpinBox_3_aumento_modificar_transaccion.setValue(transaccion.aumento)

            fecha1 = transaccion.fecha_boleto
            fecha2 = transaccion.fecha_primera_cuota
            self.modificar_transaccion_ui.dateEdit_fecha_boleto_modificar_transaccion.setDate(QDate(fecha1.year, fecha1.month, fecha1.day))
            self.modificar_transaccion_ui.dateEdit_fecha_primera_cuota_modificar_transaccion.setDate(QDate(fecha2.year, fecha2.month, fecha2.day))

            self.modificar_transaccion_ui.show()

    def actualizar_transaccion(self):
        transaccion = Transaccion.get(self.transaccion_modificada_id)

        index_comboBox = self.modificar_transaccion_ui.comboBox_cliente_modificar_transaccion.currentIndex()

        transaccion.id_cliente = self.modificar_transaccion_ui.comboBox_cliente_modificar_transaccion.itemData(index_comboBox)
        transaccion.valor_final = self.modificar_transaccion_ui.doubleSpinBox_valor_final_modificar_transaccion.value()
        transaccion.cuotas = self.modificar_transaccion_ui.spinBox_cuotas_modificar_transaccion.value()
        transaccion.valor_cuota = self.modificar_transaccion_ui.doubleSpinBox_2_valor_cuota_modificar_transaccion.value()
        transaccion.aumento = self.modificar_transaccion_ui.doubleSpinBox_3_aumento_modificar_transaccion.value()
        transaccion.fecha_boleto = self.modificar_transaccion_ui.dateEdit_fecha_boleto_modificar_transaccion.date().toPyDate()
        transaccion.fecha_primera_cuota = self.modificar_transaccion_ui.dateEdit_fecha_primera_cuota_modificar_transaccion.date().toPyDate()

        if Transaccion.modificar(transaccion) == True:
            QMessageBox.information(self, "Éxito", "Se han actualizado los datos de la transaccion.")
            self.actualizar_tabla_transacciones(Transaccion.get())
            self.modificar_transaccion_ui.hide()
        else:
            QMessageBox.critical(self, "Error", "Ha habido un error al intentar modificar la transacción.")

    def actualizar_tabla_transacciones(self, transacciones):
        # Tomo la tabla de transacciones y elimino todas las filas
        tabla = self.main_ui.tabla_transacciones
        tabla.setRowCount(0)

        # Por cada transaccion actualizo de una en una las filas de la tabla
        for row, transaccion in enumerate(transacciones):
            cliente = Cliente.get(transaccion.id_cliente)
            nombre_completo = f"{cliente.nombre} {cliente.apellido}"
            data = [nombre_completo, transaccion.valor_final, transaccion.cuotas, transaccion.aumento, transaccion.valor_cuota]

            self.setRowData(row, data, tabla, transaccion.id)
        
    def buscar_transacciones(self):
        # Tomo todas las transacciones, filtro por el texto de la barra de busqueda y actualizo la tabla
        transacciones = Transaccion.get()

        search_text = self.main_ui.buscar_transacciones.text().lower()
        filtered_transactions = []

        for transaccion in transacciones:
            cliente = Cliente.get(transaccion.id_cliente)

            if search_text in cliente.nombre.lower():
                filtered_transactions.append(transaccion)

        self.actualizar_tabla_transacciones(filtered_transactions)


    def abrir_lista_pagos(self):
        # Relleno el comboBox de AÑO
        años = list(set(int(year[0]) for year in Transaccion.get_años_cuotas()))
        años.sort()

        comboBox_mes = self.main_ui.comboBox_mes_lista_pagos
        comboBox_año = self.main_ui.comboBox_anio_lista_pagos
        comboBox_año.clear()

        for año in años:
            comboBox_año.addItem(str(año))

        # Mes y año seleccionados en los comboBox = a los actuales
        mes_actual = datetime.now().month
        año_actual = datetime.now().year
        comboBox_año_index = comboBox_año.findText(str(año_actual))

        comboBox_mes.setCurrentIndex(mes_actual - 1)       
        if comboBox_año_index != -1:
            comboBox_año.setCurrentIndex(comboBox_año_index)

        # Muestro lista de pagos
        self.actualizar_tabla_pagos()

    def actualizar_tabla_pagos(self):
        # Tomo la tabla de pagos y elimino todas las filas
        tabla = self.main_ui.tableWidget
        tabla.setRowCount(0)

        # Filtros
        estado = self.main_ui.comboBox_estado_lista_pagos.currentIndex()
        mes = self.main_ui.comboBox_mes_lista_pagos.currentIndex() + 1
        año = self.main_ui.comboBox_anio_lista_pagos.currentText()

        transacciones = Transaccion.get()

        row_counter = 0

        for transaccion in transacciones:
            cuotas = transaccion.get_cuotas()

            # Por cada cuota actualizo de una en una las filas de la tabla
            for cuota in cuotas:
                estado_cuota = cuota["estado"]
                fecha = cuota["fecha"]

                # Si la cuota coincide con los filtros
                if estado == estado_cuota and mes == fecha.month and int(año) == fecha.year:

                    cliente = Cliente.get(transaccion.id_cliente)
                    nombre_completo = f"{cliente.nombre} {cliente.apellido}"
                    fecha_pago = cuota["fecha_pago"] if cuota["fecha_pago"] != None else "-"

                    data = [nombre_completo, cuota["cuota"], cuota["valor"], fecha_pago]

                    self.setRowData(row_counter, data, tabla, cuota["id"])


            row_counter += tabla.rowCount()

    def modificar_pago(self, estado):
        tabla = self.main_ui.tableWidget
        row_seleccionada = tabla.currentRow()

        if row_seleccionada >= 0:
            item = tabla.item(row_seleccionada, 0)
            id = item.data(Qt.ItemDataRole.UserRole)
            
            modificar_cuota = Transaccion.modificar_estado_cuota(id, estado)

            if modificar_cuota == True:
                QMessageBox.information(self, "Exito", "Se ha modificado el estado de la cuota.")
            else:
                QMessageBox.critical(self, "Error", "Ha ocurrido un error al intentar modificar el estado de la cuota.")

            self.actualizar_tabla_pagos()


    def custom_close_event(self, event):
        self.login_ui.close()
        self.modificar_cliente_ui.close()
        self.modificar_transaccion_ui.close()
        self.bd.con.close()
        event.accept()

    def cambiar_pestaña(self, pestaña):
        self.main_ui.stackedWidget.setCurrentWidget(pestaña)

    def center_window(self, window):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - window.width()) // 2
        y = (screen_geometry.height() - window.height()) // 2
        window.move(x, y)

    def setRowData(self, row, data, table, id):
        # Por cada columna de la tabla actualizo su valor con el correspondiente en data
        table.insertRow(row)
        for col, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            table.setItem(row, col, item)
            item.setData(Qt.ItemDataRole.UserRole, id)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def eliminar_row(self, table, instance_type):
        # Elimino la fila actualmente seleccionada de la tabla y de la BD.
        row_seleccionada = table.currentRow()

        if row_seleccionada >= 0:
            item = table.item(row_seleccionada, 0)

            if item:
                id = item.data(Qt.ItemDataRole.UserRole)
                if instance_type.eliminar(id) == True:
                    table.removeRow(row_seleccionada)
                    QMessageBox.information(self, "Éxito", "El elemento ha sido eliminado correctamente.")
                elif instance_type is Cliente:
                    QMessageBox.critical(self, "Error", "Se produjo un error al intentar eliminar el elemento.\nAsegurese de borrar las transacciones vinculadas con este cliente.")
                else:
                    QMessageBox.critical(self, "Error", "Se produjo un error al intentar eliminar el elemento.")
        else:
            QMessageBox.warning(self, "Error de seleccion", "Si desea eliminar un elemento, primero debe seleccionarlo.")

    def generar_pdf(self):
        tabla = self.main_ui.tabla_transacciones
        row_seleccionada = tabla.currentRow()

        if row_seleccionada >= 0:
            item = tabla.item(row_seleccionada, 0)

            if item:
                id = item.data(Qt.ItemDataRole.UserRole)
                transaccion = Transaccion.get(id)

                generar_pdf(transaccion)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mi_app = VentanaPrincipal()
    sys.exit(app.exec())