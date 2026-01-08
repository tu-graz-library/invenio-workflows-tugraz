..
    Copyright (C) 2026 Graz University of Technology.

    invenio-workflows-tugraz is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

=========
PUBLISHER
=========

CSV upload
==========

csv file has to have following columns::

  "id","doi","filename","title","year","authors"

steps to use csv import.

- got to url `/catalogue/uploads/new`
- fill in necessary fields
- save draft
- reload page
- upload csv + zip file with `Upload Files`
- save draft
- open `Upload CSV`
- start process by clicking `Start Process`
- wait some time
- close popup
- reload page
- check if all articles have been added

to publish the records.

- on the root element click publish
- (2) navigate back `/publications/uploads`
- click edit on the root element of the proceeding
- click on the article you want to publish
- click publish
- back to step (2)

Problems
--------

- the publishing part has to be optimized. at the moment it takes to long,
  because every article has to be published by hand.

- some steps on the import workflow will be removed from the list, because they
  should be handled by the feature itself


