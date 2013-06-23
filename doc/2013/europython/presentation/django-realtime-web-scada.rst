Designing a Real Time Control System based on Django, ZMQ and WebSockets
========================================================================


----

About the problem
=================

Our goal is to build a low-cost microcontroller network and
a SCADA system on top of it for monitoring (and control).

Some requriements::

    - Time resolution of 10mS
    - Hierachical data structure
    - Web Interfase


------

SCADA Software
==============


SCADA software monitors and controls industrial processes. They provide an "nice"
UI overview of the process and allow to interect with dedicated hardware (PLC, RTU, IED, etc)

----

Power distribution
==================

.. image:: img/power_station.png



----

Is Python suited for this kind of enviroments?
==============================================

At first Python was seen as a very high level language, in an enviroment where
C and specific assembler where predominant.



----


Why Django
==========


- Settings (with logging)
- Commands
- Easy to learn ORM (with Signals)


Presenter Note
--------------

    This is a note



