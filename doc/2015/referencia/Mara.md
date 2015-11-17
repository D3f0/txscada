% Protocolo MARA
% Versión 1.4 (?)
% Tramas Ethernet


Conceptos básicos del sistema
-----------------------------

* Protocolo binario maestro/esclavo.
* Comunicación cliente/servidor.
* Comunicación por *polling*
* Modo RS485 multi-punto y modo punto a punto (PtP) sobre TCP.
  * Mara/RS485 entre concentrador y red de placas de campo.
  * Mara/TCP entre concentrador y centro de control (SCADA/HMI).

Esquema
-------
```

               ┌────────────────┐
               │ Cent.Control   │
               │ nguru (txscada)│
               └────────────────┘
                        │   TCP
                        │  (9761)
                        ▼
               ┌─────────────────┐
               │ Concentrador  1 │
               └─────────────────┘
                        │
     ┌────────────┬─────┴────┬──────────┐  RS485
     │            │          │          │
     ▼            ▼          ▼          ▼
┌────────┐   ┌────────┐ ┌────────┐ ┌────────┐
│ IED 2  │   │ IED 3  │ │ IED 4  │ │ IED 5  │
└────────┘   └────────┘ └────────┘ └────────┘

```

Mara sobre TCP
--------------
* El maestro es el cliente (`socket connect`) y el esclavo
 es el servidor (`socket accept`).
* El servidor (a.k.a. **concentrador**) escucha conexión en puerto 9761. Responde comandos Mara que envía el cliente. *Atiende un solo cliente.*
* El servidor tiene *aguas abajo* una red de placas:
  * Estas placas se comunican en Mara con el concentrador en modo multi-punto (no PtP) mediante [RS485](https://es.wikipedia.org/wiki/RS-485).
  * Estas placas realizan la función de adqusisción de datos.
  * El concentrador respalda los datos y luego envía al cliente.
* El cliente es un software SCADA/HMI bautizado [nguru](https://github.com/D3f0/txscada) ya que es el depredador patagónico natural de la Mara.


Estructura básica
-----------------

Ejemplo paquete de comando `0x10`, con destino `01` y origen `40`.

|     | SOF | QTY | DST | SRC | SEC | COM | BCCH | BCCL |
|-----|-----|-----|-----|-----|-----|-----|------|------|
|Valor| FE  | 08  | 01  | 40  | 80  | 10  | 80   | A7   |
|Byte |  0  |  1  |  2  |  3  |  4  |  5  |   6  |  7   |


* *SOF* Start of Frame. Indica que comienza una trama.
* *QTY* Cantidad total de bytes de la trama.
* *DST* Destino 0-64 (fijo en 1 para concentrador).
  El servidor debe entregar una
* *SRC* Origen 0-64 (fijo en 1 para concentrador)
  No se tiene en cuenta en comunicación PtP.
* *SEC* Número de secuencia empieza en `0x20` y termina en `0x7F`.
  El cliente es responsable de avanzar la secuencia. Implica un
  *aknowledge* del mensaje previo *(el servidor puede liberar
    buffer de retransmisión)*
* *COM* Comando
* *BCCH* y *BCCL* parte alta y baja de checksum

Comandos de Mara
----------------

* Puesta en Hora
  * `COM=0x12` y `SEC=0xBB`
  * No tiene respuesta
* Pedido de estados y eventos
  * `COM=0x10`
  * La respuesta responde 4 arreglos
    * Estados
      - SV (varsys)
      - DI
      - AI
    * Eventos
      - Digitales
      - Analógicos


