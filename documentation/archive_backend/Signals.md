# Signals
## RemotePeer
 - mirror_files on change
     - If from false to true -> launch job to start import process

## FileFormat
 - Nothing

## Language
 - Nothing

## Author
 - Nothing

## Author description translation
 - Nothing

## Abstract document
 - Nothing

## Abstract document description translation
 - Nothing

## Edition
 - See activity diagram below

![see "edition revision generation activity diagram"](./Edition%20Revision%20Generation%20activity%20diagram.drawio.png)

 - On existance type change, see table below

|  to\from        | Local                       | Generated                           | Remote                 | Mirroredremote                |
|-----------------|----------------------------|-----------------------------------------|-------------------------|-------------------------------|
| Local           | ✔                          | Integrity: Remove corresponsing generation config and parent edition| ❌                     | ❌                            |
| Generated   | See activity diagram | ✔                                      | ❌                 | ❌                           |
| Remote          | ❌                         | ❌                                     | ✔                       | ✔    |
| Mirroredremote  | ❌                         | ❌                                     | Request revision | ✔                            |

## Revision
 - On status change any->ondisk: TODO
    - Clean non-milestone versions when a newer version is added
    - Queue generation jobs dependents ![see "edition revision generation activity diagram"](./Edition%20Revision%20Generation%20activity%20diagram.drawio.png)

## File
 - Nothing

## GenerationConfig
 - On change: For each edition using it, CGR ![see "edition revision generation activity diagram"](./Edition%20Revision%20Generation%20activity%20diagram.drawio.png)
