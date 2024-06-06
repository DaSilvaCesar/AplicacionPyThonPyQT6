import sqlite3

class BD:
    _instance = None

    # Este metodo sirve para aplicar patron Singleton a la clase
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BD, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        if not hasattr(self, 'initialized'): # Checkea para evitar re-inicializar
            # Conexión y creación de BD
            self.con = sqlite3.connect("database.db")
            self.cur = self.con.cursor()

            # Configuro la BD que me devuelva diccionarios en vez de listas
            self.con.row_factory = sqlite3.Row

            self.initialized = True

    def crear_tablas(self):
        # Creación de las tablas
        self.usuario()
        self.cliente()
        self.lote()
        self.transaccion()
        self.pago_cuotas()
        self.con.commit()

    def usuario(self):
        # Tabla usuario
        sql = """
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """
        self.cur.execute(sql)

    def cliente(self):
        # Tabla cliente
        sql = """
            CREATE TABLE IF NOT EXISTS cliente (
                id INTEGER PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                apellido VARCHAR(50) NOT NULL,
                telefono VARCHAR(25),
                cuit INT UNIQUE NOT NULL
            )
        """
        self.cur.execute(sql)

    def transaccion(self):
        # Tabla transaccion. 
        # Campos de fecha tienen el tipo %d-%m-%Y
        sql = """
            CREATE TABLE IF NOT EXISTS transaccion (
                id INTEGER PRIMARY KEY,
                id_cliente INTEGER NOT NULL,
                valor_final REAL NOT NULL,
                cuotas INT NOT NULL,
                valor_cuota REAL NOT NULL,
                aumento REAL NOT NULL DEFAULT 0.0,
                fecha_boleto TEXT NOT NULL,
                fecha_primera_cuota TEXT NOT NULL,
                id_lote INT NOT NULL,
                FOREIGN KEY (id_cliente) REFERENCES cliente (id),
                FOREIGN KEY (id_lote) REFERENCES lote (id)
            )
        """
        
        self.cur.execute(sql)

    def pago_cuotas(self):
        sql = """
            CREATE TABLE IF NOT EXISTS pago_cuotas (
                id INTEGER PRIMARY KEY,
                id_transaccion INTEGER NOT NULL,
                cuota INT NOT NULL,
                estado INT NOT NULL DEFAULT 0,
                fecha TEXT NOT NULL,
                FOREIGN KEY (id_transaccion) REFERENCES transaccion (id)
            )
        """
        self.cur.execute(sql)

    def lote(self):
        sql = """
            CREATE TABLE IF NOT EXISTS lote (
                id INTEGER PRIMARY KEY,
                circunscripcion INT,
                seccion VARCHAR(10),
                manzana INT,
                parcela VARCHAR(20)
            )
        """
        self.cur.execute(sql)
    
if __name__ == "__main__":
    bd = BD()
    bd.crear_tablas()