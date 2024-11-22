# Requirements

## Needed signals/features
### RemotePeer
 - mirror_files change
 - last_checkin periodic lookup, configurable

### FileFormat
 - Aliasable
 - Auto alias/signal possible alias when identical fileformat name (strip dots)

### Language
 - Aliasable
 - Auto alias/signal possible alias when identical iso code

### Author
 - Aliasable
 - Auto alias/signal possible alias when identical fallback_name, if both have birthdays, identical birthdays

### Author description translation
 - Nothing

### Abstract document
 - Auto alias/signal possible alias when identical original publication date, at least one shared (aliased author)

### Abstract document description translation
 - Nothing

### Edition
 - On existance type change

### Revision
 - Add milestone revision option (prevents deletions downstream)
 - Clean non-milestone versions when a newer version is added
 - Launch autogeneration on addition

### File
 - Implement clean function on delete

### AutoGenerationConfig
 - Nothing
 - "regenerate all" option for when someone changes it

### AutoGeneration
 - Launch generation on addition
