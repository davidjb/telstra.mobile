TODO
====

* Add context manager support into underlying modem library
   -- add this support to the prepaid account library too (proxy it)
   -- with Modem('/dev/ttyUSB0') as modem:
      (__enter__ connects)
      (__exit__ disconnects, closes, etc)
* Decide on a consistent way of closing out USSD sessions
* ? - Cache main menu results
* More robust syntax checking
* Command line scripts & entry points
* Unit tests
