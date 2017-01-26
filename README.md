# DownloaderForReddit
Downloader for Reddit is a GUI application for downloading content submitted to reddit.  It has many advanced features and customizable settings to extract only content that you want and avoid duplicate downloads (if you so choose).  
The main GUI window is based on a similar project, The reddit Data Extractor by NSchrading.

Main Window
------------
![Main Window] (http://i.imgur.com/KKMdIxM.png)

In the main window you can add lists of users or subreddits to download content from.  User content is always downloaded in order of newest, and subreddit content order may be changed in the settings located in the file menu.

The downloader will first attempt to verify that each user or subreddit that is to be downloaded exists on reddit. Any time a user or subreddit fails verification a dialog will pop up to alert you as well as ask if you would like to remove the user or subreddit from the list. If the user or subreddit has a download folder in the current save path (meaning that posts were downloaded by that user or subreddit before) and you select to remove the user or subreddit, the download folder will be appended with word 'deleted' after the name so you are aware when looking in the folder that the user or subreddit no longer exists. 

To add a user or subreddit you must first add a user or subreddit list.  This can be done by either right clicking the dropdown combo box (displayed above with the words "Default" and "List Two") or from the lists menu at the top of the window.  This will open a dialog box that allows you to enter the list name.  You may make as many different lists as you wish and only the list displayed at the time the download button is clicked will be downloaded.  List may be deleted by right clicking the list combo box or from the lists menu.

To add users or subreddits either right click in the user list (left) or the subreddit list (right) and click "add user/subreddit" or select the option from the list menu at the top of the window.  This will bring up a dialog box allowing you to enter the names of the user or subreddits.  The dialog box has a third option besides ok and cancel which allows you to add multiple users or subreddits without having to close and open the window.  Holding shift + enter is a keyboard shortcut for this feature.  Users or subreddits may be deleted by right clicking the item you wish to delete or selecting the item then clicking the "-" button under the list.

The checkboxes below their respective windows dictate which list will be downloaded when the program is run.  Checking both checkboxes will constrain the user downloads to only the content which has been posted to the subreddits in the subreddit list.

Right clicking on a user or subreddit in one of the lists brings up a menu that allows you to open the individual items settings, view the items downloads in an application window, or open the items download folder in the default file manager.

Clicking the download button while the program is running will cancel the current downloads.  Any downloads which have already started (may be up to 4) will continue downloading after the button has been clicked and then the downloads will stop.  Any content that was extracted during the current session will be lost unless the download is resumed before the window is closed. In order to restart canceled downloads click the "Unfinished Downloads" button under the Lists menu option.  This will bring up a dialog display any downloads which have been extracted but not downloaded, and allow you to download them without being extracted again.

The output box will output information in real time as it happens during running.  It will output each user or subreddit that is validated and then each post that is saved with the full path the file was saved at. It will also output any posts that fail to extract or download.. The output will specify why the download failed (connection error, extraction error, unsupported domain, etc.) as well as tell you the post author, post title, the subreddit the post was submitted to, as well as provide the url for the content so that it may be downloaded manually.

Additionally under the lists menu there is a selection for 'Failed Downloads.' Clicking this button will bring up a dialog that displays all failed downloads as well as the information listed above. The default is for this dialog to open automatically at the end of a download to alert you to all failed downloads. The auto open feature can be disabled from the dialog.

Also in the lists menu is an option for 'Last Downloaded Users.' This option opens a dialog box which contains a list of the users that had content downloaded during the last session and optionally displays the content in their user download folder.


Settings Window
---------------
![Settings Window] (http://i.imgur.com/Pjytk4b.png)

The main settings window controls the universal settings through the entire program.  
From this window you can:
- Set the program to automatically save on close
- Backup and import user and subreddit lists
- Configure your Imgur client information
- Restrict downloads by post score
- Set the post score limit and whether to only download posts above or below that score
- Set the way that subreddit posts will be ordered (choosing to sort by top will enable a combo box to choose the desired top time period)
- Set the number of posts to download from (Reddits api sets the max number at 1000)
- Choose to enforce user date limits\*
- Restrict posts to after the specified date
- Choose whether or not to download videos or images
- Choose whether or not to avoid downloading duplicate links\*\*
- Set how downloaded subreddit posts are saved and named. The options are:
  - Save the posts in a folder named after the subreddit the post was submitted to
  - Save the posts in a folder named after the user that submitted the post
  - Save the posts in a folder named after the user that submitted the post which is then located in a folder named after the subreddit
  - Save the post in a folder named after the subreddit the post was submitted to which is then located in a folder named after the user that submitted the post
- Set wheter downloaded user posts will be named by the name of the post as used on reddit or by the image or album ID used on the hosting site
- Set the directory where you want posts to be saved to
- Change the method and order used to sort the user and subreddit lists 

The save button must be clicked for these settings to take affect. Saving the settings will also save any main window changes (i.e. user and subreddit lists).  After clicking 'Restore Defaults' and resetting all settings options, you must still click save for the settings to take affect.

\* Each time a post is downloaded useing the 'download user' method the latest date from a retrieved post is saved for that
   user.  Selecting this option will restrict post retrieval to after this date. There is no way to reset the date, although
   an alternate date may be set with the next option in the settings window or through each users individual settings window.

\*\* Each time an image or video is downloaded from a user or subreddit the url is saved in the users 'downloaded url list.' 
  If this option is checked the downloader will scan the list to make sure a queued url has not already be downloaded and will
  remove it from the queue if it has. Disabling this option does not mean the downloader will not save urls, but just means
  that it will not search the lists before attempting to download.


User Settings
-------------
![User Settings] (http://i.imgur.com/jb41c0r.png)

User settings is a way to further refine the downloader settings on a user by user basis.  Aside from user settings this window also displays some information about the selected user.  It will display the date and time the user was added to the list, the total number of downloads from the user, and a list of the urls that have been downloaded (this list is also used internally to avoid duplicate downloads).  By useing the 'Download This User' button at the top of the dialog, you can download only the selected user without downloading the rest of the users in the list.

Through the user settings menu you can also:
- Set a user specific post download limit
- Set how downloaded content is named for the user
- Set a custom save location for the user
- Choose to avoid downloading images or videos
- Choose whether or not to avoid duplicates for the user

The  'Do not overwrite these settings' checkbox when checked will not allow the main window settings to change the custom settings that you have set for individual users.

The 'Restrict by Date' checkbox restricts downloads to posts submitted after the latest post that has been downloaded for the user.  This date is shown in the calender box beside the checkbox. This date can be set to a custom date and time by clicking the calender box.  Be aware that if this date is changed to a custom date, it will no longer be updated to the users latest downloads by the program until the 'Restore Defaults' button is clicked.

Clicking restore defaults will set all options to the way the options are set in the main window settings and also uncheck the 'Do not overwrite these settings' checkbox for any user that has it checked. **After clicking 'Restore Defaults' you must then click the 'OK' button to accept the reset changes or they will not be reset.**

Clicking the 'View Downloads' button will display the content currently in the users download folder in place of the settings options. 


Subreddit Settings
------------------
![Subreddit Settings] (http://i.imgur.com/remW18B.png)

Subreddit settings works identically to the user settings dialog, but with a two more subreddit specific options.  You can change how saved subreddit posts will be named when they are saved.  The other additional settings is the sort method used to extract submissions from reddit.  This option only applies if the 'Download This Subreddit' button is used.  The sort method will not be applied to individual subreddits when the main downloader is run.


User Finder
-----------
![User Finder] (http://i.imgur.com/MYRbLBB.png)

The user finder allows you to find users who post top scoring content over the set amount of time (hour, day, week, etc.) and add the user to the user list to follow their posts. 

The Subreddit Watchlist window is where you will enter subreddits that you want to monitor.  The User Blacklist window is for users who consistenly post top scoring content that you do not wish to follow.  These users will not be included in the results if their posts are in the top.

You can also select to add found users to your main window user list automatically as well as selecting which main window user list you want to add users to. 

Setting the download sample size will dictate how many posts are downloaded from found users when the finder is ran.  

The user finder can be set to run at the same time as the main downloader by checking the 'Run when main app runs' checkbox. It may also be ran independatly by clicking the 'Run User Finder Only' button.

If any users are found to meet the score limit in the designated subreddits they will be added to a list on the second page of the finder dialog and their downloaded content will be displayed beside the list. From this page you can also add the users to main window user list designated on the first page of the finder. 

Content downloaded useing the user finder is kept in a sperate folder from the rest of the download folders.  There will be a folder created in the parent save directory called 'User Finder' which will contain found users download folders.

Any user that is in any of the main window user lists or that has a folder in the User Finder parent folder will not be downloaded or listed by the user finder.

When a found user is deleted from the found users list on the second page of the user finder their download folder in the User Finder parent folder is also deleted. These deleted users are not automatically added to the black list and may be found again if not added to the black list.  When deleting a user from the user finder list there is an option to also add the user to the black list automatically.
