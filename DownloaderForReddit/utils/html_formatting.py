import re


def format_html(html_text: str) -> str:
    """
    Formats a given HTML text by replacing newline characters with HTML line break
    tags and wrapping the entire text with paragraph tags.

    :param html_text: The HTML text to format.
    :return: The formatted HTML text.
    """
    html_text = html_text.replace('\n', '<br/>')
    html_text = linkify_urls(html_text)
    return f'<p>{html_text}</p>'


def linkify_urls(text: str) -> str:
    """
    Converts all URLs in a given string into clickable HTML anchor links.

    :param text: The input string containing URLs that need to be converted
        into clickable HTML links.
    :return: A string where any valid URLs are replaced with equivalent clickable
        anchor links in HTML format.
    """
    url_regex = re.compile(
        r'(https?://[^\s"<>()]+)',  # match http(s) URLs excluding common HTML-breaking chars
        re.IGNORECASE
    )

    return url_regex.sub(r'<a href="\1">\1</a>', text)