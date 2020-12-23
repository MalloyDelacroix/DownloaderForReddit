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

from pythonjsonlogger import jsonlogger


class JsonStreamFormatter(jsonlogger.JsonFormatter):

    """
    A custom formatter to display log items each on a new line when logging
    to stream.

    This is basically an exact copy of the jsonlogger.JsonFormatter with the
    format method overwritten to not serialize the output to json and to
    display each would be json item on a different line to enhance readability
    in the stream output.
    """

    def format(self, record):
        message_dict = {}
        if isinstance(record.msg, dict):
            message_dict = record.msg
            record.message = None
        else:
            record.message = record.getMessage()
        # only format time if needed
        if "asctime" in self._required_fields:
            record.asctime = self.formatTime(record, self.datefmt)

        # Display formatted exception, but allow overriding it in the
        # user-supplied dict.
        if record.exc_info and not message_dict.get('exc_info'):
            message_dict['exc_info'] = self.formatException(record.exc_info)
        if not message_dict.get('exc_info') and record.exc_text:
            message_dict['exc_info'] = record.exc_text

        log_record = {}

        self.add_fields(log_record, record, message_dict)
        log_record = self.process_log_record(log_record)

        return '%s%s\n' % (self.prefix, self.format_return(log_record))

    @staticmethod
    def format_return(log_record):
        """Formats the log_record to display each item on a new line to increase readability"""
        ret_list = []
        for key, value in log_record.items():
            ret_list.append('%s: %s' % (key, value))
        return '\n'.join(ret_list)
