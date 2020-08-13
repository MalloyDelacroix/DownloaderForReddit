"""
Downloader for Reddit takes a list of reddit users and subreddits and downloads content posted to reddit either by the
users or on the subreddits.


Copyright (C) 2017, Kyle Hickey


This file is part of the Downloader for Reddit.

Downloader for Reddit is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Downloader for Reddit is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Downloader for Reddit.  If not, see <http://www.gnu.org/licenses/>.
"""


from PyQt5 import QtCore, QtWidgets, QtGui


class FfmpegInfoDialog(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent=parent)
        self.layout = QtWidgets.QVBoxLayout()
        self.setWindowTitle('FFmpeg Info')
        self.setWindowIcon(QtGui.QIcon('Resources/Images/RedditDownloaderIcon.png'))

        self.label = QtWidgets.QLabel(
            """
            <p><font size=4>
            Videos hosted on v.redd.it are hosted as two separate files.  A video file and an audio file.  The
            Downloader For Reddit can download and save both files.  However, in order to join these files together to 
            make a complete video file, this application must reply on FFmpeg.  
            <br><br>
            FFmpeg is a cross platform open source application that plays and manipulates multimedia.  It is available
            for download <a href="http://ffmpeg.org/download.html">here.</a>
            <br><br>
            In order for FFmpeg to be used from this application, it must also be on the system path.  For full
            instructions on how to install FFmpeg on Windows and add it to your path please follow this link:
            
            <a href="https://www.wikihow.com/Install-FFmpeg-on-Windows">How to Install FFmpeg on Window</a>
            </font></p>
            
            """
        )

        self.label.setOpenExternalLinks(True)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setWordWrap(True)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
