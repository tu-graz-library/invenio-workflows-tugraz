..
    Copyright (C) 2022 Graz University of Technology.

    invenio-workflows-tugraz is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v0.9.2 (release 2025-05-07)

- fix(theses): misunderstood embargo field


Version v0.9.1 (release 2025-05-01)

- fix: quibbles from ruff 0.8.0
- imoox: convert learningresourcetype
- cleanup: rename filename for consistency


Version v0.9.0 (release 2025-04-30)

- fix(tests): add configuration
- theses: add jobs
- theses: add tests
- fix(thesis): apply change of marc21 datamodel
- fix(thesis): use embargo and 971 for keeping close
- theses: fix caused by new marc21 api
- oer: fix with new marc21 method
- theses: add tests
- oer: fix tests
- setup: add python3.13 support
- setup: reduce MANIFEST.in complexity
- chore: fix ruff error
- change: make it possible to update papers
- refactor: to add oer to alma workflows
- oer: fix small bugs
- oer: mapping lom -> marc21
- oer: oer to alma, initial commit


Version v0.8.2 (release 2025-01-24)

- fix: openaccess convert, structure was wrong
- chore: update ruff configuration
- openaccess: make mark optional
- fix: publisher


Version v0.8.1 (release 2025-01-09)

- fix: handle missing keys


Version v0.8.0 (release 2025-01-08)

- fix: docs reference target not found
- tests: temporary solution
- setup: update ruff configuration
- setup: move dependencies
- openaccess: refactore import function
- fix: delimter needs to be not '-'


Version v0.7.1 (release 2024-07-18)

- theses: add cms_id to error message


Version v0.7.0 (release 2024-07-05)

- workflows: add teachcenter workflow
- setup: move to python3.12 only


Version v0.6.0 (release 2024-05-29)

- add imoox workflow


Version v0.5.3 (release 2024-03-14)

- fix: thesis tasks wrong wording


Version v0.5.2 (release 2024-03-12)

- fix: theses task variable handling


Version v0.5.1 (release 2024-03-01)

- setup: add missing dependency
- theses: fix alembic


Version v0.5.0 (release 2024-02-27)

- fix: due python version not possible to use Self
- theses: add update_access parameter
- setup: move ruff configuration
- theses: make it more fail prove
- thesis: add cli, update models
- theses: improve
- theses: add logic for tasks
- theses: add alembic
- theses: add model to set state
- theses: improve campusonline filter
- theses: change requirement for import


Version v0.4.0 (release 2024-02-02)

- theses: change error to 423
- theses: add endpoint for theses uploads


Version v0.3.2 (release 2024-01-24)

- theses: fix not catched exception


Version v0.3.1 (release 2024-01-07)

- fix: add changed error except
- theses: implement changed requirement for embargo


Version v0.3.0 (release 2023-11-03)

- theses: add implementation for duplicate check
- theses: add check if record has AC number
- theses: change behavior checking file restriction
- theses: pass through the duplicate error message
- ruff: apply new ruff rules


Version v0.2.4 (release 2023-10-20)

- fix: ruff upgrade introduced discrepancy
- fix: 995 subfield notation was wrong
- tests: add test for update_func


Version v0.2.3 (release 2023-06-05)

- theses: revert to simple version


Version v0.2.2 (release 2023-06-05)

- fix: wrong method used to get the record


Version v0.2.1 (release 2023-06-02)

- theses: not only drafts should be updated
- fix: theses update_func api used wrong


Version v0.2.0 (release 2023-05-26)

- fix: use data instead of metadata
- fix: tests
- fix: 971 not used all additions
- theses: rewrite access in update func
- theses: add update_func to the workflow
- theses: add embargo on creation
- theses: remove locked generator
- setup: migrate to ruff


Version v0.1.19 (release 2023-05-17)

- fix: apply requested changes for field 008


Version v0.1.18 (release 2023-05-12)

- fix: position 19 was the wrong value
- fix: keyw was not processed
- theses: change visitor api
- theses: implement sorting for 971 fields
- fix: revert back change of 007 field
- fix: 245 field missed author


Version v0.1.17 (release 2023-05-11)

- fix: errors


Version v0.1.16 (release 2023-05-11)

- fix: int not serializable


Version v0.1.15 (release 2023-05-11)

- theses: fix german language code


Version v0.1.14 (release 2023-05-11)




Version v0.1.13 (release 2023-05-10)

- theses: apply requested marc21 field changes
- fix: date for status


Version v0.1.12 (release 2023-05-10)

- fix: the crap from last commit


Version v0.1.11 (release 2023-05-10)

- fix: date and format where not compatible


Version v0.1.10 (release 2023-05-10)

- fix: used wrong date format


Version v0.1.9 (release 2023-05-10)

- theses: apply marc21 request changes


Version v0.1.8 (release 2023-04-25)

- theses: add necessary need to import


Version v0.1.7 (release 2023-01-26)

- theses: change alma import size
- theses: change import start date


Version v0.1.6 (release 2023-01-23)

- modification: create an endpoint for theses records


Version v0.1.5 (release 2023-01-23)

- fix: return value of import_func
- fix: wrong alias name


Version v0.1.4 (release 2023-01-20)

- theses fix: play safe with real data


Version v0.1.3 (release 2023-01-20)

- theses: mapping change


Version v0.1.2 (release 2023-01-20)

- fix: remove print


Version v0.1.1 (release 2023-01-18)

- theses: convert abstract and keywords


Version v0.1.0 (release 2023-01-18)




