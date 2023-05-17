===========
 Changelog
===========

Version 1.0.0
-------------

- Major update to support the Duo Universal Prompt by default
- Adding ``DUO_LEGACY_PROMPT`` setting to fallback to traditional behavior
- Traditional prompt should be considered deprecated and will be removed if Duo ever removes support for it.
- Optional ``FAIL_OPEN`` per-app setting for allowing Duo being unavailable or refusing to authenticate an insecure client to skip second factor
- Per-app settings ``IKEY``, ``SKEY``, and ``HOST``, may now be referred to as ``CLIENT_ID``, ``CLIENT_SECRET``, and ``API_HOSTNAME``, respectively
- ``AKEY`` is no longer used by Universal Prompt


Version 0.1.6
-------------

- Some extra logic ensuring that the user has logged in before Duo logic fires

Version 0.1.5
-------------

- Making an exception for forcing second factor for paths containing ``STATIC_URL``

Version 0.1.4
-------------

- Adding some more logging

Version 0.1.3
-------------

- Added support for username remapping via the ``USERNAME_REMAPPER`` option
  for entries in ``DUO_CONFIG``.

Version 0.1.2
-------------

First public release.
