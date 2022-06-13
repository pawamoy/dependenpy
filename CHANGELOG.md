# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [3.3.1](https://github.com/pawamoy/dependenpy/releases/tag/3.3.1) - 2022-06-13

<small>[Compare with 3.3.0](https://github.com/pawamoy/dependenpy/compare/3.3.0...3.3.1)</small>

### Bug Fixes
- Handle the case where all modules names are shorter than the header when printing a matrix ([1d83b17](https://github.com/pawamoy/dependenpy/commit/1d83b17612cdf5ab16c27668bd241d64dd872e5c) by Vlad Dumitrescu). [PR #48](https://github.com/pawamoy/dependenpy/pull/48)


## [3.3.0](https://github.com/pawamoy/dependenpy/releases/tag/3.3.0) - 2020-09-04

<small>[Compare with 3.2.0](https://github.com/pawamoy/dependenpy/compare/3.2.0...3.3.0)</small>

### Code Refactoring
- Poetrize the project ([811c3fb](https://github.com/pawamoy/dependenpy/commit/811c3fb7271d6474a58f5b800bef5c220be3b8f6) by Timothée Mazzucotelli).

### Features
- Add 'zero' argument to change character for 0 ([1c13c00](https://github.com/pawamoy/dependenpy/commit/1c13c000685466f46ad8c6f7ac30534a6efe9373) by Timothée Mazzucotelli).
- Update archan provider for archan 3.0 ([9249dc1](https://github.com/pawamoy/dependenpy/commit/9249dc161e9fdd64e15a42f644232c43cb6875b2) by Timothée Mazzucotelli).


## [3.2.0](https://github.com/pawamoy/dependenpy/releases/tag/3.2.0) - 2017-06-27

<small>[Compare with 3.1.0](https://github.com/pawamoy/dependenpy/compare/3.1.0...3.2.0)</small>

### Features
- Add graph option ([1ebc8f6](https://github.com/pawamoy/dependenpy/commit/1ebc8f6d12cc5ceb0dcbbfd240c96bcbfa6f867e)).
- Implement archan provider ([66edb5b](https://github.com/pawamoy/dependenpy/commit/66edb5be54544af78476514494c85dac84205f2b)).


## [3.1.0](https://github.com/pawamoy/dependenpy/releases/tag/3.1.0) - 2017-06-02

<small>[Compare with 3.0.0](https://github.com/pawamoy/dependenpy/compare/3.0.0...3.1.0)</small>

### Features
- Add `-i, --indent` option to specify indentation level.

### Changes
- Change `-i, --enforce-init` option to its contrary `-g, --greedy`.
- Options `-l`, `-m` and `-t` are now mutually exclusive.

### Bug fixes
- Fix imports order ([9a9fcc3](https://github.com/pawamoy/dependenpy/commit/9a9fcc33c258a89eafcbf6995bebc64fccb85d54)).
- Fix matrix build for depth=0 ([955cc21](https://github.com/pawamoy/dependenpy/commit/955cc210d6acf5dc83e39b41edbf26b95b09d7b0)).

### Misc
- Improve cli tool and print methods, 


## [3.0.0](https://github.com/pawamoy/dependenpy/releases/tag/3.0.0) - 2017-05-22

<small>[Compare with 2.0.3](https://github.com/pawamoy/dependenpy/compare/2.0.3...3.0.0)</small>

This version is a big refactoring. The code is way more object oriented,
cleaner, shorter, simpler, smarter, more user friendly- in short: better.

Additional features:

- command line entry point,
- runtime static imports are now caught (in functions or classes),
  as well as import statements (previously only from import).
  

## [2.0.3](https://github.com/pawamoy/dependenpy/releases/tag/2.0.3) - 2017-04-20

<small>[Compare with 2.0.2](https://github.com/pawamoy/dependenpy/compare/2.0.2...2.0.3)</small>

### Changes
- Change license from MPL 2.0 to ISC ([35400bf](https://github.com/pawamoy/dependenpy/commit/35400bf755c40e88a0e2bd9bd7a21b96194b0e1b)).

### Bug fixes
- Fix occasional UnicodeEncode when reading utf8 file ([333e987](https://github.com/pawamoy/dependenpy/commit/333e98710d80976196367fb6fc2ed8f82313d117)).
- Handle bad characters in files when parsing with ast ([200e014](https://github.com/pawamoy/dependenpy/commit/200e0147cc44fcd80c9b53115f63405107e2bfd3)).


## [2.0.2](https://github.com/pawamoy/dependenpy/releases/tag/2.0.2) - 2016-10-06

<small>[Compare with 1.0.4](https://github.com/pawamoy/dependenpy/compare/1.0.4...2.0.2)</small>

- Split code in two projects: dependenpy and archan.
- Update to use Python 3.
- Various bug fixes, additions, improvements and refactor.

## [1.0.4](https://github.com/pawamoy/dependenpy/releases/tag/1.0.4) - 2015-03-05

<small>[Compare with 1.0.3](https://github.com/pawamoy/dependenpy/compare/1.0.3...1.0.4)</small>

Documentation and tests improvements.


## [1.0.3](https://github.com/pawamoy/dependenpy/releases/tag/1.0.3) - 2015-02-26

<small>[Compare with 1.0.2](https://github.com/pawamoy/dependenpy/compare/1.0.2...1.0.3)</small>

### Bug fixes
- Add check for target_index not None ([d3e573f](https://github.com/pawamoy/dependenpy/commit/d3e573fcbc79957bc19dada4359663adb48a0a81)).


## [1.0.2](https://github.com/pawamoy/dependenpy/releases/tag/1.0.2) - 2015-02-24

<small>[Compare with 1.0.1](https://github.com/pawamoy/dependenpy/compare/1.0.1...1.0.2)</small>

### Features
- Added CSV export ([ce8a911](https://github.com/pawamoy/dependenpy/commit/ce8a91130e20e57208d45a93c83dfc47565c16e4)).

### Bug fixes
- Fix get_matrix if str instead of int, fix csv write row (extend return None) ([bb1289d](https://github.com/pawamoy/dependenpy/commit/bb1289dc2c035f6f25fd6ab5cb29aa776f5d6bc6)).


## [1.0.1](https://github.com/pawamoy/dependenpy/releases/tag/1.0.1) - 2015-02-23

<small>[Compare with 1.0](https://github.com/pawamoy/dependenpy/compare/1.0...1.0.1)</small>

### Bug fixes
- Fix hashable for dict ([7d221db](https://github.com/pawamoy/dependenpy/commit/7d221db07766f41d942c947f621286e21ad17b48)).
- Fix path resolver ([4e8a192](https://github.com/pawamoy/dependenpy/commit/4e8a19211648255365477a8b6d83d538463f8488)).


## [1.0](https://github.com/pawamoy/dependenpy/releases/tag/1.0) - 2015-02-23

<small>[Compare with 0.2-beta](https://github.com/pawamoy/dependenpy/compare/0.2-beta...1.0)</small>

## Code refactoring

- [4bd14d9](https://github.com/pawamoy/dependenpy/commit/4bd14d92d842b173b2456c3ff0083b84960545ad)
- [15ba1e5](https://github.com/pawamoy/dependenpy/commit/15ba1e54700896abdaccc3fefcdc261d73be1368)
- [12fa604](https://github.com/pawamoy/dependenpy/commit/12fa60444a83c11644026270c1df37eddaecc2c8)


## [0.2-beta](https://github.com/pawamoy/dependenpy/releases/tag/0.2-beta) - 2015-02-20

<small>[Compare with first commit](https://github.com/pawamoy/dependenpy/compare/1ed68a25fb858a9da721a4cd3ab24fcc5f5e08a5...0.2-beta)</small>

First release.
