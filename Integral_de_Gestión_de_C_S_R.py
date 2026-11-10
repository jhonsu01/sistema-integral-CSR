# -*- coding: utf-8 -*-
"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ.

Curso: Programación (213023) - Grupo 213023_638 - UNAD.
Actividad: Fase 4 - Componente práctico - Prácticas simuladas.

Software FJ ofrece reserva de salas, alquiler de equipos y asesorías
especializadas. El programa gestiona clientes, servicios y reservas solo con
objetos y listas en memoria (no usa bases de datos). El único archivo que
escribe es el registro de eventos y errores: registro_eventos.log.

Ejecución:  python Integral_de_Gestión_de_C_S_R.py
"""
# =============================================================================
# SECCIÓN 1: CONFIGURACIÓN, REGISTRO DE EVENTOS, EXCEPCIONES Y CLASE ENTIDAD
# Aporte de: Jhon Jaiver Supelano Rojas (rama main)
# =============================================================================

import os                                   # Ruta del archivo de logs
import re                                   # Expresión regular para validar correos
import logging                              # Registro de eventos y errores en un archivo
from abc import ABC, abstractmethod         # Clases y métodos abstractos
from datetime import datetime               # Fecha de creación de cada entidad
from typing import overload                 # Declaración de las variantes de un método
import tkinter as tk                        # Ventana principal y variables de la interfaz
from tkinter import ttk                     # Controles: pestañas, tablas, listas y botones
from tkinter import messagebox              # Cuadros de diálogo de éxito y de error

# El archivo de logs se guarda en la misma carpeta del programa
RUTA_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "registro_eventos.log")


def configurar_registro(ruta=RUTA_LOG):
    """Configura el registrador de eventos del sistema y lo devuelve."""
    logging.addLevelName(logging.WARNING, "AVISO")       # Nombres de nivel en español
    logging.addLevelName(logging.CRITICAL, "CRÍTICO")
    registrador = logging.getLogger("SoftwareFJ")        # Registrador propio del programa
    registrador.setLevel(logging.INFO)                   # Guarda eventos informativos y errores
    registrador.propagate = False                        # Evita repetir los mensajes en consola
    if registrador.handlers:                             # Si ya estaba configurado no se repite
        return registrador
    # Formato de cada línea: fecha y hora | nivel | mensaje
    formato = logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s",
                                "%Y-%m-%d %H:%M:%S")
    try:
        manejador = logging.FileHandler(ruta, encoding="utf-8")    # Abre o crea el archivo
    except OSError as error:
        # Sin permiso para escribir: los eventos van a la consola y el programa continúa
        manejador = logging.StreamHandler()
        manejador.setFormatter(formato)
        registrador.addHandler(manejador)
        registrador.warning("No se pudo abrir el archivo de logs (%s); se usa la consola.", error)
    else:
        # else: solo se ejecuta cuando el archivo se abrió sin errores
        manejador.setFormatter(formato)
        registrador.addHandler(manejador)
    return registrador


registro = configurar_registro()            # Registrador compartido por todas las secciones


def registrar_error(error, operacion):
    """Escribe un error en el log junto con la excepción que lo originó, si existe."""
    mensaje = f"{operacion} -> {type(error).__name__}: {error}"    # Operación, tipo y mensaje
    causa = error.__cause__                 # Excepción original guardada con "raise ... from"
    if causa is not None:
        mensaje += f" | Causa: {type(causa).__name__}: {causa}"    # Se agrega la causa encadenada
    registro.error(mensaje)                 # Nivel ERROR en el archivo de logs


def leer_registro(ruta=RUTA_LOG):
    """Devuelve el contenido del archivo de logs (usa try/finally para cerrarlo siempre)."""
    archivo = None                          # Aún no hay archivo abierto
    try:
        archivo = open(ruta, encoding="utf-8")
        return archivo.read()               # Devuelve todo el texto del registro
    except FileNotFoundError:
        return "Todavía no hay eventos registrados."
    except OSError as error:
        return f"No se pudo leer el archivo de logs: {error}"
    finally:
        if archivo is not None:
            archivo.close()                 # El archivo se cierra aunque ocurra un error

# -----------------------------------------------------------------------------
# Excepciones personalizadas: todas heredan de ErrorSistemaFJ
# -----------------------------------------------------------------------------
class ErrorSistemaFJ(Exception):
    """Excepción base de todos los errores controlados del sistema."""

    titulo = "Error del sistema"            # Título del cuadro de diálogo en la interfaz


class DatoInvalidoError(ErrorSistemaFJ):
    """Un dato tiene un formato o un valor que no está permitido."""

    titulo = "Dato inválido"                # Ejemplo: correo sin @ o tarifa negativa


class ParametroFaltanteError(ErrorSistemaFJ):
    """Falta un dato obligatorio."""

    titulo = "Parámetro faltante"           # Ejemplo: nombre vacío


class OperacionNoPermitidaError(ErrorSistemaFJ):
    """La operación no se puede realizar en el estado actual."""

    titulo = "Operación no permitida"       # Ejemplo: cancelar una reserva ya procesada


class ReservaInvalidaError(ErrorSistemaFJ):
    """El intento de reserva no cumple las reglas del sistema."""

    titulo = "Reserva inválida"             # Ejemplo: duración mayor a la permitida


class ServicioNoDisponibleError(ErrorSistemaFJ):
    """El servicio no existe en el catálogo o está marcado como no disponible."""

    titulo = "Servicio no disponible"       # Ejemplo: reservar un equipo deshabilitado


class CalculoInconsistenteError(ErrorSistemaFJ):
    """Un cálculo de costos recibe o produce valores sin sentido."""

    titulo = "Cálculo inconsistente"        # Ejemplo: descuento del 150 %



# -----------------------------------------------------------------------------
# Clase abstracta que representa cualquier entidad general del sistema
# -----------------------------------------------------------------------------
class Entidad(ABC):
    """Entidad general: tiene un código único, una fecha de creación y sabe describirse."""

    _contadores = {}                        # Consecutivo por tipo de entidad: CLI, SER, RES

    def __init__(self, prefijo):
        # Las clases hijas llaman a este constructor al final, cuando sus datos ya son
        # válidos; así solo los objetos correctos consumen un código consecutivo.
        consecutivo = Entidad._contadores.get(prefijo, 0) + 1     # Siguiente número del tipo
        Entidad._contadores[prefijo] = consecutivo
        self._id = f"{prefijo}-{consecutivo:03d}"           # Ejemplo: CLI-001
        self._fecha_creacion = datetime.now()               # Momento en que se creó

    @property
    def id(self):
        """Código único de la entidad (solo lectura)."""
        return self._id

    @property
    def fecha_creacion(self):
        """Fecha y hora en que se creó la entidad (solo lectura)."""
        return self._fecha_creacion

    @abstractmethod
    def describir(self):
        """Cada entidad concreta debe describirse con sus propios datos."""

    def __str__(self):
        # Texto común a todas las entidades: código y descripción propia (polimorfismo)
        return f"{self._id} - {self.describir()}"


# =============================================================================
# SECCIÓN 2: FUNCIONES DE VALIDACIÓN Y CLASE CLIENTE
# Aporte de: Johan Ricardo Reina Florindo (rama Johan)
# =============================================================================

SIN_TILDES = str.maketrans("áéíóúüÁÉÍÓÚÜ", "aeiouuAEIOUU")    # Tabla para borrar tildes


def normalizar(texto):
    """Pasa un texto a minúsculas, sin tildes ni espacios repetidos (para comparar)."""
    return " ".join(str(texto).split()).lower().translate(SIN_TILDES)


def texto_obligatorio(valor, campo):
    """Verifica que un dato obligatorio no esté vacío y lo devuelve sin espacios sobrantes."""
    if valor is None or str(valor).strip() == "":                 # Vacío o solo espacios
        raise ParametroFaltanteError(f"El campo '{campo}' es obligatorio.")
    return " ".join(str(valor).split())     # Quita espacios al inicio, al final y repetidos


def convertir_numero(valor, campo, tipo=float, minimo=None, maximo=None):
    """Convierte un dato a número (float o int) y verifica sus límites."""
    texto = texto_obligatorio(valor, campo)                     # Primero: que no esté vacío
    try:
        numero = tipo(texto)                                    # int("12") o float("2.5")
    except ValueError as error:
        clase = "un número entero" if tipo is int else "un número (use punto decimal)"
        # Encadenamiento: el ValueError original queda guardado como causa del error propio
        raise DatoInvalidoError(
            f"El campo '{campo}' debe ser {clase}; se recibió '{texto}'.") from error
    if numero != numero or numero in (float("inf"), float("-inf")):    # NaN o infinito
        raise DatoInvalidoError(f"El campo '{campo}' debe ser un número finito.")
    if minimo is not None and numero < minimo:                  # Límite inferior
        raise DatoInvalidoError(f"El campo '{campo}' debe ser mayor o igual a {minimo:g}.")
    if maximo is not None and numero > maximo:                  # Límite superior
        raise DatoInvalidoError(f"El campo '{campo}' debe ser menor o igual a {maximo:g}.")
    return numero


def formato_moneda(valor):
    """Muestra un valor en pesos colombianos: 1234567.5 -> $ 1.234.567,50."""
    texto = f"{valor:,.2f}"                 # 1,234,567.50 (formato inglés)
    # " " es un espacio que no se parte: el signo $ nunca queda separado del valor
    return "$ " + texto.replace(",", "#").replace(".", ",").replace("#", ".")


class Cliente(Entidad):
    """Cliente de Software FJ con sus datos personales privados y validados."""

    PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")     # usuario@dominio.ext

    def __init__(self, documento, nombre, correo, telefono):
        self.__documento = self.validar_documento(documento)   # Atributo privado
        self.nombre = nombre            # Cada asignación pasa por su setter, que valida
        self.correo = correo
        self.telefono = telefono
        super().__init__("CLI")         # El código se asigna solo si todo fue válido

    @staticmethod
    def validar_documento(documento):
        """El documento es obligatorio, solo con dígitos y de 6 a 10 cifras."""
        texto = texto_obligatorio(documento, "documento")
        if not (texto.isascii() and texto.isdigit()):          # Solo dígitos del 0 al 9
            raise DatoInvalidoError(
                "El documento solo puede contener números, sin puntos ni espacios.")
        if not 6 <= len(texto) <= 10:                          # Longitud permitida
            raise DatoInvalidoError("El documento debe tener entre 6 y 10 dígitos.")
        return texto

    @property
    def documento(self):
        """Documento de identidad: es de solo lectura porque no tiene setter."""
        return self.__documento

    @property
    def nombre(self):
        """Nombre completo del cliente."""
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        texto = texto_obligatorio(valor, "nombre")
        if len(texto) < 3:                                      # Nombre demasiado corto
            raise DatoInvalidoError("El nombre debe tener al menos 3 letras.")
        if not all(letra.isalpha() or letra == " " for letra in texto):    # Solo letras
            raise DatoInvalidoError("El nombre solo puede contener letras y espacios.")
        self.__nombre = texto                                   # Se guarda solo si es válido

    @property
    def correo(self):
        """Correo electrónico del cliente (siempre en minúsculas)."""
        return self.__correo

    @correo.setter
    def correo(self, valor):
        texto = texto_obligatorio(valor, "correo").lower()
        if not Cliente.PATRON_CORREO.match(texto):              # Compara con el patrón
            raise DatoInvalidoError(
                f"El correo '{texto}' no tiene un formato válido (ejemplo: usuario@dominio.com).")
        self.__correo = texto

    @property
    def telefono(self):
        """Teléfono de contacto del cliente."""
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        texto = texto_obligatorio(valor, "teléfono")
        # Debe tener solo dígitos y entre 7 (fijo) y 10 (celular) cifras
        if not (texto.isascii() and texto.isdigit()) or not 7 <= len(texto) <= 10:
            raise DatoInvalidoError(
                "El teléfono debe tener entre 7 y 10 dígitos, sin espacios ni símbolos.")
        self.__telefono = texto

    def documento_protegido(self):
        """Muestra solo los 4 últimos dígitos del documento para proteger el dato personal."""
        return "*" * (len(self.__documento) - 4) + self.__documento[-4:]

    def describir(self):
        # Sobrescribe el método abstracto de Entidad con los datos propios del cliente
        return (f"{self.__nombre} | doc. {self.documento_protegido()} | "
                f"{self.__correo} | tel. {self.__telefono}")



# =============================================================================
# SECCIÓN 3: CLASE ABSTRACTA SERVICIO Y SERVICIOS ESPECIALIZADOS
# Aporte de: Mauro Daniel Rodríguez Pinzón (rama Mauro)
# =============================================================================

class Servicio(Entidad):
    """Clase abstracta para todos los servicios que ofrece Software FJ."""

    TIPO = "Servicio"                   # Nombre del tipo (cada clase hija lo redefine)
    UNIDAD = "horas"                    # Unidad en que se mide la duración de una reserva
    DURACION_MAXIMA = 1                 # Duración máxima de una reserva
    ETIQUETAS = ("Dato propio", None)   # Nombres de los datos propios (los usa la interfaz)
    TARIFA_MINIMA = 1000                # Ninguna tarifa puede ser menor a $ 1.000

    def __init__(self, nombre, tarifa):
        nombre = texto_obligatorio(nombre, "nombre del servicio")
        if len(nombre) < 3:                                     # Nombre demasiado corto
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        self._nombre = nombre
        self._tarifa = convertir_numero(tarifa, "tarifa", float, minimo=self.TARIFA_MINIMA)
        self._disponible = True                 # Todo servicio nuevo queda disponible
        super().__init__("SER")                 # Código consecutivo: SER-001, SER-002...

    @property
    def nombre(self):
        """Nombre del servicio (solo lectura)."""
        return self._nombre

    @property
    def tarifa(self):
        """Valor que se cobra por hora o por día (solo lectura)."""
        return self._tarifa

    @property
    def disponible(self):
        """Indica si el servicio se puede reservar."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        if not isinstance(valor, bool):                         # Solo True o False
            raise DatoInvalidoError("La disponibilidad solo puede ser verdadera o falsa.")
        self._disponible = valor

    # ----- Métodos abstractos: cada servicio los sobrescribe (polimorfismo) -----
    @classmethod
    @abstractmethod
    def crear(cls, nombre, tarifa, dato1=None, dato2=None):
        """Construye el servicio a partir de los datos genéricos del formulario."""

    @abstractmethod
    def validar_parametros(self, duracion):
        """Verifica la duración pedida según las reglas del servicio y la devuelve."""

    @abstractmethod
    def calcular_costo_base(self, duracion):
        """Costo sin descuento ni impuesto para una duración ya validada."""

    @classmethod
    def ayuda(cls):
        """Reglas del servicio en texto; se arma con las constantes de la clase."""
        return f"Duración permitida: de 1 a {cls.DURACION_MAXIMA} {cls.UNIDAD}."

    # ----- Método sobrecargado: tres variantes del cálculo de costos -----
    # Python no admite dos métodos con el mismo nombre; la sobrecarga se declara
    # con @overload y se implementa con parámetros opcionales.
    @overload
    def calcular_costo(self, duracion):
        ...                                     # Variante 1: solo el costo base

    @overload
    def calcular_costo(self, duracion, impuesto):
        ...                                     # Variante 2: costo base más impuesto

    @overload
    def calcular_costo(self, duracion, impuesto, descuento):
        ...                                     # Variante 3: con descuento y con impuesto

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        """Calcula el costo total; impuesto y descuento son porcentajes de 0 a 100."""
        cantidad = self.validar_parametros(duracion)        # Regla propia de cada servicio
        impuesto = self._porcentaje(impuesto, "impuesto")
        descuento = self._porcentaje(descuento, "descuento")
        subtotal = self.calcular_costo_base(cantidad)       # Fórmula propia de cada servicio
        subtotal -= subtotal * descuento / 100              # Primero se aplica el descuento
        total = subtotal + subtotal * impuesto / 100        # Después se suma el impuesto
        if total <= 0:                                      # Un total en cero no tiene sentido
            raise CalculoInconsistenteError(
                f"El costo total debe ser mayor que cero; se obtuvo {formato_moneda(total)}.")
        return round(total, 2)                              # Valor con dos decimales

    @staticmethod
    def _porcentaje(valor, campo):
        """Convierte un porcentaje y verifica que esté entre 0 y 100."""
        porcentaje = convertir_numero(valor, campo, float)
        if not 0 <= porcentaje <= 100:                      # Fuera de rango: cálculo inválido
            raise CalculoInconsistenteError(
                f"El {campo} debe estar entre 0 % y 100 %; se recibió {porcentaje:g} %.")
        return porcentaje

    def __str__(self):
        """Sobrescribe __str__ para agregar si el servicio está disponible."""
        estado = "disponible" if self._disponible else "no disponible"
        return f"{super().__str__()} ({estado})"           # Reutiliza el texto de Entidad


