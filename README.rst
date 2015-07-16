Telstra Mobile API for Python
=============================

.. contents::

A potentially vain attempt at creating an API to interact with some of
Telstra's services for mobile.  At present, this library handles:

* Majority of key functionality for USSD via hardware modem
* Some web-based prepaid account interrogation

Other Telstra services can be added later into the top-level ``telstra.``
namespace, potentially by other developers.

Quickstart
----------

Install this library with ``pip install telstra.mobile``, make sure
you have a supported 3G modem plugged in with a Telstra SIM card
installed. See Install_ section later for full details.

An example is worth a thousand words, so let's just jump straight into
it.

.. code:: python

    from telstra.mobile import autodetect_account
    
    # detect first available account
    account = autodetect_account()  
    # detect specific phone number
    account = autodetect_account('0412345678')  

    # Detected via the network
    account.phone_number

    # Access a session to #100#
    ussd = account.main_menu()

    # So something wacky manually
    ussd = account.modem.sendUssd('#100*2*2#')

This provides an interface with Telstra's USSD (Unstructured Supplementary
Service Data) services. You may also know this as the ``#100#`` or ``#125#``
service.

So, now, you have an ``account`` that gives you access to common cellular
commands that you'd normally be able to manually perform with USSD. A variety
of operations are automated, such as balance & expiry checking.

This library allows auto-detection either without a phone number, being
the first available physical modem that responds, or with a phone number, and
the modem/account must conform to the given number.

If you're already got a pre-existing `python-gsmmodem`_ modem instance
available to you, then you can re-use this by passing it directly during
manual initialisation of an account.

.. code:: python

    from telstra.mobile import Prepaid
    modem = ... #pre-existing python-gsmmodem instance
    prepaid = Prepaid(modem)

Features
--------

This library provides a Python-based API that can communicate with these
services via a connected cellular modem.  So, you can easily auto-detect an
account (and modem) based upon the underlying account's phone number. This,
whilst helpful, is entirely Telstra specific.

The initital implementation features an API for working with Telstra Prepaid,
as this is what I can test against primarily.  To a lesser extent, I have
been able to abstract some parts of the code to work with Telstra Postpaid
as well.

Requirements
------------

* USB or serial-based cellular modem that works with `python-gsmmodem
  <https://github.com/faucamp/python-gsmmodem>`_.  A USB 3G dongle or stick
  like the ZTE 3571-Z works fantastically for all known functionality.
* Telstra SIM card, prepaid or postpaid

Install
-------

#. Obtain materials, insert SIM into modem, connect modem to computer.

#. Ensure you can communicate with your modem via its serial port, for 
   example by using Hyperterminal (Windows), or ``screen`` or ``cu`` (Linux).
   This may require driver installation.  

#. Install this library.  All dependencies will automatically be satisfied::

       pip install telstra.mobile

   or, if you like `Buildout <http://buildout.org>`_::

       [buildout]
       parts = telstra

       [telstra]
       receipe = zc.recipe.egg
       eggs = telstra.mobile
       interpreter = py

#. Start using this library. The recommendation is to use the autodetection
   functionality, as this will automatically find the correct serial port
   to connect to. See `Quickstart`_ above.


Scripts
-------

* ``bin/send-credit`` - sends credit to a nominated Telstra prepaid phone number by utilising
  the relevant USSD menus and options. This script can automatically run based
  on a number of conditions when called (such as target account balance and
  expiry).


Useful links
------------

* http://pyserial.sourceforge.net/shortintro.html#readline

* http://www.cyberciti.biz/hardware/5-linux-unix-commands-for-connecting-to-the-serial-console/

* https://github.com/smn/txgsm/blob/develop/txgsm/txgsm.py
