## 0.6.0

This is the first version of django-forge that provides v3 API support and
uses the v3 API when syncing with another Forge.

The support for v1 has been greatly improved, including better dependency
calculation and bug fixes for Puppet Labs' shorthand semantic version
ranges (e.g. `1.2.x`).

## 0.5.1 (April 4, 2014)

Fixed a bug where incorrect dependencies would be sent when a semantic
version specifier wasn't given in a module dependency.