class ReservaSala(Servicio):
    """Reserva de salas: se cobra por hora."""

    TIPO = "Reserva de sala"
    UNIDAD = "horas"
    DURACION_MAXIMA = 8                     # Una sala se reserva máximo una jornada
    CAPACIDAD_MAXIMA = 100                  # Personas que caben como máximo
    ETIQUETAS = ("Capacidad (personas)", None)

    def __init__(self, nombre, tarifa_hora, capacidad):
        # Dato propio de la sala: capacidad entera entre 1 y 100 personas
        self._capacidad = convertir_numero(capacidad, "capacidad", int,
                                           1, self.CAPACIDAD_MAXIMA)
        super().__init__(nombre, tarifa_hora)   # Valida nombre y tarifa en la clase padre

    @classmethod
    def crear(cls, nombre, tarifa, dato1=None, dato2=None):
        return cls(nombre, tarifa, dato1)       # dato1 = capacidad

    @property
    def capacidad(self):
        """Número de personas que caben en la sala."""
        return self._capacidad

    @classmethod
    def ayuda(cls):
        # Sobrescribe la ayuda general con las reglas propias de las salas
        return (f"La sala se cobra por hora y se reserva de 1 a {cls.DURACION_MAXIMA} horas. "
                f"Capacidad: de 1 a {cls.CAPACIDAD_MAXIMA} personas.")

    def validar_parametros(self, duracion):
        horas = convertir_numero(duracion, "duración", float)     # Admite fracciones: 1.5
        if not 1 <= horas <= self.DURACION_MAXIMA:                # Máximo una jornada
            raise DatoInvalidoError(f"Una sala se reserva entre 1 y {self.DURACION_MAXIMA} "
                                    f"horas; se pidieron {horas:g}.")
        return horas

    def calcular_costo_base(self, duracion):
        return self.tarifa * duracion           # Tarifa por hora x horas

    def describir(self):
        # Descripción propia de la sala (sobrescribe describir)
        return (f"{self.nombre}: sala para {self._capacidad} personas, "
                f"{formato_moneda(self.tarifa)} por hora")


