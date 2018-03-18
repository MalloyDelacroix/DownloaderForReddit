# Guidelines for Contributing

## Code of Conduct
This project has a [Contributor Code Of Conduct]( DownloaderForReddit/CODE_OF_CONDUCT.md ).  By participating in this project, you agree to abide by its terms.

## Creating an Issue

Please create a new issue for each item that can be resolved.  Avoid grouping multiple bugs or feature requests into the same issue.

### Bugs
* For all but the most trivial issues, please attach the latest log file produced by the application to your issue.  This greatly helps solve issues.
  * Be sure that the issue that you are reporting is the last thing that happened when running the application so that it is the last item in the log.
  * Please attach the actual log file to the issue, not the copied and pasted text from the log.
* Please include enough information in your issue that the problem can be identified and reproduced.
* Check the unreleased section of the [changelog]( DownloaderForReddit/CHANGE_LOG.md ) to make sure the issue you are reporting has not already been resolved.
* Indicate which operating system and version of the Downloader For Reddit you are using
 
 ### Request For Features / Improvements
 * Request for features and/or improvements are always welcome.
 * Please check both open and closed issues marked with the "feature request" or "enhancement" label to see if the feature you are requesting has already been requested.
 * Provide as many details as possible about the feature that you are requesting.

## Contributing 

### Contribution Priorities
This is a list of the priorities for the project in order from most important to least important:
* Major bug fixes - bugs that hinder the applications operation or cause it to crash.
* Minor bugs - bugs that don't cause major problems but do cause minor annoyance. (e.g. typos and display issues )
* New extractors
* New features
* Code refactoring for easier development

### Pull Requests
Before opening a pull request, please consider the following items:
* Please base changes off of the master branch of this repo
* Ensure that your pull request only includes the minimum amount of change needed to fix a single issue
* If you are fixing an issue from the issue tracker, please reference the issue number that you are fixing in your commit message, this will allow the issue to be [automatically closed](https://help.github.com/articles/closing-issues-using-keywords/).
* If possible, please provide tests for the feature that you have added.
* Be sure to test your contribution thoroughly before committing.  Test not only your new feature, but other application features to make sure your change did not affect any other aspects of the application.
* If possible please also package the application with pyinstaller, then test the same as described above
  * This app is distributed in an executable version made with pyinstaller and many times bugs are not seen until after being packaged.
  * See the sample .spec file for packaging with pyinstaller.
  * Indicate in your pull request if you have tested your code by packaging with pyinstaller.

### Style Guide
Consistent code style is considered very important in this project.  When looking through the source files for this 
project, a clear coding style should be apparent.  If a contribution varies from this style guide in a very noticeable way, 
it will not be merged until corrected.
* Follow pep8 (except where this guide specifies otherwise).
* Spell check to a reasonable extent.
* All class names, file names, and package names should be `CapitalizedWords` with no spaces or underscores (a.k.a. `UpperCamelCase`)
* All method and variable names should be in `lower_case_with_underscores`
* Constants should be in `UPPER_CASE_WITH_UNDERSCORES`
* Formatted strings should be used in lieu of the `+` operator for string concatenation.  (e.g. `'%s should be used' % 'this'` | `'instead' + 'of' + 'this'`)
* Single quotations `'should be used for strings'`.
* Place spaces between items separated by commas and between variables and operators (e.g. `1 + 2` and `[1, 2, 3]` not `1+2` or `[1,2,3]`)
* Do not put spaces between parentheses and variables (e.g. `(x, y)` not `( x, y )`)
* Use one blank line between method definitions and two blank lines between top level definitions
* Do not use `==` or `!=` to compare bool statements or `None`.  Use `if x:`, `if not x:`, `if x is not None:`
* Indent with tabs, not spaces (tab should equate to 4 spaces)

#### Documentation
All but the very simplest of methods should be well documented with a clear description of what the method does, what parameters it takes,
what type those parameters are, what it returns, and what type the return is.  The documentation should appear after the method name
and before the methods code.
* Method parameters should be indicated by `:param parameter: description here`.
* Method parameter types should be indicated by `:type parameter: str`.
* Return parameters should be indicated by `:return: description here`
* Return type should be indicated by `:rtype: bool`

Below is an example method with documentation:
```python
def get_filename(self, media_id):
    """
    Checks the settings manager to determine if the post title or the content id (as stored on the container site)
    should be used to name the content that is being extracted.
    :param media_id: The image/album/video id as stored on a container site.
    :type media_id: str
    :return: The file name that should be used when creating the Content object from the extracted url.
    :rtype: str
    """
    return self.post_title if self.name_downloads_by == 'Post Title' else media_id
```

#### Imports
* Unless being imported from the same package or library, each import should appear on its own line.
* The import order should be as follows:
  * Built in python modules
  * External modules
  * *a blank space for separation*
  * DownloaderForReddit modules

Example:
```python
import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

from Core import Injector
from Extractors.BaseExtractor import BaseExtractor
```

If you create a new file, please include the license comment at the top of the file.  This comment can be copied and pasted from any other source file.
 
There is no particular way in which methods and functions must be ordered.  However, please ensure that your methods and functions are in **some logical order**.
New methods should not just be added to the end of a class, but should be in some order in which you could explain if asked.
