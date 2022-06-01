# Change Log


## v3.14.1

### Bug Fixes
* Fix crashing due to error responses when trying to connect to a reddit account.


## v3.14.0

### Minor Changes
* Improve look of main UI window.
* Improve look of settings window, and make some supporting text more clear.

### Bug Fixes
* Fix problems with scheduling.


## v3.13.2

### Bug Fixes
* Fix extraction errors for erome hosted content.


## v3.13.1

### Bug Fixes
* Fix crashing that occurred when attempting a json export failed content list from database dialog.


## v3.13.0

### We are out of beta!

### Minor Changes
* Update PRAW version.


### Bug Fixes
* Fix crashing that rarely occurred when PRAW failed to connect to reddit with a RequestException.


## v3.12.1-beta

### Bug Fixes
* Fix the application was being falsely flagged as a trojan by some anti-virus software.


## v3.12.0-beta

### Minor Changes
* Add a single command line option to locate all files created by the app in one directory.  This essentially makes the
  app portable when used.


### Bug Fixes
* Fix "--data" command line argument not locating database and log file in the specified directory with the config file.


## v3.11.0-beta

### Minor Changes
* Greatly improve user account pairing OAuth flow.  There is no longer any need for the user to manually copy and paste
  information between the browser and the app.


## v3.10.3-beta
* Fix crashing and unexpected behavior when deleting posts, content, or files from the database dialog.


## v3.10.2-beta
* Update youtube-dl and add supported site url for youtu.be.


## v3.10.1-beta

### Bug Fixes
* Fix crash that sometimes happens when checking for authorized connection status.


## v3.10.0-beta

### Minor Changes
* Users can now link their reddit accounts with the application.  This should relieve some of the slow download times
that users have been experiencing in recent weeks.
  * To connect, use the connect reddit account wizard accessed from the file menu.


## v3.9.0-beta

### Minor Changes
* Users now have the option to sync download settings when moving users/subreddits between lists.

### Bug Fixes
* Fix problems in downloading from gfycat/redgifs.
* Fix crashing from csv importer/exporter.


## v3.8.0-beta

### Minor Changes
* Users are now notified if they are adding a user/subreddit that already exists in another list, and are asked how 
  they would like to proceed.
* Add ability to set custom save paths for downloaded posts and comments that override the global base save directories.  
  Can be set in the user/subreddit settings dialog for each user/subreddit.
* Add status tray icon with download options and notifications.
  
### Bug Fixes
* Fix crashing when right clicking on empty user/subreddit fields.
* Fix various download scheduling errors


## v3.7.0-beta

### Minor Changes
* Invalid or deleted users/subreddits are now handled all at once at the end of a download session instead of in their
own individual dialogs.
* Add context menu option for moving and copying users/subreddits from one list to another.
* Add ability to remove multiple users/subreddits from a list at a time.


## v3.6.0-beta

### Minor Changes
* Add command line arguments for ability to specify application data directory as well as user and subreddit download
directories before the application starts.
* Multiple user/subreddit names can now be added in one line in the add user/subreddit dialog.  Names are separated by
either a comma or a newline character.  This enables names to be copy and pasted into the multi-add input and added
all at once.

### Bug Fixes
* Fix user/subreddit count label in add dialog when importing from file.
* Fix list syncing errors when adding users/subreddits that may already be in the database, but not included on any
download lists.
  * Ex: A subreddit download is performed and a post is downloaded where the author is User-A.  Later, User-A is added 
  to a user list for download.  User-A's download settings will now be synced with the user list they have now been 
  added to, even though they were previously in the database with default settings.
* Fix ability to delete multiple users/subreddits at the same time.
* Fix audio downloads for reddit hosted videos.



## v3.5.0-beta

### Minor Changes
* Make date display format user adjustable.

### Bug Fixes
* Fix being able to sort user submissions by "rising', which is not a valid sort method for users.
* Fix some date display formats creating extra folders.
* Fix crashing when trying to remove a user/subreddit list when there are none available
* Fix errors when importing users/subreddit names with spaces, blank lines, and duplicates form a text file.
* Fix errors when adding user/subreddit names with spaces and duplicate names in the add user/subreddit dialog.
* Fix crashing when exporting posts or content that have errors.
* Fix submission id naming token.



## v3.4.0-beta

### Minor Changes
* Add naming options for individual media id or reddit submission id.

### Bug Fixes
* Fix crashing when removing user/subreddit with over 1,000 posts or content items.
* Fix failed cross-posted reddit gallery downloads.


## v3.3.2-beta

### Bug Fixes
* Fix errors downloading image albums.
* Fix errors downloading reddit gallery albums.
* Fix freezing when merging some reddit video files.



## v3.3.1-beta

### Bug Fixes
* Fix crashing when trying to view list settings.
* Fix crashing when attempting to export to a directory that does not exist.
* Fix crashing when attempting to order user/subreddit lists by the count of related objects.
* Fix errors in attempting to download audio from reddit videos which do not contain audio.

## v3.3.0-beta