class AlquilerEquipo(Servicio):
    """Alquiler de equipos: se cobra por día y por equipo, más un seguro."""

    TIPO = "Alquiler de equipo"
    UNIDAD = "días"
    DURACION_MAXIMA = 30                    # Máximo un mes de alquiler
    CANTIDAD_MAXIMA = 20                    # Equipos que se pueden alquilar a la vez
    SEGURO = 0.05                           # 5 % de seguro sobre el valor del alquiler
    ETIQUETAS = ("Cantidad de equipos", None)

    def __init__(self, nombre, tarifa_dia, cantidad):
        # Dato propio del alquiler: cantidad entera de equipos entre 1 y 20
        self._cantidad = convertir_numero(cantidad, "cantidad de equipos", int,
                                          1, self.CANTIDAD_MAXIMA)
        super().__init__(nombre, tarifa_dia)    # Valida nombre y tarifa en la clase padre

    @classmethod
    def crear(cls, nombre, tarifa, dato1=None, dato2=None):
        return cls(nombre, tarifa, dato1)       # dato1 = cantidad de equipos

    @property
    def cantidad(self):
        """Número de equipos incluidos en el alquiler."""
        return self._cantidad

    @classmethod
    def ayuda(cls):
        # Sobrescribe la ayuda general con las reglas propias del alquiler
        return (f"Se cobra por día y por equipo, más un seguro del {cls.SEGURO * 100:g} %. "
                f"Alquiler de 1 a {cls.DURACION_MAXIMA} días y de 1 a "
                f"{cls.CANTIDAD_MAXIMA} equipos.")

    def validar_parametros(self, duracion):
        dias = convertir_numero(duracion, "duración", int)        # Solo días completos
        if not 1 <= dias <= self.DURACION_MAXIMA:                 # Máximo 30 días
            raise DatoInvalidoError(f"Los equipos se alquilan entre 1 y {self.DURACION_MAXIMA} "
                                    f"días; se pidieron {dias}.")
        return dias

    def calcular_costo_base(self, duracion):
        alquiler = self.tarifa * duracion * self._cantidad   # Tarifa diaria x días x equipos
        return alquiler + alquiler * self.SEGURO             # Más el seguro obligatorio

    def describir(self):
        # Descripción propia del alquiler (sobrescribe describir)
        return (f"{self.nombre}: {self._cantidad} equipos, {formato_moneda(self.tarifa)} por día "
                f"cada uno, más {self.SEGURO * 100:g} % de seguro")


