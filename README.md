class Reserva(Entidad):
    """Reserva de un servicio realizada por un cliente."""

    ESTADOS = ("Pendiente", "Confirmada", "Cancelada", "Procesada")

    def __init__(self, cliente, servicio, duracion):
        # Verifica que el cliente y el servicio sean objetos válidos
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva debe tener un cliente válido.")

        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva debe tener un servicio válido.")

        # Comprueba que el servicio esté disponible
        if not servicio.disponible:
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible.")

        # Valida la duración y calcula el costo de la reserva
        self._duracion = servicio.validar_parametros(duracion)
        self._costo = servicio.calcular_costo(self._duracion)

        self._cliente = cliente
        self._servicio = servicio
        self._estado = "Pendiente"

        super().__init__("RES")  # Código consecutivo de la reserva
        registro.info("Reserva creada: %s para el cliente %s.",
                      self.id, cliente.id)

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def duracion(self):
        return self._duracion

    @property
    def costo(self):
        return self._costo

    @property
    def estado(self):
        return self._estado

    def confirmar(self):
        # Solo permite confirmar reservas pendientes
        if self._estado != "Pendiente":
            raise OperacionNoPermitidaError(
                "Solo se pueden confirmar reservas pendientes.")

        if not self._servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio ya no está disponible.")

        self._estado = "Confirmada"
        registro.info("Reserva %s confirmada.", self.id)
        return self

    def cancelar(self):
        # No permite cancelar reservas que ya fueron procesadas
        if self._estado not in ("Pendiente", "Confirmada"):
            raise OperacionNoPermitidaError(
                "Solo se pueden cancelar reservas pendientes o confirmadas.")

        self._estado = "Cancelada"
        registro.info("Reserva %s cancelada.", self.id)
        return self

    def procesar(self):
        # Para procesar una reserva primero debe estar confirmada
        if self._estado != "Confirmada":
            raise OperacionNoPermitidaError(
                "Primero se debe confirmar la reserva.")

        self._estado = "Procesada"
        registro.info("Reserva %s procesada.", self.id)
        return self

    def describir(self):
        # Presenta la información principal de la reserva
        return (
            f"Cliente: {self._cliente.nombre} | "
            f"Servicio: {self._servicio.nombre} | "
            f"Duración: {self._duracion:g} {self._servicio.UNIDAD} | "
            f"Costo: {formato_moneda(self._costo)} | "
            f"Estado: {self._estado}"
        )


# -----------------------------------------------------------------------------
# Gestor del sistema: administra clientes, servicios y reservas
# -----------------------------------------------------------------------------
class GestorSistema:
    """Administra los objetos del sistema mediante listas en memoria."""

    def __init__(self):
        # Listas que almacenan los registros durante la ejecución
        self._clientes = []
        self._servicios = []
        self._reservas = []

    @property
    def clientes(self):
        return tuple(self._clientes)

    @property
    def servicios(self):
        return tuple(self._servicios)

    @property
    def reservas(self):
        return tuple(self._reservas)

    def registrar_cliente(self, cliente):
        # Verifica el tipo de objeto antes de registrarlo
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe registrar un objeto Cliente.")

        # Evita registrar dos clientes con el mismo documento
        if any(c.documento == cliente.documento for c in self._clientes):
            raise DatoInvalidoError(
                f"Ya existe un cliente con documento {cliente.documento}.")

        self._clientes.append(cliente)
        registro.info("Cliente registrado: %s.", cliente.id)
        return cliente

    def registrar_servicio(self, servicio):
        # Comprueba que el objeto pertenezca a la clase Servicio
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe registrar un servicio válido.")

        if any(s.id == servicio.id for s in self._servicios):
            raise DatoInvalidoError("El servicio ya está registrado.")

        self._servicios.append(servicio)
        registro.info("Servicio registrado: %s.", servicio.id)
        return servicio

    def buscar_cliente(self, identificador):
        # Permite buscar al cliente por código o documento
        texto = texto_obligatorio(identificador, "identificador del cliente")

        for cliente in self._clientes:
            if cliente.id == texto or cliente.documento == texto:
                return cliente

        raise DatoInvalidoError(
            f"No se encontró el cliente '{texto}'.")

    def buscar_servicio(self, identificador):
        # Busca un servicio por su código o nombre
        texto = texto_obligatorio(identificador, "identificador del servicio")

        for servicio in self._servicios:
            if (servicio.id == texto or
                    normalizar(servicio.nombre) == normalizar(texto)):
                return servicio

        raise ServicioNoDisponibleError(
            f"No se encontró el servicio '{texto}'.")

    def buscar_reserva(self, identificador):
        # Localiza una reserva mediante su código
        texto = texto_obligatorio(identificador, "identificador de la reserva")

        for reserva in self._reservas:
            if reserva.id == texto:
                return reserva

        raise ReservaInvalidaError(
            f"No se encontró la reserva '{texto}'.")

    def crear_reserva(self, cliente, servicio, duracion):
        # Obtiene los objetos registrados en el sistema
        cliente_obj = (cliente if isinstance(cliente, Cliente)
                       else self.buscar_cliente(cliente))

        servicio_obj = (servicio if isinstance(servicio, Servicio)
                        else self.buscar_servicio(servicio))

        if cliente_obj not in self._clientes:
            raise DatoInvalidoError(
                "El cliente debe estar registrado en el sistema.")

        if servicio_obj not in self._servicios:
            raise ServicioNoDisponibleError(
                "El servicio debe estar registrado en el sistema.")

        # Crea y almacena la nueva reserva
        reserva = Reserva(cliente_obj, servicio_obj, duracion)
        self._reservas.append(reserva)
        return reserva

    def confirmar_reserva(self, identificador):
        # Busca la reserva y ejecuta su confirmación
        return self.buscar_reserva(identificador).confirmar()

    def cancelar_reserva(self, identificador):
        # Busca la reserva y ejecuta su cancelación
        return self.buscar_reserva(identificador).cancelar()

    def procesar_reserva(self, identificador):
        # Busca la reserva y ejecuta su procesamiento
        return self.buscar_reserva(identificador).procesar()

    def listar_reservas(self):
        # Devuelve todas las reservas registradas
        if not self._reservas:
            return "No hay reservas registradas."

        return "\n".join(str(reserva) for reserva in self._reservas)


