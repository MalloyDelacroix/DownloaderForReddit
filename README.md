# Downloader For Reddit
Downloader for Reddit is a GUI application for downloading content submitted to reddit.  It has many advanced features and customizable settings to extract only content that you want and avoid duplicate downloads (if you so choose).  
The main GUI window is based on a similar project, The reddit Data Extractor by NSchrading.

[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/MalloyDelacroix) 
![BuildStatus](https://github.com/MalloyDelacroix/DownloaderForReddit/workflows/Build/badge.svg)
![TestStatus](https://github.com/MalloyDelacroix/DownloaderForReddit/workflows/Test/badge.svg)
------------
![Main Window](http://i.imgur.com/vmK8Su8.png)

The two list windows are where users (left) and subreddits (right) will be displayed after they are entered.  To add users or subreddits to the list you must first create a list name by right-clicking the drop down boxes under the corresponding windows.  When you run the downloader, only the lists that are displayed in the combo boxes will be downloaded.  The checkboxes under each list dictate which list will be downloaded.  Checking both will download only user content that is posted to the subreddits in the subreddit list.

![Settings Window](https://i.imgur.com/jciqBy4.png?1)

Filters and limits can be set from the settings dialog opened through the file menu and settings for individual users and subreddits can be accessed by right clicking them in their respective lists.  Accessing the user or subreddit settings menus will also allow you to display the content that is in the user or subreddits download folder. 

![User Settings](https://i.imgur.com/zIM4oPR.png?1)

### Requirements:

#### Imgur Posts:

Before any content can be downloaded from Imgur.com you will need to have an imgur client-id and client secret.
To obtain this go to https://api.imgur.com/oauth2/addclient.  
The following settings are recommended:
- Application name: Downloader For Reddit
- Authorization type: Anonymouse usage without user authorization
- Authorization callback URL: Any valid url can be used here (ex. https://google.com) 
- Application website: https://github.com/MalloyDelacroix/DownloaderForReddit
- Email: This is the email the client-id and secret will me sent to

This client-id and client secret will be entered in the 'Imgur Client Information' dialog box accesed through the settings menu.

Imgur will allow you 12,500 downloads per day. Your remaining Imgur credits can be viewed by clicking 'Imgur Credits' in the help menu.


#### Reddit Video Posts:

Due to the way they are hosted by reddit, video's that are downloaded from v.redd.it will be two files, one video and one audio.  In order for the application to merge the two files into one playable video after download, [FFmpeg](https://www.ffmpeg.org/) must be installed and on the system path.

Please see this [wikiHow article](https://www.wikihow.com/Install-FFmpeg-on-Windows) for more information on how to install FFmpeg on a Windows system.


Installing The Downloader For Reddit
---------------------------------

By far the easiest way to install and use The Downloader for Reddit is to download one of the pre-packaged executables from the [releases section](https://github.com/MalloyDelacroix/DownloaderForReddit/releases) (at the moment stand alone executables are only available for Windows and Linux).

To run the program, extract the folder (DownloaderForReddit) from the zip file and scroll down to and click the executable file (DownloaderForReddit.exe on windows and just DownloaderForReddit on Linux). Everything is self contained in the folder, there is nothing to install.

To run the application from source, please refer to the wiki entry [Setting Up A Development Environment.](https://github.com/MalloyDelacroix/DownloaderForReddit/wiki/Setting-Up-A-Development-Environment)
