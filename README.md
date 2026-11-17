<div align="center">

# Sistema Integral de Gestión de Clientes, Servicios y Reservas

**Software FJ** · Aplicación de escritorio en Python, orientada a objetos, sin base de datos y con
manejo avanzado de excepciones

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Interfaz](https://img.shields.io/badge/Interfaz-tkinter%20%2B%20ttk-2E7D32)
![Base de datos](https://img.shields.io/badge/Base%20de%20datos-ninguna-lightgrey)
![Licencia](https://img.shields.io/badge/Licencia-MIT-blue)

Curso **Programación (213023)** · Grupo **213023_638** · UNAD<br>
Fase 4: Componente práctico — Prácticas simuladas

</div>

---

## Contenido

1. [Qué hace](#qué-hace)
2. [Cómo ejecutarlo](#cómo-ejecutarlo)
3. [Cómo se usa](#cómo-se-usa)
4. [Cómo funciona por dentro](#cómo-funciona-por-dentro)
5. [Mapas de decisión](#mapas-de-decisión)
6. [Manejo de excepciones](#manejo-de-excepciones)
7. [Registro de eventos (logs)](#registro-de-eventos-logs)
8. [Simulación de operaciones](#simulación-de-operaciones)
9. [Estructura del repositorio](#estructura-del-repositorio)
10. [Equipo y trabajo colaborativo](#equipo-y-trabajo-colaborativo)
11. [Licencia](#licencia)

> [!TIP]
> Los diagramas de este README se pueden ampliar: pase el mouse sobre cualquiera de ellos y
> GitHub muestra botones para acercar, alejar, desplazar y abrirlo en pantalla completa.

---

## Qué hace

Software FJ ofrece tres tipos de servicio: **reserva de salas**, **alquiler de equipos** y
**asesorías especializadas**. El programa permite:

| Función | Descripción |
|---|---|
| Registrar clientes | Valida documento, nombre, correo y teléfono; guarda los datos personales como atributos privados y muestra el documento protegido (`******6789`) |
| Crear servicios | Cada tipo de servicio tiene sus propios datos, reglas y fórmula de costo |
| Gestionar reservas | Crea reservas con impuesto y descuento, y las confirma, cancela o procesa según su estado |
| Simular operaciones | Ejecuta 23 operaciones válidas e inválidas de una vez y demuestra que el sistema nunca se detiene |
| Registrar eventos | Escribe cada evento y cada error en `registro_eventos.log`, incluida la causa de los errores encadenados |

Toda la información vive en **objetos y listas en memoria**: no hay base de datos. El único archivo
que escribe el programa es el registro de eventos.

**Conceptos de programación orientada a objetos aplicados:**

| Concepto | Dónde se ve |
|---|---|
| Abstracción | Clases abstractas `Entidad` y `Servicio` con métodos `@abstractmethod` |
| Herencia | `Cliente`, `Servicio` y `Reserva` heredan de `Entidad`; tres servicios heredan de `Servicio` |
| Polimorfismo | Cada servicio sobrescribe `crear`, `validar_parametros`, `calcular_costo_base`, `describir` y `ayuda` |
| Encapsulación | Atributos privados (`__documento`, `__estado`…), propiedades que validan y listas internas protegidas |
| Sobrecarga | `calcular_costo` con tres variantes declaradas con `@overload` |
| Excepciones | 7 excepciones propias, `try/except`, `else`, `finally` y encadenamiento con `raise ... from` |

---

## Cómo ejecutarlo

**Requisitos:** Python 3.10 o superior con `tkinter` (viene incluido en el instalador oficial de
Windows). No necesita bases de datos ni paquetes adicionales.

| Opción | Pasos |
|---|---|
| Visual Studio Code | Abra `Integral_de_Gestión_de_C_S_R.py` y pulse ▶ (*Run Python File*) |
| Terminal | `python Integral_de_Gestión_de_C_S_R.py` |

Al iniciar se abre una ventana con cinco pestañas: **Clientes**, **Servicios**, **Reservas**,
**Simulación** y **Registro de eventos**.

---

## Cómo se usa

| Pestaña | Qué se hace | Botones |
|---|---|---|
| **Clientes** | Escribir documento, nombre completo, correo y teléfono | **Registrar cliente** |
| **Servicios** | Elegir el tipo de servicio; las etiquetas y la ayuda cambian según el tipo | **Crear servicio** · **Cambiar disponibilidad del seleccionado** |
| **Reservas** | Elegir cliente y servicio, escribir la duración, el IVA (19 % por defecto) y el descuento | **Crear reserva** · **Confirmar** · **Cancelar** · **Procesar** |
| **Simulación** | Ejecutar las 23 operaciones de demostración (una vez por sesión) | **Ejecutar simulación** |
| **Registro de eventos** | Ver el contenido de `registro_eventos.log` | **Actualizar** |

Cada operación exitosa se confirma con un cuadro de diálogo de información; cada error se muestra
con un cuadro de diálogo de error cuyo título es el tipo de excepción, y la ventana sigue abierta.

---

## Cómo funciona por dentro

### Flujo general de la aplicación

```mermaid
flowchart TD
    A(["Inicio: python Integral_de_Gestión_de_C_S_R.py"]) --> B["configurar_registro()"]
    B --> C{"¿Se pudo abrir<br/>registro_eventos.log?"}
    C -->|Sí| D["Los eventos se guardan en el archivo"]
    C -->|No| E["Aviso: los eventos se muestran en la consola"]
    D --> F["main() crea la ventana AplicacionFJ"]
    E --> F
    F --> G{"¿Hay entorno gráfico?"}
    G -->|No| H["TclError registrado en el log<br/>y mensaje en la consola"]
    G -->|Sí| I["Ventana con 5 pestañas"]
    I --> J["El usuario pulsa un botón"]
    J --> K["_ejecutar() llama al GestorSistema"]
    K --> L{"¿Cómo terminó la operación?"}
    L -->|Éxito| M["Se refrescan las tablas<br/>messagebox.showinfo"]
    L -->|ErrorSistemaFJ| N["El error ya está en el log<br/>messagebox.showerror con su título"]
    L -->|Error no previsto| O["Se registra como CRÍTICO<br/>y se informa sin cerrar la ventana"]
    M --> I
    N --> I
    O --> I
    I -->|Cerrar la ventana| P(["Fin de sesión registrado en el log"])
    H --> P

    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef error fill:#fdecea,stroke:#c62828,color:#000
    class M ok
    class N,O,H error
```

### Arquitectura en cinco secciones

El programa es un solo archivo dividido en cinco secciones. La lógica del negocio (secciones 1 a
4) no depende de la interfaz (sección 5), por eso sus clases se pueden usar sin abrir ninguna
ventana.

```mermaid
flowchart LR
    subgraph S5["Sección 5 · Interfaz gráfica"]
        APP["AplicacionFJ<br/>tkinter · ttk · messagebox"]
        MAIN["main()"]
    end
    subgraph S4["Sección 4 · Reservas, gestor y simulación"]
        GES["GestorSistema<br/>listas internas"]
        RES["Reserva"]
        SIM["ejecutar_simulacion()"]
    end
    subgraph S3["Sección 3 · Servicios"]
        SER["Servicio (abstracta)"]
        TIPOS["ReservaSala · AlquilerEquipo<br/>AsesoriaEspecializada"]
    end
    subgraph S2["Sección 2 · Validaciones y clientes"]
        VAL["Funciones de validación"]
        CLI["Cliente"]
    end
    subgraph S1["Sección 1 · Base"]
        ENT["Entidad (abstracta)"]
        EXC["7 excepciones propias"]
        LOG[("registro_eventos.log")]
    end
    MAIN --> APP
    APP --> GES
    SIM --> GES
    GES --> RES
    RES --> CLI
    RES --> SER
    SER --> TIPOS
    CLI --> VAL
    SER --> VAL
    VAL --> EXC
    CLI --> ENT
    SER --> ENT
    RES --> ENT
    GES -.->|registra| LOG
    APP -.->|registra| LOG
```

| Sección | Contenido | Aporte (según el encabezado del código) |
|---|---|---|
| 1 | Configuración, registro de eventos, excepciones personalizadas y clase abstracta `Entidad` | Jhon Jaiver Supelano Rojas |
| 2 | Funciones de validación y clase `Cliente` | Johan Ricardo Reina Florindo |
| 3 | Clase abstracta `Servicio` y servicios especializados | Mauro Daniel Rodríguez Pinzón |
| 4 | Clase `Reserva`, `GestorSistema` y simulación de operaciones | Nicolas Farid Salinas Carrillo |
| 5 | Interfaz gráfica (tkinter, ttk y messagebox) y punto de entrada | Líder del grupo de trabajo |

### Diagrama de clases

```mermaid
classDiagram
    direction TB
    class Entidad {
        <<abstract>>
        #_id
        #_fecha_creacion
        +id
        +describir()* str
    }
    class Cliente {
        -__documento
        -__nombre
        -__correo
        -__telefono
        +validar_documento(documento)$ str
        +documento_protegido() str
        +describir() str
    }
    class Servicio {
        <<abstract>>
        +TIPO
        +UNIDAD
        +DURACION_MAXIMA
        +disponible
        +crear(nombre, tarifa, dato1, dato2)$
        +validar_parametros(duracion)*
        +calcular_costo_base(duracion)*
        +calcular_costo(duracion, impuesto, descuento) float
        +ayuda()$ str
    }
    class ReservaSala {
        +capacidad
        +calcular_costo_base(duracion)
    }
    class AlquilerEquipo {
        +cantidad
        +SEGURO
        +calcular_costo_base(duracion)
    }
    class AsesoriaEspecializada {
        +especialidad
        +nivel
        +calcular_costo_base(duracion)
    }
    class Reserva {
        -__cliente
        -__servicio
        -__duracion
        -__costo
        -__estado
        +confirmar()
        +cancelar()
        +procesar() float
    }
    class GestorSistema {
        -_clientes
        -_servicios
        -_reservas
        +registrar_cliente(documento, nombre, correo, telefono)
        +crear_servicio(tipo, nombre, tarifa, dato1, dato2)
        +crear_reserva(cliente, servicio, duracion, impuesto, descuento)
        +confirmar_reserva(codigo)
        +cancelar_reserva(codigo)
        +procesar_reserva(codigo)
        +ejecutar_operacion(descripcion, funcion)
    }
    class AplicacionFJ {
        +gestor
        -_ejecutar(accion, titulo, mensaje)
        +report_callback_exception(tipo, valor, rastro)
    }
    Entidad <|-- Cliente
    Entidad <|-- Servicio
    Entidad <|-- Reserva
    Servicio <|-- ReservaSala
    Servicio <|-- AlquilerEquipo
    Servicio <|-- AsesoriaEspecializada
    Reserva o-- Cliente : integra
    Reserva o-- Servicio : integra
    GestorSistema *-- Cliente : lista interna
    GestorSistema *-- Servicio : lista interna
    GestorSistema *-- Reserva : lista interna
    AplicacionFJ --> GestorSistema : usa
```

---

## Mapas de decisión

### Registro de un cliente

```mermaid
flowchart TD
    A(["Clic en Registrar cliente"]) --> B{"¿El documento<br/>está vacío?"}
    B -->|Sí| E1["ParametroFaltanteError<br/>El campo documento es obligatorio"]
    B -->|No| C{"¿Tiene solo dígitos?"}
    C -->|No| E2["DatoInvalidoError<br/>solo puede contener números"]
    C -->|Sí| D{"¿Tiene entre 6<br/>y 10 dígitos?"}
    D -->|No| E3["DatoInvalidoError<br/>longitud no permitida"]
    D -->|Sí| F{"¿Ya existe un cliente<br/>con ese documento?"}
    F -->|Sí| E4["OperacionNoPermitidaError<br/>documento repetido"]
    F -->|No| G{"¿Nombre de 3 o más letras,<br/>solo letras y espacios?"}
    G -->|No| E5["ParametroFaltanteError<br/>o DatoInvalidoError"]
    G -->|Sí| H{"¿Correo con formato<br/>usuario@dominio.ext?"}
    H -->|No| E6["DatoInvalidoError<br/>correo sin formato válido"]
    H -->|Sí| I{"¿Teléfono de 7<br/>a 10 dígitos?"}
    I -->|No| E7["DatoInvalidoError<br/>teléfono no válido"]
    I -->|Sí| OK1["Cliente CLI-### creado<br/>y agregado a la lista interna"]
    OK1 --> OK2(["Log INFO con el documento protegido<br/>y cuadro Cliente registrado"])
    E1 --> X["registrar_error() escribe ERROR en el log"]
    E2 --> X
    E3 --> X
    E4 --> X
    E5 --> X
    E6 --> X
    E7 --> X
    X --> Y(["messagebox.showerror con el título del error<br/>la ventana sigue abierta"])

    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef error fill:#fdecea,stroke:#c62828,color:#000
    class OK1,OK2 ok
    class E1,E2,E3,E4,E5,E6,E7 error
```

### Creación de un servicio

```mermaid
flowchart TD
    A(["Clic en Crear servicio"]) --> B{"¿El tipo está en<br/>TIPOS_SERVICIO?"}
    B -->|No| E1["DatoInvalidoError<br/>tipo desconocido"]
    B -->|Sí| C{"Cada clase se construye sola<br/>con crear() - polimorfismo"}
    C -->|Reserva de sala| S1{"¿Capacidad entera<br/>de 1 a 100 personas?"}
    C -->|Alquiler de equipo| S2{"¿Cantidad entera<br/>de 1 a 20 equipos?"}
    C -->|Asesoría especializada| S3{"¿Especialidad y nivel<br/>en las listas permitidas?"}
    S1 -->|No| E2["DatoInvalidoError"]
    S2 -->|No| E2
    S3 -->|No| E2
    S1 -->|Sí| N{"¿Nombre del servicio<br/>de 3 o más caracteres?"}
    S2 -->|Sí| N
    S3 -->|Sí| N
    N -->|No| E3["ParametroFaltanteError<br/>o DatoInvalidoError"]
    N -->|Sí| T{"¿Tarifa numérica y<br/>de al menos 1.000 pesos?"}
    T -->|No| E4["DatoInvalidoError<br/>encadenado a ValueError si no es un número"]
    T -->|Sí| OK1(["Servicio SER-### creado,<br/>disponible y agregado al catálogo"])

    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef error fill:#fdecea,stroke:#c62828,color:#000
    class OK1 ok
    class E1,E2,E3,E4 error
```

| Tipo de servicio | Dato propio | Duración por reserva | Fórmula del costo base |
|---|---|---|---|
| Reserva de sala | Capacidad: 1 a 100 personas | 1 a 8 horas (admite fracciones) | tarifa × horas |
| Alquiler de equipo | Cantidad: 1 a 20 equipos | 1 a 30 días completos | tarifa × días × equipos + 5 % de seguro |
| Asesoría especializada | Especialidad (software, redes, bases de datos, seguridad) y nivel | 1 a 6 horas | tarifa × horas × factor del nivel (básico 1,0 · avanzado 1,25 · experto 1,5) |

### Creación de una reserva

```mermaid
flowchart TD
    A(["Clic en Crear reserva"]) --> B{"¿Existe el cliente?<br/>documento o código CLI"}
    B -->|No| E1["ReservaInvalidaError<br/>cliente no registrado"]
    B -->|Sí| C{"¿Existe el servicio?<br/>código SER"}
    C -->|No| E2["ServicioNoDisponibleError<br/>no está en el catálogo"]
    C -->|Sí| D{"¿El servicio<br/>está disponible?"}
    D -->|No| E3["ServicioNoDisponibleError"]
    D -->|Sí| V{"validar_parametros(duración)<br/>¿está dentro del rango del servicio?"}
    V -->|No| E4["DatoInvalidoError"]
    E4 --> E5["raise ReservaInvalidaError(...) from error<br/>el log guarda el error y su causa"]
    V -->|Sí| P{"¿Impuesto y descuento<br/>entre 0 % y 100 %?"}
    P -->|No| E6["CalculoInconsistenteError"]
    P -->|Sí| T{"¿Costo total<br/>mayor que cero?"}
    T -->|No| E7["CalculoInconsistenteError"]
    T -->|Sí| OK1(["Reserva RES-### en estado Pendiente<br/>con su costo calculado"])

    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef error fill:#fdecea,stroke:#c62828,color:#000
    class OK1 ok
    class E1,E2,E3,E4,E5,E6,E7 error
```

### Cálculo del costo: sobrecarga y polimorfismo

`calcular_costo` es un método sobrecargado: se declara con tres variantes (`@overload`) y una sola
implementación con parámetros opcionales. La parte que cambia según el servicio la resuelve el
polimorfismo.

```mermaid
flowchart LR
    V1["calcular_costo(duración)"] --> IMP
    V2["calcular_costo(duración, impuesto)"] --> IMP
    V3["calcular_costo(duración, impuesto, descuento)"] --> IMP
    IMP["Implementación única<br/>impuesto = 0 y descuento = 0 por defecto"] --> VAL["validar_parametros(duración)"]
    VAL --> Q{"¿Qué servicio es?"}
    Q -->|ReservaSala| F1["tarifa × horas"]
    Q -->|AlquilerEquipo| F2["tarifa × días × equipos<br/>más 5 % de seguro"]
    Q -->|AsesoriaEspecializada| F3["tarifa × horas<br/>× factor del nivel"]
    F1 --> DES["subtotal menos el descuento"]
    F2 --> DES
    F3 --> DES
    DES --> IVA["más el impuesto"]
    IVA --> TOT(["Total redondeado a 2 decimales"])
```

| Ejemplo: sala de 50.000 pesos por hora, 3 horas | Variante | Resultado |
|---|---|---|
| `calcular_costo(3)` | Solo el costo base | $ 150.000,00 |
| `calcular_costo(3, 19)` | Con IVA del 19 % | $ 178.500,00 |
| `calcular_costo(3, 19, 10)` | Con 10 % de descuento y luego el IVA | $ 160.650,00 |

### Ciclo de vida de una reserva

```mermaid
stateDiagram-v2
    [*] --> Pendiente: crear_reserva()
    Pendiente --> Confirmada: confirmar()
    Pendiente --> Cancelada: cancelar()
    Confirmada --> Procesada: procesar()
    Confirmada --> Cancelada: cancelar()
    Procesada --> [*]
    Cancelada --> [*]
    note right of Confirmada
        Para confirmar, el servicio
        debe seguir disponible
    end note
    note right of Procesada
        Cancelar o procesar de nuevo
        lanza OperacionNoPermitidaError
    end note
```

### Recorrido de una operación

Así viaja una reserva desde el botón hasta el archivo de logs, con el caso exitoso y el caso con
error encadenado:

```mermaid
sequenceDiagram
    actor U as Usuario
    participant V as AplicacionFJ
    participant G as GestorSistema
    participant R as Reserva
    participant S as Servicio
    participant L as registro_eventos.log
    U->>V: Pulsa Crear reserva
    V->>G: crear_reserva(cliente, servicio, duración, IVA, descuento)
    G->>G: buscar_cliente() y buscar_servicio()
    G->>R: Reserva(cliente, servicio, duración, ...)
    R->>S: validar_parametros(duración)
    alt Duración válida
        R->>S: calcular_costo(duración, IVA, descuento)
        S-->>R: costo total
        R-->>G: reserva en estado Pendiente
        G->>L: INFO Reserva creada
        G-->>V: reserva
        V->>U: Cuadro Reserva creada con el costo
    else Duración fuera de rango
        S-->>R: DatoInvalidoError
        R-->>G: ReservaInvalidaError encadenada a DatoInvalidoError
        G->>L: ERROR con la causa encadenada
        G-->>V: vuelve a lanzar la excepción
        V->>U: Cuadro de error Reserva inválida
    end
```

### Flujo de trabajo del equipo en GitHub

```mermaid
flowchart LR
    A(["Integrante"]) --> B["Trabaja en su rama<br/>Jhon, Johan, Mauro o Nicolas"]
    B --> C["Update from main<br/>trae lo ya aprobado"]
    C --> D["Agrega su sección<br/>en VS Code"]
    D --> E{"¿El programa funciona?"}
    E -->|No| D
    E -->|Sí| F["Commits y Push origin<br/>en GitHub Desktop"]
    F --> G["Pull Request hacia main"]
    G --> H{"¿Jhon lo aprueba?"}
    H -->|Pide cambios| D
    H -->|Sí| I(["Merge en main"])

    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#000
    class I ok
```

---

## Manejo de excepciones

### Jerarquía de excepciones propias

```mermaid
flowchart TD
    EX["Exception"] --> BASE["ErrorSistemaFJ<br/>título: Error del sistema"]
    BASE --> D1["DatoInvalidoError<br/>título: Dato inválido"]
    BASE --> D2["ParametroFaltanteError<br/>título: Parámetro faltante"]
    BASE --> D3["OperacionNoPermitidaError<br/>título: Operación no permitida"]
    BASE --> D4["ReservaInvalidaError<br/>título: Reserva inválida"]
    BASE --> D5["ServicioNoDisponibleError<br/>título: Servicio no disponible"]
    BASE --> D6["CalculoInconsistenteError<br/>título: Cálculo inconsistente"]

    classDef base fill:#e3f2fd,stroke:#1565c0,color:#000
    class BASE base
```

| Excepción | Cuándo se lanza | Ejemplo |
|---|---|---|
| `DatoInvalidoError` | Un dato tiene un formato o un valor no permitido | Correo sin @, tarifa negativa |
| `ParametroFaltanteError` | Falta un dato obligatorio | Nombre vacío, ninguna reserva seleccionada |
| `OperacionNoPermitidaError` | La acción no es válida en el estado actual | Documento repetido, cancelar una reserva procesada |
| `ReservaInvalidaError` | El intento de reserva no cumple las reglas | Cliente inexistente, duración fuera de rango |
| `ServicioNoDisponibleError` | El servicio no existe o está deshabilitado | Reservar un equipo marcado como no disponible |
| `CalculoInconsistenteError` | El cálculo recibe o produce valores sin sentido | Descuento del 150 % |

### Bloques usados y dónde

| Bloque | Dónde se usa | Para qué |
|---|---|---|
| `try/except` | Todos los métodos del gestor y la interfaz | Capturar el error, registrarlo y relanzarlo o mostrarlo |
| `try/except/else` | `configurar_registro`, `registrar_cliente`, `crear_servicio`, `crear_reserva`, `_ejecutar` | Guardar o informar solo cuando no hubo error |
| `try/finally` | `leer_registro` y `ejecutar_operacion` | Cerrar el archivo y registrar el fin de cada operación, falle o no |
| `try/except/else/finally` | `_cambiar_estado` y `main` | Dejar constancia del intento aunque la acción falle |
| `raise ... from` | `convertir_numero` y `Reserva` | Encadenar la excepción original como causa |

### Cómo una operación nunca detiene el sistema

```mermaid
flowchart TD
    A["ejecutar_operacion(descripción, función)"] --> B["try interno: ejecuta la función"]
    B --> C["finally: registra Operación N finalizada<br/>se ejecuta siempre"]
    C --> D{"¿Cómo terminó?"}
    D -->|Sin error| E["else: resultado Éxito"]
    D -->|ErrorSistemaFJ| F["except ErrorSistemaFJ: Error controlado<br/>ya quedó en el log"]
    D -->|Cualquier otra excepción| G["except Exception: Error inesperado<br/>log CRÍTICO con la traza completa"]
    E --> H(["Devuelve el resultado<br/>y el sistema sigue funcionando"])
    F --> H
    G --> H

    classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#000
    classDef error fill:#fdecea,stroke:#c62828,color:#000
    class E ok
    class F,G error
```

En la interfaz hay dos redes de seguridad más: `_ejecutar()` captura cualquier error de un botón,
y `report_callback_exception()` sobrescribe el método de tkinter para que un error en un evento
no cierre la aplicación.

---

## Registro de eventos (logs)

El archivo `registro_eventos.log` se crea en la carpeta del programa al ejecutarlo. Cada línea tiene
la fecha, el nivel y el mensaje. Los documentos de los clientes aparecen protegidos.

| Nivel | Uso |
|---|---|
| `INFO` | Eventos normales: inicio, registros, creaciones, cambios de estado y fin de cada operación |
| `ERROR` | Errores controlados, con su tipo y, si existe, la excepción que los originó |
| `CRÍTICO` | Errores no previstos, con la traza completa |
| `AVISO` | El archivo de logs no se pudo abrir y los eventos se muestran en la consola |

Ejemplo real de una sesión:

```text
2026-10-19 15:40:23 | INFO    | Cliente registrado: CLI-001 - Valentina Ruiz Castro | doc. ******6789 | valentina.ruiz@correo.com | tel. 3014567890
2026-10-19 15:40:25 | ERROR   | Registrar cliente -> DatoInvalidoError: El correo 'laura.rios.correo.com' no tiene un formato válido (ejemplo: usuario@dominio.com).
2026-10-19 15:40:33 | INFO    | Reserva creada: RES-001 - Valentina Ruiz Castro | Sala de capacitación | 3 horas | $ 160.650,00 | Pendiente
2026-10-19 15:40:35 | ERROR   | Crear reserva -> ReservaInvalidaError: No se pudo crear la reserva de 'Sala de capacitación': Una sala se reserva entre 1 y 8 horas; se pidieron 12. | Causa: DatoInvalidoError: Una sala se reserva entre 1 y 8 horas; se pidieron 12.
2026-10-19 15:40:38 | INFO    | Fin del intento de procesar la reserva RES-001.
2026-10-19 15:40:41 | CRÍTICO | Operación 23 (Operación no soportada: eliminar un cliente) -> error inesperado AttributeError: 'GestorSistema' object has no attribute 'eliminar_cliente'
```

> [!NOTE]
> El archivo de logs se genera cada vez que se ejecuta el programa; no hace falta subirlo al
> repositorio.

---

## Simulación de operaciones

La pestaña **Simulación** ejecuta 23 operaciones completas sobre los mismos datos de la
aplicación. Cada operación pasa por `ejecutar_operacion()`, así que ningún error detiene la
secuencia.

```mermaid
pie showData title Resultado de las 23 operaciones simuladas
    "Éxito" : 11
    "Error controlado" : 11
    "Error inesperado capturado" : 1
```

<details>
<summary><b>Ver las 23 operaciones y su resultado esperado</b></summary>

| N.º | Operación | Resultado |
|---|---|---|
| 1 | Registrar cliente válido: Ana María Gómez | Éxito |
| 2 | Registrar cliente válido: Carlos Pérez | Éxito |
| 3 | Registrar cliente con correo inválido | `DatoInvalidoError` |
| 4 | Registrar cliente sin nombre | `ParametroFaltanteError` |
| 5 | Registrar cliente con documento repetido | `OperacionNoPermitidaError` |
| 6 | Crear servicio: Sala de juntas | Éxito |
| 7 | Crear servicio: Portátiles | Éxito |
| 8 | Crear servicio: Asesoría en software | Éxito |
| 9 | Crear servicio con tarifa negativa | `DatoInvalidoError` |
| 10 | Crear asesoría con especialidad no ofrecida | `DatoInvalidoError` |
| 11 | Reservar la sala 3 horas con IVA del 19 % | Éxito: $ 178.500,00 |
| 12 | Confirmar la reserva de la sala | Éxito |
| 13 | Procesar (facturar) la reserva de la sala | Éxito |
| 14 | Reservar asesoría 2 horas con IVA y 10 % de descuento | Éxito: $ 257.040,00 |
| 15 | Cancelar la reserva de asesoría | Éxito |
| 16 | Cancelar otra vez la misma reserva | `OperacionNoPermitidaError` |
| 17 | Procesar una reserva cancelada | `OperacionNoPermitidaError` |
| 18 | Reservar la sala por 12 horas (máximo 8) | `ReservaInvalidaError` encadenada a `DatoInvalidoError` |
| 19 | Reservar con un cliente no registrado | `ReservaInvalidaError` |
| 20 | Marcar los portátiles como no disponibles | Éxito |
| 21 | Reservar portátiles no disponibles | `ServicioNoDisponibleError` |
| 22 | Reservar con un descuento del 150 % | `CalculoInconsistenteError` |
| 23 | Operación no soportada: eliminar un cliente | Error inesperado (`AttributeError`) capturado y registrado como CRÍTICO |

</details>

---

## Estructura del repositorio

```text
sistema-integral-CSR/
├── Integral_de_Gestión_de_C_S_R.py   # Programa completo en 5 secciones
├── LICENSE                           # Licencia MIT
└── README.md                         # Este documento
```

---

## Equipo y trabajo colaborativo

| Integrante | Rama |
|---|---|
| Jhon Jaiver Supelano Rojas (líder del grupo) | `Jhon` |
| Johan Ricardo Reina Florindo | `Johan` |
| Mauro Daniel Rodríguez Pinzón | `Mauro` |
| Nicolas Farid Salinas Carrillo | `Nicolas` |

Cada integrante trabaja en su propia rama con **GitHub Desktop** y **Visual Studio Code**, y sus
cambios llegan a `main` por medio de un Pull Request que revisa y aprueba el líder del grupo.

**Tutor:** Edduar Yakseir Perez Perez · **Universidad Nacional Abierta y a Distancia (UNAD)** ·
Escuela de Ciencias Básicas, Tecnología e Ingeniería

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulte el archivo [LICENSE](LICENSE).
