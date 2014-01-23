cpview
======
a simple codepoint viewer app using PyQt
----------------------------------------

This program is written based on Py3 and PyQt4's different behaviour (esp. w.r.t. strings) when used with Py3. It may require some tweaking to be used with Py2.

Also note that as of latest version (3.3.3), Python's unicodedata module only provides the name() function which returns only the immutable primary character name. This is not always the most useful name such as in the case of naming errors etc. When Python's unicodedata module is upgraded to provide a usefulname() function, this program should use that.