# -----------------------------------------------------------------------------
# Simulación de operaciones correctas e incorrectas
# -----------------------------------------------------------------------------
def simular_operaciones():
    # Se crea el gestor principal del sistema
    gestor = GestorSistema()
    reserva_prueba = [None]

    def ejecutar(descripcion, operacion):
        # Ejecuta cada operación y controla los posibles errores
        print(f"\n{descripcion}")

        try:
            resultado = operacion()

        except ErrorSistemaFJ as error:
            print(f"ERROR CONTROLADO: {error}")
            registrar_error(error, descripcion)

        except Exception as error:
            print(f"ERROR INESPERADO: {error}")
            registrar_error(error, descripcion)

        else:
            if resultado is not None:
                print(resultado)
            else:
                print("Operación realizada correctamente.")

        finally:
            registro.info("Finalizó la operación de prueba: %s.",
                          descripcion)

    print("\n========== SIMULACIÓN DEL SISTEMA SOFTWARE FJ ==========")

    # 1. Registro de un cliente válido
    ejecutar(
        "1. Registrar un cliente",
        lambda: gestor.registrar_cliente(
            Cliente("12345678", "Laura Pineda",
                    "laura@email.com", "3001234567")
        )
    )

    # 2. Intento de registro con documento repetido
    ejecutar(
        "2. Intentar registrar un cliente con documento repetido",
        lambda: gestor.registrar_cliente(
            Cliente("12345678", "Carlos Perez",
                    "carlos@email.com", "3101234567")
        )
    )

    # 3. Registro de una sala
    ejecutar(
        "3. Registrar una sala",
        lambda: gestor.registrar_servicio(
            ReservaSala("Sala principal", 50000, 30)
        )
    )

    # 4. Registro de alquiler de equipos
    ejecutar(
        "4. Registrar alquiler de equipos",
        lambda: gestor.registrar_servicio(
            AlquilerEquipo("Computadores", 20000, 3)
        )
    )

    # 5. Registro de una asesoría especializada
    ejecutar(
        "5. Registrar una asesoría especializada",
        lambda: gestor.registrar_servicio(
            AsesoriaEspecializada(
                "Asesoria de redes", 80000, "redes", "avanzado")
        )
    )

    # 6. Creación de una reserva válida
    ejecutar(
        "6. Crear una reserva válida",
        lambda: reserva_prueba.__setitem__(
            0, gestor.crear_reserva(
                "12345678", "Sala principal", 2)
        )
    )

    # 7. Confirmación de la reserva
    ejecutar(
        "7. Confirmar la reserva",
        lambda: gestor.confirmar_reserva(reserva_prueba[0].id)
    )

    # 8. Procesamiento de la reserva confirmada
    ejecutar(
        "8. Procesar la reserva confirmada",
        lambda: gestor.procesar_reserva(reserva_prueba[0].id)
    )

    # 9. Intento de cancelar una reserva procesada
    ejecutar(
        "9. Intentar cancelar una reserva procesada",
        lambda: gestor.cancelar_reserva(reserva_prueba[0].id)
    )

    # 10. Intento de reserva con duración no permitida
    ejecutar(
        "10. Intentar crear una reserva con duración no permitida",
        lambda: gestor.crear_reserva(
            "12345678", "Sala principal", 12)
    )

    # 11. Cambio de disponibilidad de un servicio
    ejecutar(
        "11. Marcar un servicio como no disponible",
        lambda: setattr(
            gestor.buscar_servicio("Computadores"),
            "disponible", False)
    )

    # 12. Intento de reservar un servicio no disponible
    ejecutar(
        "12. Intentar reservar un servicio no disponible",
        lambda: gestor.crear_reserva(
            "12345678", "Computadores", 1)
    )

    # 13. Consulta de las reservas registradas
    ejecutar(
        "13. Consultar las reservas registradas",
        gestor.listar_reservas
    )

    print("\n========== FIN DE LA SIMULACIÓN ==========")
    print("Consulte el archivo registro_eventos.log para ver los eventos y errores.")
