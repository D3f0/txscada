Designing a Real Time Control System based on Django, ZMQ and WebSockets
========================================================================


----

$ whoami
========


    - Python advocate for +6 years
    - Teacher at **Univerisdad Nacional de la Patagonia**
    - Devop at **Machinalis**


.. image:: img/logos.svg


----

The SMVE project
================

This talk will cover the SVME project, an attemp to build
an UI (HMI) for a Power Substation monitoring system using HTML5 (SVG, WebSockets)
and Python!

We de

----


Power distribution
==================

.. image:: img/power_station.png



----

HMI
===

.. image:: img/hmi.jpg


----


Where do data come from?
========================

.. image:: img/explorer16.jpg

----



Measurement
============

.. image:: img/alpha2.jpg


-----

IEDs
====

Power station have already **their** measurement equipment,
so you've got to figure out how to take talk to them.
Some devices can do **optical**, others **RS485**, but generally They are only capable of **one-to-one communication**.


So we built an interfase to poll every device in a network
under Mara, and we called it **IED**.

.. image:: img/ied.svg


----

IED Network
===========

IEDs are built with very basic hardware, they have limited
memory and they communicate through Mara over RS485. They
measure **digital inputs**, **analog input** and **events**.

To take data out of these devices we need some kind of
gateway.


----

Concentratos
============

A Cocentrator is an IED with larger computing power
and Ethernet port, so it can talk Mara/485 with the
IED network and Mara/TCP-IP to the computer.

.. image:: img/comaster.svg


----

Concentrators also...
=====================

* Poll every IED connnected to it and store its **AI**, **DI**, **Events** in
  internal tables (data buffering).
* Synchronize their clock (from the PC or from external GPS)
* Gateway TCP-IP/485 for direct access to IEDs (i.e. PC broadcast).
* System status variables
* Communication status variables


-----

SCADA Deamon
============

The SCADA deamon polls every concentrator over TCP/IP.

It talks to the concentrators using **Twisted** for protocol management
and **Construct** for dict to stream/stream to bits conversion.

It talks to the database through **Django models**.

It's implemented as a **django management command**.


----

How do I run it?
================


        .. code-block:: bash

            python manage.py poll

.. image:: img/basic.svg


----

But how do we do it?
====================


----

Frames
======

Mara protocol is byte/word oriented. It defines 6 bytes for header and 2 for checksum.
Some payloads have bit fields

.. image:: img/frame.svg
    :scale: 50



----


.. image:: img/construct-logo2.png

Let us define Mara frame as follows:

.. sourcecode:: python2

    MaraFrame = BaseMaraStruct('Mara',
            ULInt8('sof'),
            ULInt8('length'),
            ULInt8('dest'),
            ULInt8('source'),
            ULInt8('sequence'),
            ULInt8('command'),
            Optional(Payload_10),
            ULInt16('bcc')
    )



----


Showing the data in the web
===========================


----

Diagrams
========

SVG



------

SCADA Software
==============


SCADA software monitors and controls industrial processes. They provide an "nice"
UI overview of the process and allow to interect with dedicated hardware (PLC, RTU, IED, etc)

----




----

Python really?
==============================================

At first Python was seen as a very high level language, in an enviroment where
C and specific assembler where predominant.



----

We were not the first!
======================

.. image:: img/book.jpg



----

Why Django
==========


- Settings (with logging)
- Commands
- Easy to learn ORM (with Signals)



----

Questions?
==========

----

Contact
=======

Nahuel Defossé

@D3f0

nahuel.defosse (at) gmail (dot) com
