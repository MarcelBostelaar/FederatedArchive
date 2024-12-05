# Signals
## RemotePeer
 - On mirror_files change or new remote peer:
   - Schedule downloading and updating of everything.
     - Other signals will take care of proper revision/file syncing

## Edition
 - New:
   - Local: Create new empty on disk revision*
   - Generated: Handled by activity diagram logic
   - Remote: Schedule sync job*
   - Mirrored-remote: Schedule sync job*
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
    ![see "edition revision generation activity diagram"](./Edition%20Revision%20Generation%20activity%20diagram.drawio.png)

## GenerationConfig
 - On change: For each edition using it, CGR ![see "edition revision generation activity diagram"](./Edition%20Revision%20Generation%20activity%20diagram.drawio.png)

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

## FileFormat
 - Nothing

## File
- Nothing