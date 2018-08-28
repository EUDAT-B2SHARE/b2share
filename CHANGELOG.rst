B2Share changelog
*****************

2.1.2 (end of August 2018)
===========================

Changes since 2.1.1 include:

- more (developer oriented) documentation
- bug fixes


2.1.1 (end of February)
===========================

Changes since 2.1.0 include:

- support external files, specified by PID, including B2SAFE files
- support latest version of b2drop/nextcloud
- bug fixes


2.1.0 (mid November)
===========================

Changes since 2.0.1 include:

- record versioning!
- the new upgrade command, automatically executed on start
- file statistics module and UI integration
- file checksum verification
- configuration options for B2NOTE integration
- compatibility with the handle system API (via b2handle)
- latest versions of Invenio packages
- record deletion (HTTP API, superadmin only)
- improved error messages
- various UI fixes
- documentation improvements


2.0.1 (released 2017-04-29)
===========================

Patch update. Changes since 2.0.0 include:

- added the community membership administration page
- fix UI editing metadata bug
- fix incorrect config check
- fix missing location when demo not loaded
- improve cli command for checking DOI allocation
- improve Docker demo config
- fix incorrect docs link
- added more tests


2.0.0 (released 2017-02-28)
===========================

First stable release of B2Share 2.0.0.

Changes since 1.7.0 include:

- B2Share 2.0.0 is now based on Invenio version 3.
- a new User Interface.
- a new REST API.
- a new command line interface.
- a new datamodel based on JSON and JSON-Schemas.
- a new Docker deployment for demonstration.
- Postgresql support.

See documentation for more information.


2.0.0rc13
=========

- allow record owners and community administrators to edit metadata of published records
- add OAI-PMH sets and a CLI command for syncing the sets with the communities
- add PID and DOI in the MarcXML OAI-PMH output
- add link to own drafts in the Profile page
- add administration docs
- various bugfixes
