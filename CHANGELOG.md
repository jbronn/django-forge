## 0.6.0 (June 4, 2014)

This is the first version of django-forge that provides v3 API support.

The `mirror_forge` command has been removed; the `sync_forge` command
replaces it, and uses the v3 API to synchronize with Puppet Labs.

The support for v1 has been greatly improved, including better dependency
calculation and bug fixes for Puppet Labs' shorthand semantic version
ranges (e.g. `1.2.x`).

The `forge.settings` module will no longer work directly, please use
`forge.settings.dev` or `forge.settings.prod`, depending on your needs.

## 0.5.1 (April 4, 2014)

Fixed a bug where incorrect dependencies would be sent when a semantic
version specifier wasn't given in a module dependency.
