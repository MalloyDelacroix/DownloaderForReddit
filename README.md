# Downloader For Reddit
Downloader for Reddit is a GUI application for downloading content, self text, and comments submitted to reddit.  
It has many advanced features and customizable settings to extract only content that you want and avoid duplicate 
downloads.  Everything that is extracted is stored in an sqlite database.  A built in database view window allows for
viewing and filtering all of the stored data.  The database can also be accessed with any software capable of reading 
an sqlite database so the data you extract can be used and analysed in limitless ways.



[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/MalloyDelacroix/DownloaderForReddit)
![BuildStatus](https://github.com/MalloyDelacroix/DownloaderForReddit/workflows/Build/badge.svg)
![TestStatus](https://github.com/MalloyDelacroix/DownloaderForReddit/workflows/Test/badge.svg)
[![Donate](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=XJQS23G9SN79G&currency_code=USD)
![GitHub all releases](https://img.shields.io/github/downloads/malloydelacroix/downloaderforreddit/total)
------------
<br>

![Main Window](https://imgur.com/759Job3.gif)


Users and subreddits are kept in two separate list displays.  You can have an unlimited number of lists containing an 
unlimited number of users/subreddits.  The lists can be downloaded as a whole or the individual users/subreddits can be 
downloaded independently.  User downloads can also be constrained to posts made only to the subreddits in the current 
subreddit list.

The output display can be customized to what level of information you would like to have shown.  Each output level can
be customized to display in what ever color you would like it shown.

<br>
<br>
<br>

![User/subreddit Settings](https://imgur.com/MByBar8.png)

Most download settings can be applied to the entire application, an entire user/subreddit list, or individual 
users/subreddits. This allows you to fine tune what is downloaded from where on a large or small scale.

<br>
<br>
<br>

![Settings Window](https://imgur.com/cpfzx0n.png)

The settings dialog is robust and lets you fine tune many aspects of the application such as download parameters,
display settings, and notifications.  Through this dialog you can also schedule downloads to run at a particular time
interval or run at certain times on certain days.

<br>
<br>
<br>

![Database View](https://imgur.com/Lr4B8xL.gif)

The database view can be adjusted to show you only the data that you want to see.  Each object view can be toggled on or
off and is dependant on the model view before it.  For instance: as shown above, if a subreddit is selected and the post
view is toggled off, all of the content for that subreddit will be displayed.  If posts are toggled on, only posts for
the selected subreddit will be displayed, and only content for the selected post will be displayed.

In addition to this filtering, there is also a robust specific filtering system in which every model can be filtered by 
almost every parameter in an easy to use interface.
<br>
<br>
<br>
### Requirements:

#### Imgur Posts:

Before any content can be downloaded from Imgur.com you will need to have an imgur client-id and client secret.
To obtain this go to https://api.imgur.com/oauth2/addclient.  
The following settings are recommended:
- Application name: Downloader For Reddit
- Authorization type: Anonymous usage without user authorization
- Authorization callback URL: Any valid url can be used here (ex. https://google.com) 
- Application website: https://github.com/MalloyDelacroix/DownloaderForReddit
- Email: This is the email the client-id and secret will me sent to

This client-id and client secret will be entered on the Imgur category of the settings menu.

Imgur will allow you 12,500 downloads per day and 500 downloads per hour. Your remaining Imgur credits and reset time 
can be viewed by clicking 'Imgur Credits' in the help menu.


#### Reddit Video Posts:

Due to the way they are hosted by reddit, video's that are downloaded from v.redd.it will be saved as two files, one 
video file and one audio file.  In order for the application to merge the two files into one playable video after 
download, [FFmpeg](https://www.ffmpeg.org/) must be installed and on the system path.

Please see this [wikiHow article](https://www.wikihow.com/Install-FFmpeg-on-Windows) for more information on how to 
install FFmpeg on a Windows system.


Installing The Downloader For Reddit
---------------------------------

By far the easiest way to install and use The Downloader for Reddit is to download one of the pre-packaged executables 
from the [releases section](https://github.com/MalloyDelacroix/DownloaderForReddit/releases) (at the moment stand alone 
executables are only available for Windows).

To run the program, extract the folder (DownloaderForReddit) from the zip file and scroll down to and click the 
executable file (DownloaderForReddit.exe). Everything is self contained in the folder, there is nothing to install.
<br>
To run the application from source, please refer to the wiki entry 
[Setting Up A Development Environment.](https://github.com/MalloyDelacroix/DownloaderForReddit/wiki/Setting-Up-A-Development-Environment)
