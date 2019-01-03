# Change Log

# Unreleased

## v2.3.3

### Minor Changes
* Add user and subreddit list exporting options
* Allow importing user and subreddit lists from json and xml files

  * User or subreddit lists that have been exported to json or xml format will contain all information for the associated
reddit object (except for previously downloaded urls).  By doing this, reddit object lists that are exported
to json or xml file types can then be imported at a later date retaining the reddit objects user set attributes (ie: 
last downloaded post date, post limit, media filters, date added, etc.) 

### Bug Fixes
* Restore copy and paste functionality to add reddit object dialog input line





# Released

## v2.3.2

### Minor Changes
* Layout rate limiter structure
  * At this time only the ImgurExtractor is affected by the rate limiter due to user reported errors


## v2.3.1

### Minor Changes
* Update failed to save dialog to give reason when trying to save while downloader is running

### Bug Fixes
* Fix minor logging error in extractor


## v2.3.0

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
* Add imgur credit limit check to avoid additional imgur api calls when out of credits
    * These posts can be saved (see settings) for future download without having to be re-extracted from reddit

### Bug Fixes
* Fix title bar name not changing in last downloaded dialog
* Fix index error when displaying saved content for some reddit objects
* Fix crashes related to resetting date restriction from user/subreddit settings dialog
* Fix imgur credits not updating properly
* Fix gifv extraction
* Fix saved submission display in reddit object settings dialog
* Fix save submissions not being removed from saved list upon download
* Tertiary windows now open in center of main window instead of saved location
* Updated gfycat api caller to new version
* Fix last downloaded dialog error when user or subreddit list has not been set