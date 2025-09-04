// This file is part of Invenio.
//
// Copyright (C) 2024-2025 Graz University of Technology.
//
// invenio-workflows-tugraz is free software; you can redistribute it and/or
// modify it under the terms of the MIT License; see LICENSE file for more
// details.


import { expandableStore } from "@js/invenio_catalogue_marc21/utils/expandable";

import { UploadCSV } from "./UploadCSV";

expandableStore.append("InvenioCatalogueMarc21.Manage.Container", UploadCSV);
