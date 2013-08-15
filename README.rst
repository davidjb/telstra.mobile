Telstra Prepaid module for Python
=================================

A potentially vain attempt at creating an API to interact with some of
Telstra's services for Prepaid Mobile.  Other services can be added later
into the top-level ``telstra.`` namespace, potentially by other developers. 

telstra.mobile
--------------

In particular, this aims to provide an initial interface
with Telstra Prepaid's USSD (Unstructured Supplementary Service Data). You
may also know this as the ``#100#`` or ``#125#`` service.  This library
provides a Python-based API that can communicate with these services
via a connected cellular modem.

Requirements
------------

* USB or serial-based cellular modem that works with `python-gsmmodem
  <https://github.com/faucamp/python-gsmmodem>`_.  A USB 3G dongle or stick
  like the ZTE 3571-Z works fantastically for all known functionality.
* Telstra Prepaid SIM card

Install
-------

#. Obtain materials, insert SIM into modem, connect modem to computer.
#. Ensure you can communicate with your modem via its serial port, for 
   example by using Hyperterminal (Windows), or ``screen`` or ``cu`` (Linux).
   This may require driver installation. 
#. Install this library.  All dependencies will automatically be satisfied.

   pip install telstra.mobile

#. Start using this library by telling the 

Useful links
------------

* https://github.com/smn/txgsm/blob/develop/txgsm/txgsm.py

* http://pyserial.sourceforge.net/shortintro.html#readline

* http://www.cyberciti.biz/hardware/5-linux-unix-commands-for-connecting-to-the-serial-console/
