=========
Changelog
=========

3.2.0 (2017-06-27)
==================

- Change ``-g`` short option for ``--greedy`` to ``-G``.
- Add ``-g, --show-graph`` option with related graph class and capabilities.
- Add a provider for Archan (``dependenpy.plugins.InternalDependencies``).
- Update documentation accordingly.

3.1.0 (2017-06-02)
==================

- Change ``-i, --enforce-init`` option to its contrary ``-g, --greedy``.
- Add ``-i, --indent`` option to specify indentation level.
- Options ``-l``, ``-m`` and ``-t`` are now mutually exclusive.
- Fix matrix build for depth 0.
- Print methods have been improved.
- Update documentation.

3.0.0 (2017-05-23)
==================

This version is a big refactoring. The code is way more object oriented,
cleaner, shorter, simpler, smarter, more user friendly- in short: better.

Additional features:

- command line entry point,
- runtime static imports are now caught (in functions or classes),
  as well as import statements (previously only from import).

2.0.3 (2017-04-20)
==================

- Fix occasional UnicodeEncode when reading UTF-8 file.
- Handle bad characters in files when parsing with ``ast``.

0.1.0 to 2.0.2 (2016-10-06)
===========================

- Development (alpha then beta version).

0.1.0 (2016-10-06)
==================

- Alpha release on PyPI.
