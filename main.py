from PyQt6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt6.uic.load_ui import loadUi
from modelos.usuario import Usuario
from modelos.cliente import Cliente
from modelos.transaccion import Transaccion
from utils.pdf_generador import generar_pdf

import sys
import os

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super(VentanaPrincipal, self).__init__()

        # Instancias
        self.login_ui = loadUi(os.path.join("Front", "Login", "loginUI3.ui"))
        self.main_ui = loadUi(os.path.join("Front", "Proyecto_Inmobiliaria.ui"))
        self.main_ui.stackedWidget.setCurrentWidget(self.main_ui.page_1gestion_clientes)

        
        # Muestro login al iniciar app
        self.login_ui.show()

        # Login buttons
        self.login_ui.bt_login_inicio.clicked.connect(self.login)

        # Main UI menu lateral buttons
        self.main_ui.bt_registrar_menulateral.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_1gestion_clientes))
        self.main_ui.bt_transacciones_menulateral.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_5gestion_transacciones))
        self.main_ui.bt_pagos_menulateral.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_9gestion_pagos))
        self.main_ui.bt_salir_menulateral.clicked.connect(lambda: sys.exit())

        # Clientes Buttons
        self.main_ui.bt_gestionar_cliente.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_2registrar_cliente))
        self.main_ui.bt_modificar_cliente.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_3modificar_cliente))

        self.main_ui.bt_listar_cliente.clicked.connect(lambda: (
            self.cambiar_pestaña(self.main_ui.page_4eliminar_cliente), 
            self.actualizar_tabla_clientes(Cliente.get())
            ))

        # Listado de clientes
        self.main_ui.bt_eliminar_cliente_2.clicked.connect(lambda: self.eliminar_row(self.main_ui.tabla_borrar, Cliente))
        self.main_ui.bt_volver_menu.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_1gestion_clientes))
        self.main_ui.buscar_cliente.textChanged.connect(self.buscar_clientes)

        # Agregar cliente
        self.main_ui.bt_Aceptar_Cliente.clicked.connect(self.agregar_cliente)
        self.main_ui.bt_volver_cliente.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_1gestion_clientes))


        # Main UI Transacciones Buttons
        self.main_ui.bt_agregar_Transaccion.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_6agregar_transaccion))
        self.main_ui.bt_modificar_Transaccion.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_7modificar_transaccion))
        self.main_ui.bt_listar_Transaccion.clicked.connect(lambda: (
            self.cambiar_pestaña(self.main_ui.page_8lista_transacciones),
            self.actualizar_tabla_transacciones(Transaccion.get())
            ))
        
        # Listado de transacciones
        self.main_ui.lineEdit_41.textChanged.connect(self.buscar_transacciones)
        self.main_ui.bt_eliminar_transaccion.clicked.connect(lambda: self.eliminar_row(self.main_ui.tabla_clientes, Transaccion))
        self.main_ui.bt_Volver_Menu.clicked.connect(lambda: self.cambiar_pestaña(self.main_ui.page_5gestion_transacciones))
        self.main_ui.bt_pdf_transaccion.clicked.connect(self.generar_pdf)

        # Agregar transacciones
        for cliente in Cliente.get():
            self.main_ui.combobox_cliente.addItem(f"{cliente.nombre} {cliente.apellido}")

    def generar_pdf(self):
        tabla = self.main_ui.tabla_clientes
        row_seleccionada = tabla.currentRow()

        if row_seleccionada >= 0:
            item = tabla.item(row_seleccionada, 0)

            if item:
                id = int(item.text())
                transaccion = Transaccion.get(id)

                generar_pdf(transaccion)

    def setRowData(self, row, data, table):
        # Por cada columna de la tabla actualizo su valor con el correspondiente en data
        table.insertRow(row)
        for col, value in enumerate(data):
            table.setItem(row, col, QTableWidgetItem(str(value)))

    def eliminar_row(self, table, instance_type):
        # Elimino la fila actualmente seleccionada de la tabla y de la BD.
        row_seleccionada = table.currentRow()

        if row_seleccionada >= 0:
            item = table.item(row_seleccionada, 0)

            if item:
                id = int(item.text())
                instance_type.eliminar(id)
                table.removeRow(row_seleccionada)

    def login(self):
        # Inicio sesión
        contraseña = self.login_ui.line_contrasea_login.text()
        nombre = self.login_ui.line_usuario_login.text()

        usuario = Usuario.login(nombre, contraseña)

        if usuario != None:
            print("Se ha iniciado sesion!")
            self.login_ui.hide()
            self.main_ui.show()
        else:
            print("Usuario y/o contraseña incorrectos")

    def cambiar_pestaña(self, pestaña):
        self.main_ui.stackedWidget.setCurrentWidget(pestaña)

    def buscar_clientes(self):
        # Tomo todos los clientes, filtro por el texto de la barra de busqueda y actualizo la tabla
        clientes = Cliente.get()
        search_text = self.main_ui.buscar_cliente.text().lower()
        filtered_clients = [cliente for cliente in clientes if search_text in cliente.nombre.lower()]
        self.actualizar_tabla_clientes(filtered_clients)

    def actualizar_tabla_clientes(self, clientes):
        # Tomo la tabla de clientes y elimino todas las filas
        tabla = self.main_ui.tabla_cliente
        tabla.setRowCount(0)

        # Por cada cliente actualizo de una en una las filas de la tabla
        for row, cliente in enumerate(clientes):
            data = [cliente.nombre, cliente.apellido, "-" if cliente.telefono is None else cliente.telefono, cliente.cuit]
            self.setRowData(row, data, tabla)

    def agregar_cliente(self):
        nombre = self.main_ui.line_nombre_registro_cliente
        apellido = self.main_ui.line_apellido_registro_cliente
        telefono = self.main_ui.lineEdit
        cuit = self.main_ui.spinBox

        nuevo_cliente = Cliente(nombre.text(), apellido.text(), cuit.value(), telefono.text() if telefono.text() != "" else None)

        if nuevo_cliente.crear() is True:
            print("Se ha agregado el cliente existosamente!")
            nombre.clear()
            apellido.clear()
            telefono.clear()
            cuit.setValue(0)
        else:
            print("Ha habido un error")
        
    def actualizar_tabla_transacciones(self, transacciones):
        # Tomo la tabla de transacciones y elimino todas las filas
        tabla = self.main_ui.tabla_clientes
        tabla.setRowCount(0)

        # Por cada transaccion actualizo de una en una las filas de la tabla
        for row, transaccion in enumerate(transacciones):
            cliente = Cliente.get(transaccion.id_cliente)
            data = [transaccion.id, cliente.nombre, transaccion.valor_final, transaccion.cuotas, transaccion.valor_cuota]

            self.setRowData(row, data, tabla)
        
    def buscar_transacciones(self):
        # Tomo todas las transacciones, filtro por el texto de la barra de busqueda y actualizo la tabla
        transacciones = Transaccion.get()

        search_text = self.main_ui.lineEdit_41.text().lower()
        filtered_transactions = []

        for transaccion in transacciones:
            cliente = Cliente.get(transaccion.id_cliente)

            if search_text in cliente.nombre.lower():
                filtered_transactions.append(transaccion)

        self.actualizar_tabla_transacciones(filtered_transactions)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mi_app = VentanaPrincipal()
    sys.exit(app.exec())
