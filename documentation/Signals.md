
## Signals
### RemotePeer
 - mirror_files on change
     - If from false to true -> launch job to start import process
     - If from true to false -> add delete option to suggestions.
 - last_checkin periodic lookup, configurable

### FileFormat
 - Aliasable
 - On change
    - Auto alias/signal possible alias when identical fileformat name (strip dots)

### Language
 - Aliasable
 - On change
    - Auto alias/signal possible alias when identical iso code

### Author
 - Aliasable
 - On change
    - Auto alias/signal possible alias when identical fallback_name, if both have birthdays, identical birthdays

### Author description translation
 - Nothing

### Abstract document
 - On change
    - Auto alias/signal possible alias when identical original publication date, at least one shared (aliased author)

### Abstract document description translation
 - Nothing

### Edition
 - On existance type change

|  to\from        | Local         | Autogenerated                           | Remote                     | Mirroredremote                |
|-----------------|---------------|-----------------------------------------|----------------------------|-------------------------------|
| Local           | ✔             | Copy all revisions into local versions  | Make job to copy locally   | Make job to copy locally     |
| Autogenerated   | ❌            | ✔                                      | ❌                         | ❌                           |
| Remote          | ❌            | ❌                                     | ✔                          | add job to clean local files |
| Mirroredremote  | ❌            | ❌                                     | Make job to copy locally    | ✔                            |


### Revision
 - TODO: Add milestone revision option (prevents deletions downstream)
 - On adding: 
    - Clean non-milestone versions when a newer version is added
    - Launch autogeneration

### File
 - On delete: clean function

### AutoGenerationConfig
 - Nothing
 - On change: Add suggestion to add job "regenerate all" (if any exist using this config)

### AutoGeneration
 - On addition: add generation job