class AsesoriaEspecializada(Servicio):
    """Asesoría especializada: se cobra por hora y el nivel del asesor cambia el precio."""

    TIPO = "Asesoría especializada"
    UNIDAD = "horas"
    DURACION_MAXIMA = 6                     # Máximo seis horas por sesión
    ESPECIALIDADES = ("software", "redes", "bases de datos", "seguridad")
    NIVELES = {"básico": 1.0, "avanzado": 1.25, "experto": 1.5}   # Factor sobre la tarifa
    ETIQUETAS = ("Especialidad", "Nivel")

    def __init__(self, nombre, tarifa_hora, especialidad, nivel="básico"):
        # Datos propios de la asesoría: deben estar en las listas permitidas
        self._especialidad = self._elegir(especialidad, "especialidad", self.ESPECIALIDADES)
        self._nivel = self._elegir(nivel, "nivel", tuple(self.NIVELES))
        super().__init__(nombre, tarifa_hora)   # Valida nombre y tarifa en la clase padre

    @classmethod
    def crear(cls, nombre, tarifa, dato1=None, dato2=None):
        return cls(nombre, tarifa, dato1, dato2)    # dato1 = especialidad, dato2 = nivel

    @staticmethod
    def _elegir(valor, campo, opciones):
        """Devuelve la opción permitida que coincide con el valor (sin mirar tildes)."""
        buscado = normalizar(texto_obligatorio(valor, campo))
        for opcion in opciones:
            if normalizar(opcion) == buscado:   # "Basico" coincide con "básico"
                return opcion
        raise DatoInvalidoError(
            f"El valor '{valor}' no es válido para {campo}. Opciones: {', '.join(opciones)}.")

    @property
    def especialidad(self):
        """Área de la asesoría."""
        return self._especialidad

    @property
    def nivel(self):
        """Nivel del asesor: básico, avanzado o experto."""
        return self._nivel

    @classmethod
    def ayuda(cls):
        # Sobrescribe la ayuda general con las opciones de la asesoría
        return (f"Especialidades: {', '.join(cls.ESPECIALIDADES)}. "
                f"Niveles: {', '.join(cls.NIVELES)}. "
                f"Duración: de 1 a {cls.DURACION_MAXIMA} horas.")

    def validar_parametros(self, duracion):
        horas = convertir_numero(duracion, "duración", float)
        if not 1 <= horas <= self.DURACION_MAXIMA:                # Máximo 6 horas
            raise DatoInvalidoError(f"Una asesoría dura entre 1 y {self.DURACION_MAXIMA} "
                                    f"horas; se pidieron {horas:g}.")
        return horas

    def calcular_costo_base(self, duracion):
        return self.tarifa * duracion * self.NIVELES[self._nivel]   # El nivel encarece la hora

    def describir(self):
        # Descripción propia de la asesoría (sobrescribe describir)
        return (f"{self.nombre}: asesoría en {self._especialidad}, nivel {self._nivel}, "
                f"{formato_moneda(self.tarifa)} por hora")


