# Change Log

## Unreleased


## V2.3.0

### Major Changes
* Add youtube-dl video download support (any site that can be downloaded by the youtube-dl project can now be downloaded
from reddit by this downloader)
* Massively update the failed downloads dialog
* Add ability to export failed downloads in multiple formats
* Add new extractor for reddituploads
* Add ability to exclude a user/subreddit from download without removing them from the download list
* Massively update the add user/subreddit dialog
  * Dialog now handles importing from text file or sub folders instead of main window
  * List copy and paste now supported

### Minor Changes

### Bug Fixes
* Fix title bar name not changing in last downloaded dialog
* Fix index error when displaying saved content for some reddit objects
* Fix crashes related to resetting date restriction from user/subreddit settings dialog
* Fix imgur credits not updating properly
* Fix gifv extraction
* Fix saved submission display in reddit object settings dialog
* Fix save submissions not being removed from saved list upon download