

class Link:

    def __init__(self, url, title, score, date):
        """
        A class that holds information about an image link to be displayed in the user finder gui.
        :param url: The url of the image.
        :param title: The title of the post from reddit.
        :param score: The score of the post on reddit.
        :param date: The date that the post was made.
        """
        self.url = url
        self.title = title
        self.score = score
        self.date = date