# Catálogo de tipos de servicio: relaciona el nombre visible con su clase
TIPOS_SERVICIO = {clase.TIPO: clase
                  for clase in (ReservaSala, AlquilerEquipo, AsesoriaEspecializada)}



# =============================================================================
# SECCIÓN 4: CLASE RESERVA, GESTOR DEL SISTEMA Y SIMULACIÓN DE OPERACIONES
# Aporte de: Nicolas Farid Salinas Carrillo (rama Nicolas)
# =============================================================================

class Reserva(Entidad):
    """Reserva que integra un cliente, un servicio, una duración y un estado."""

    # Estados posibles de una reserva
    PENDIENTE = "Pendiente"
    CONFIRMADA = "Confirmada"
    CANCELADA = "Cancelada"
    PROCESADA = "Procesada"

    def __init__(self, cliente, servicio, duracion, impuesto=0, descuento=0):
        if not isinstance(cliente, Cliente):                    # El cliente debe ser real
            raise ReservaInvalidaError("La reserva debe tener un cliente registrado.")
        if not isinstance(servicio, Servicio):                  # Y el servicio también
            raise ServicioNoDisponibleError("La reserva debe tener un servicio del catálogo.")
        if not servicio.disponible:                             # No se reserva lo deshabilitado
            raise ServicioNoDisponibleError(
                f"El servicio '{servicio.nombre}' no está disponible en este momento.")
        try:
            self.__duracion = servicio.validar_parametros(duracion)     # Regla del servicio
            self.__costo = servicio.calcular_costo(duracion, impuesto, descuento)
        except (DatoInvalidoError, ParametroFaltanteError) as error:
            # Encadenamiento: el error de validación queda como causa de la reserva inválida
            raise ReservaInvalidaError(
                f"No se pudo crear la reserva de '{servicio.nombre}': {error}") from error
        self.__cliente = cliente                # Atributos privados de la reserva
        self.__servicio = servicio
        self.__estado = Reserva.PENDIENTE       # Toda reserva nueva inicia pendiente
        super().__init__("RES")                 # Código consecutivo: RES-001, RES-002...

    # ----- Propiedades de solo lectura -----
    @property
    def cliente(self):
        return self.__cliente

    @property
    def servicio(self):
        return self.__servicio

    @property
    def duracion(self):
        return self.__duracion

    @property
    def costo(self):
        return self.__costo

    @property
    def estado(self):
        return self.__estado

    def confirmar(self):
        """Pasa la reserva de Pendiente a Confirmada."""
        if self.__estado != Reserva.PENDIENTE:                  # Solo desde Pendiente
            raise OperacionNoPermitidaError(
                f"Solo se confirman reservas pendientes; la reserva {self.id} "
                f"está {self.__estado.lower()}.")
        if not self.__servicio.disponible:                      # El servicio pudo deshabilitarse
            raise ServicioNoDisponibleError(
                f"No se puede confirmar: el servicio '{self.__servicio.nombre}' "
                f"dejó de estar disponible.")
        self.__estado = Reserva.CONFIRMADA

    def cancelar(self):
        """Cancela la reserva mientras no esté cancelada ni procesada."""
        if self.__estado in (Reserva.CANCELADA, Reserva.PROCESADA):    # Estados finales
            raise OperacionNoPermitidaError(
                f"La reserva {self.id} ya está {self.__estado.lower()} y no se puede cancelar.")
        self.__estado = Reserva.CANCELADA

    def procesar(self):
        """Factura la reserva confirmada y la marca como procesada."""
        if self.__estado != Reserva.CONFIRMADA:                 # Solo desde Confirmada
            raise OperacionNoPermitidaError(
                f"Solo se procesan reservas confirmadas; la reserva {self.id} "
                f"está {self.__estado.lower()}.")
        if self.__costo <= 0:                                   # Revisión del valor a cobrar
            raise CalculoInconsistenteError(f"La reserva {self.id} tiene un costo no válido.")
        self.__estado = Reserva.PROCESADA
        return self.__costo                                     # Valor facturado

    def describir(self):
        # Descripción propia de la reserva (sobrescribe describir)
        return (f"{self.__cliente.nombre} | {self.__servicio.nombre} | "
                f"{self.__duracion:g} {self.__servicio.UNIDAD} | "
                f"{formato_moneda(self.__costo)} | {self.__estado}")


