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