### Minor Changes
* Users, subreddits, posts, content, and comments can now be permanently deleted from the database along with any
associated files.
* Json imports now support legacy export files from previous versions.
* More aspects of multi-part download option is now user controllable.
* Improve user/subreddit date limit controls

### Bug Fixes
* Make multi-part downloader stoppable with rest of download cycle.
* Fix content not downloading correctly when the author's account has been deleted or suspended.
* Fix issue that caused application lock due to malfunctioning multi-part download.
* Fix issues with extracting and downloading reddit videos



## v3.2.1-beta

### Bug Fixes
* Fix some youtube videos not downloading correctly.
* Fix error with some imgur links not extracting correctly.
* Fix download gif checkbox not working.

## v3.2.0-beta

### Minor Changes
* New reddit galleries are now supported.

### Bug Fixes
* Fix crashing when checking imgur credits with no valid imgur credentials.
  * Fixes #133
* Fix message level for invalid/forbidden users/subreddits.
* Add progress bar handlers for comment extraction and download.
* Fix comments not being downloaded for posts with very long titles.
* Fix date limit display in user/subreddit settings dialog.
  * Fixes 138.
* Fix download problems with post titles containing "/" characters.
* Fix crashing when searching user/subreddit list with no entries.
* Fix crashing when initiating a download without a list set.
* Fix errors in downloading and merging reddit video/audio files.
  * Fixes #135.

## v3.1.1-beta

### Bug Fixes
* Fix crashing in database view dialog on some post items.
* Fix settings migration issue

## v3.1.0-beta

### Minor Changes
* Update notification can now be adjusted by the user to only display updates of a chosen level (major, minor, patch)
  or not at all.

### Bug Fixes
* Fix crashing due to ffmpeg warning dialog

## v3.0.0-beta

### Major Changes
* Entire application now uses an sqlite database on the backend for storage.
    * With database storage, downloaded data is able to be organized and displayed in infinitely usable ways. Since
    the database is local to your computer, the potential ways to analyse and use the data are endless.
* Complete database view window lets you easily see and filter downloaded content, posts, comments, users, and subreddits.
* New updated, easier to use GUI.
* New expanded settings make it easy to download only the content you want and customize the display and function of the
  application to suite your needs.
* Self posts and comments can now be downloaded.
    * As well as links in the text of both self posts and comments.
* Large files can now be downloaded in multiple parts simultaneously.
  * This dramatically improves download times when downloading large file such as videos.


### Minor Changes
* Downloads can now be scheduled to run incrementally or on a set time on a set day.
* Video sites can be individually disabled from download.
* File naming can be fully customized with a new token system so that downloads can be named practically anything you like
  with included information from the download (ex: post title, post score, author name, subreddit name, etc...)
* Output messages and display have been improved so that you only see the messages you want to see.
* Extraction thread count is now user adjustable
    * The number of threads used for content extraction is no longer tied to the download thread count and is adjustable
    in the settings
* Individual user/subreddit settings can now be adjusted in batches.  (Select multiple users/subreddits and use the context
  menu to go to settings)




# Released

## v2.3.4

### Major Changes
* Optimize post extraction from reddit which results in much faster extraction times.
  * Up to 85% faster extraction time in some use cases.
* Add extractor for Erome.com
* Allow the user to select to use more download threads to dramatically speed up downloads
* Added Support for RedGifs
  

### Minor Changes
* Removed Dependency on deprecated Imgur library 

### Bug Fixes
* Fix post extraction from gfycat urls that contained tags
* Fix various bugs in failed downloads dialog and exporters
* Fix Vidble link extraction
* Fix crashing when running single download while a download is currently running
* Fix date modified not being set for reddit videos that are downloaded in parts and merged
* Fix files being overwritten when a file with the same name is downloaded
* Fix crashing due to certain application key words being used in user/subreddit names
* Fixed bug with pinned posts

## v2.3.3

### Major Changes
* Videos hosted on reddit via v.redd.it links are now downloaded with audio.
  * FFmpeg must be installed on host system in order to merge video and audio files.

### Minor Changes
* Add user and subreddit list exporting options
* Allow importing user and subreddit lists from json and xml files

  * User or subreddit lists that have been exported to json or xml format will contain all information for the associated
reddit object (except for previously downloaded urls).  By doing this, reddit object lists that are exported
to json or xml file types can then be imported at a later date retaining the reddit objects user set attributes (ie: 
last downloaded post date, post limit, media filters, date added, etc.) 

* Stopping downloader now stops in progress downloads when the stop button is pressed.
* Add support for Imgur's commercial API endpoint.  See https://rapidapi.com/imgur/api/imgur-9/pricing for more 
information about obtaining the commercial api credentials.
* Add ability to download a user or subreddit as a single download from the main GUI lists context menus
* Add option to download a user or subreddit as a single download immediately after they are added


### Bug Fixes
* Restore copy and paste functionality to add reddit object dialog input line.
* Fix error message when trying to add a subreddit without an existing subreddit list.
* Fix imgur url formatting issues that happened in some circumstances
* Fix occasional crashing due to posts removed by reddit
* Fix crashing when trying to download from private subreddits



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