class GestorSistema:
    """Coordina clientes, servicios y reservas guardados en listas internas (sin base de datos)."""

    def __init__(self):
        self._clientes = []                 # Lista interna de clientes registrados
        self._servicios = []                # Lista interna del catálogo de servicios
        self._reservas = []                 # Lista interna de reservas
        self._operaciones = 0               # Contador de operaciones ejecutadas

    # ----- Consultas: devuelven copias para proteger las listas internas -----
    @property
    def clientes(self):
        return list(self._clientes)

    @property
    def servicios(self):
        return list(self._servicios)

    @property
    def reservas(self):
        return list(self._reservas)

    def buscar_cliente(self, dato):
        """Busca un cliente por documento o por código (CLI-001); si no existe devuelve None."""
        dato = "" if dato is None else str(dato).strip()
        for cliente in self._clientes:                          # Recorre la lista interna
            if dato in (cliente.documento, cliente.id):
                return cliente
        return None

    def buscar_servicio(self, codigo):
        """Busca un servicio por su código (SER-001); si no existe devuelve None."""
        codigo = "" if codigo is None else str(codigo).strip().upper()
        return next((servicio for servicio in self._servicios if servicio.id == codigo), None)

    def buscar_reserva(self, codigo):
        """Busca una reserva por su código (RES-001); si no existe devuelve None."""
        codigo = "" if codigo is None else str(codigo).strip().upper()
        return next((reserva for reserva in self._reservas if reserva.id == codigo), None)

    # ----- Operaciones del sistema -----
    def registrar_cliente(self, documento, nombre, correo, telefono):
        """Valida y registra un cliente nuevo (try/except/else)."""
        try:
            documento = Cliente.validar_documento(documento)       # Primero el formato
            if self.buscar_cliente(documento) is not None:         # Luego que no se repita
                raise OperacionNoPermitidaError(
                    "Ya existe un cliente registrado con ese documento.")
            cliente = Cliente(documento, nombre, correo, telefono)
        except ErrorSistemaFJ as error:
            registrar_error(error, "Registrar cliente")            # Todo error queda en el log
            raise                           # La interfaz decide cómo mostrar el error
        else:
            self._clientes.append(cliente)  # else: solo se guarda si no hubo errores
            registro.info(f"Cliente registrado: {cliente}")
            return cliente

    def crear_servicio(self, tipo, nombre, tarifa, dato1=None, dato2=None):
        """Crea un servicio del tipo indicado; cada clase sabe construirse (polimorfismo)."""
        try:
            clase = TIPOS_SERVICIO.get(tipo)                       # Busca la clase en el catálogo
            if clase is None:
                raise DatoInvalidoError(f"Tipo de servicio desconocido: '{tipo}'. "
                                        f"Opciones: {', '.join(TIPOS_SERVICIO)}.")
            servicio = clase.crear(nombre, tarifa, dato1, dato2)   # Cada clase se construye sola
        except ErrorSistemaFJ as error:
            registrar_error(error, "Crear servicio")
            raise
        else:
            self._servicios.append(servicio)                       # Se agrega al catálogo
            registro.info(f"Servicio creado ({servicio.TIPO}): {servicio}")
            return servicio

    def cambiar_disponibilidad(self, codigo):
        """Marca un servicio como disponible o no disponible."""
        try:
            servicio = self.buscar_servicio(codigo)
            if servicio is None:
                raise ServicioNoDisponibleError(
                    f"No existe el servicio '{codigo}' en el catálogo.")
            servicio.disponible = not servicio.disponible          # Invierte el estado
        except ErrorSistemaFJ as error:
            registrar_error(error, "Cambiar disponibilidad")
            raise
        else:
            registro.info(f"Disponibilidad actualizada: {servicio}")
            return servicio

    def crear_reserva(self, cliente, codigo_servicio, duracion, impuesto=0, descuento=0):
        """Crea una reserva en estado Pendiente; cliente = documento o código del cliente."""
        try:
            encontrado = self.buscar_cliente(cliente)              # El cliente debe existir
            if encontrado is None:
                raise ReservaInvalidaError(
                    f"No hay un cliente registrado con el dato '{cliente}'.")
            servicio = self.buscar_servicio(codigo_servicio)       # El servicio también
            if servicio is None:
                raise ServicioNoDisponibleError(
                    f"No existe el servicio '{codigo_servicio}' en el catálogo.")
            reserva = Reserva(encontrado, servicio, duracion, impuesto, descuento)
        except ErrorSistemaFJ as error:
            registrar_error(error, "Crear reserva")
            raise
        else:
            self._reservas.append(reserva)                         # Se guarda la reserva válida
            registro.info(f"Reserva creada: {reserva}")
            return reserva

    # Las tres acciones sobre una reserva comparten el mismo manejo de errores
    def confirmar_reserva(self, codigo):
        return self._cambiar_estado(codigo, Reserva.confirmar, "confirmar")

    def cancelar_reserva(self, codigo):
        return self._cambiar_estado(codigo, Reserva.cancelar, "cancelar")

    def procesar_reserva(self, codigo):
        return self._cambiar_estado(codigo, Reserva.procesar, "procesar")

    def _cambiar_estado(self, codigo, accion, verbo):
        """Confirma, cancela o procesa una reserva usando try/except/else/finally."""
        try:
            reserva = self.buscar_reserva(codigo)
            if reserva is None:
                raise OperacionNoPermitidaError(f"No existe la reserva '{codigo}'.")
            accion(reserva)                 # Reserva.confirmar, cancelar o procesar
        except ErrorSistemaFJ as error:
            registrar_error(error, f"No se pudo {verbo} la reserva {codigo}")
            raise
        else:
            registro.info(f"Reserva actualizada: {reserva}")       # Solo si no hubo error
            return reserva
        finally:
            # finally: se ejecuta siempre y deja constancia del intento, exitoso o no
            registro.info(f"Fin del intento de {verbo} la reserva {codigo}.")

    def ejecutar_operacion(self, descripcion, funcion, *argumentos):
        """Ejecuta cualquier operación sin detener el sistema y devuelve su resultado."""
        self._operaciones += 1
        numero = self._operaciones
        # Resumen de la operación: número, descripción, resultado y detalle
        resultado = {"numero": numero, "operacion": descripcion,
                     "estado": "", "detalle": "", "objeto": None}
        try:
            try:
                objeto = funcion(*argumentos)   # Ejecuta la operación pedida
            finally:
                # try/finally: se registra el fin de la operación, falle o no
                registro.info(f"Operación {numero} finalizada: {descripcion}")
        except ErrorSistemaFJ as error:
            # Error previsto: el método que lo lanzó ya lo escribió en el log
            resultado.update(estado="Error controlado", detalle=f"{error.titulo}: {error}")
        except Exception as error:          # Último recurso: errores no previstos
            registro.critical(f"Operación {numero} ({descripcion}) -> error inesperado "
                              f"{type(error).__name__}: {error}", exc_info=True)
            resultado.update(estado="Error inesperado",
                             detalle=f"{type(error).__name__}: {error}")
        else:
            detalle = str(objeto) if objeto is not None else "Operación realizada."
            resultado.update(estado="Éxito", detalle=detalle, objeto=objeto)
        return resultado


