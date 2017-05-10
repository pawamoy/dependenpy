=========
Changelog
=========

3.0.0 (2017-05-??)
==================

This version is a big refactor. The code is way more object oriented,
cleaner, shorter, simpler, smarter, more user friendly- in short: better.

Some of the previous features are still not fully implemented.

The usage stays about the same, in two steps:

- the initialisation of a ``DSM`` object (the package structure),
- the generation of dependency data (parsing the code thanks to ``ast``).

Additional features:

- command line entry point (wip)
- serializers for JSON, CSV, YAML, human/editor-readable text (wip)
- runtime static imports are now caught (in functions or classes),
  as well as import statements (previously only from import).

2.0.3 (2017-04-20)
==================

* Fix occasional UnicodeEncode when reading UTF-8 file.
* Handle bad characters in files when parsing with ``ast``.

0.1.0 to 2.0.2 (2016-10-06)
===========================

* Development (alpha then beta version).

0.1.0 (2016-10-06)
==================

* Alpha release on PyPI.
