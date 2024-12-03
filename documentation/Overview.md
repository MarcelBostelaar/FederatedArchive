# Structure

The application is structured into the following parts:
 - config - contains the global configuration for the entire application
 - archive_backend - the root of the application, contains all logic concerning tracking, synching, updating, adding, etc of the archive
 - action_suggestions - contains logic which provides suggestions to the admin on which automated tasks to perform, such as detecting possible alias for authors, file formats, etc