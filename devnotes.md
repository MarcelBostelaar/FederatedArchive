# Dependencies
?pydantic
djangorestframework
markdown
django-filter
faker
django-q2
django-cleanup
?django-model-utils
(incomplete)

# TODO
- [x] rework edition revision and autogen signals (documentation as well) based on the activity diagrams
- [x] Map out signals for when items get created
- [x] Move example plugin to its own app
- [x] Add original filename back to archive file item
- [x] Fix file format logic in generator runner
- [x] Add status remoterequestable
- [x] Test all signals
- [x] revise generation config somehow, since it now only does one file format to the next
- [x] Implement 1 dummy generation functionality
- [x] Implement api
- [x] Implement download jobs
  - [x] Check that scheduled remote jobs are finished when syncing
- [x] Add special endpoint for adding a remote (you need its id)
- [x] Implement urllib.parse (function quote) to the url args
- [x] Do not expose unfinished revisions (or their files) in api
- [x] Automatically add scheduled rechecking of remotes if it doesnt exist in the job queue
- [x] Test if you can individually request an unfinished revision
- [x] Remove transition metadata code
- [x] Prevent adding 2 is this sites
- [x] Simplify jobify by getting callsign automatically

## MVP frontend
- [ ] Overview by author (aliased and additional author)
- [ ] Overview by abstract document (with indicator of status)
- [ ] Show other editions, by language, on document page
- [ ] Overview of edition files
- [ ] Button to request a requestable

## Additional features backend
- [x] Persistent ID for files that link up different versions of a file
  - [ ] Change example generator to correctly add the persistent ids to the correct files.


## Not MVP
- [ ] Diff view for text files
- [ ] Add to fileformat if its a text format
- [ ] Job to recheck everything in db (for what exactly?)
- [ ] periodically check remotes
- [ ] Add hash to files + revision for validating nothing in the remote was changed secretly

## Frontend
- [ ] abstract document, edition, revision and file need to get their own human readable autogenerated name, not synched, which is where the items are served from, in addition to a uuid based lookup which returns the same files for the api
- [ ] extra table outside main app for redirecting old urls to new editions/files


# Old Roadmap

## Backend
- [x] Basic archive system, with multiple editions per archival ID (book, publication, etc)
- [x] Mirror and federation functionality
- [ ] Milestone versioning system
- [ ] Plugin system for automatically generating other formats from existing formats
- [x] ~~Rectify/unify authors~~
- [x] ~~Rectify/unify documents~~
- [x] Generic alias system
- [ ] Simple user system?
- [ ] Docker setup

### Future features
- [ ] User submissions
- [ ] git version control for individual git editions?
- [ ] Pull request-analogue system?
- [ ] Semantically driven rectification of authors/documents/etc

## Frontend

- [ ] Basic search by author and title
- [ ] Document info pages

### Future features
- [ ] Document search

## Admin
- [ ] Rectify/unify authors
- [ ] Rectify/unify documents
- [ ] Simple user system?
- [ ] Fork/copy functionality