def resumir_simulacion(resultados):
    """Cuenta los resultados de la simulación y los resume en una frase."""
    exitos = sum(1 for resultado in resultados if resultado["estado"] == "Éxito")
    inesperados = sum(1 for resultado in resultados if resultado["estado"] == "Error inesperado")
    controlados = len(resultados) - exitos - inesperados       # El resto: errores previstos
    return (f"Se ejecutaron {len(resultados)} operaciones: {exitos} exitosas, "
            f"{controlados} con error controlado y {inesperados} con error inesperado capturado. "
            f"El sistema siguió funcionando.")


def ejecutar_simulacion(gestor):
    """Simula operaciones completas, válidas e inválidas, sin que el sistema se detenga."""
    registro.info("===== INICIO DE LA SIMULACIÓN DE OPERACIONES =====")
    resultados = []                         # Aquí se acumula el resultado de cada operación

    def paso(descripcion, funcion, *argumentos):
        """Ejecuta una operación de forma segura y guarda su resultado."""
        resultado = gestor.ejecutar_operacion(descripcion, funcion, *argumentos)
        resultados.append(resultado)
        return resultado["objeto"]          # Objeto creado o None si hubo error

    def codigo(objeto):
        """Código del objeto creado o un código inexistente si la creación falló."""
        return objeto.id if objeto is not None else "NO-EXISTE"

    # Registros válidos e inválidos de clientes
    paso("Registrar cliente válido: Ana María Gómez", gestor.registrar_cliente,
         "1012345678", "Ana María Gómez", "ana.gomez@correo.com", "3001234567")
    paso("Registrar cliente válido: Carlos Pérez", gestor.registrar_cliente,
         "79876543", "Carlos Pérez", "carlos.perez@correo.com", "3109876543")
    paso("Registrar cliente con correo inválido", gestor.registrar_cliente,
         "52123456", "Laura Ríos", "laura.rios.correo.com", "3201112233")
    paso("Registrar cliente sin nombre", gestor.registrar_cliente,
         "41234567", "", "sin.nombre@correo.com", "3005556677")
    paso("Registrar cliente con documento repetido", gestor.registrar_cliente,
         "1012345678", "Ana Duplicada", "otra@correo.com", "3001234567")
    # Creación correcta e incorrecta de servicios
    sala = paso("Crear servicio: Sala de juntas", gestor.crear_servicio,
                "Reserva de sala", "Sala de juntas", "50000", "12")
    equipos = paso("Crear servicio: Portátiles", gestor.crear_servicio,
                   "Alquiler de equipo", "Portátiles", "40000", "3")
    asesoria = paso("Crear servicio: Asesoría en software", gestor.crear_servicio,
                    "Asesoría especializada", "Asesoría en software", "80000",
                    "software", "experto")
    paso("Crear servicio con tarifa negativa", gestor.crear_servicio,
         "Reserva de sala", "Auditorio", "-20000", "50")
    paso("Crear asesoría con especialidad no ofrecida", gestor.crear_servicio,
         "Asesoría especializada", "Asesoría en cocina", "60000", "cocina", "básico")
    # Reservas exitosas y su ciclo de vida
    reserva_sala = paso("Reservar la sala 3 horas con IVA del 19 %", gestor.crear_reserva,
                        "1012345678", codigo(sala), "3", "19", "0")
    paso("Confirmar la reserva de la sala", gestor.confirmar_reserva, codigo(reserva_sala))
    paso("Procesar (facturar) la reserva de la sala", gestor.procesar_reserva,
         codigo(reserva_sala))
    reserva_asesoria = paso("Reservar asesoría 2 horas con IVA y 10 % de descuento",
                            gestor.crear_reserva, "79876543", codigo(asesoria), "2", "19", "10")
    paso("Cancelar la reserva de asesoría", gestor.cancelar_reserva, codigo(reserva_asesoria))
    paso("Cancelar otra vez la misma reserva", gestor.cancelar_reserva, codigo(reserva_asesoria))
    paso("Procesar una reserva cancelada", gestor.procesar_reserva, codigo(reserva_asesoria))
    # Reservas fallidas, servicio no disponible y cálculo inconsistente
    paso("Reservar la sala por 12 horas (máximo 8)", gestor.crear_reserva,
         "1012345678", codigo(sala), "12", "19", "0")
    paso("Reservar con un cliente no registrado", gestor.crear_reserva,
         "99999999", codigo(sala), "2", "19", "0")
    paso("Marcar los portátiles como no disponibles", gestor.cambiar_disponibilidad,
         codigo(equipos))
    paso("Reservar portátiles no disponibles", gestor.crear_reserva,
         "79876543", codigo(equipos), "2", "19", "0")
    paso("Reservar con un descuento del 150 %", gestor.crear_reserva,
         "79876543", codigo(asesoria), "1", "19", "150")
    # Error no previsto: el sistema lo captura, lo registra y sigue funcionando
    paso("Operación no soportada: eliminar un cliente",
         lambda: getattr(gestor, "eliminar_cliente")("1012345678"))

    registro.info(f"===== FIN DE LA SIMULACIÓN. {resumir_simulacion(resultados)} =====")
    return resultados



# =============================================================================
# SECCIÓN 5: INTERFAZ GRÁFICA (tkinter, ttk y messagebox) Y PUNTO DE ENTRADA
# Aporte de: Kevin Geovani Santos Ortega (rama Kevin)
# =============================================================================

# >>> APORTE PENDIENTE DE KEVIN: reemplace esta línea por el contenido de seccion_5_interfaz.py
