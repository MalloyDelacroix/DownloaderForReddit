from unittest import TestCase

from DownloaderForReddit.viewmodels.hyperlink_delegate import HyperlinkDelegate


class TestHyperlinkDelegate(TestCase):

    def test_linkify_urls_basic(self):
        input_text = 'Check out this sick link: https://example.com'
        expected_output = 'Check out this sick link: <a href="https://example.com">https://example.com</a>'
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_text), expected_output)

    def test_linkify_urls_multiple_links(self):
        input_text = 'Visit https://example.com and http://test.com'
        expected_output = 'Visit <a href="https://example.com">https://example.com</a> and <a href="http://test.com">http://test.com</a>'
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_text), expected_output)

    def test_linkify_urls_no_links(self):
        input_output_text = 'No URLs here, just plain text.'
        # Input and output should be the same with no URLs
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_output_text), input_output_text)

    def test_linkify_urls_empty_value_supplied(self):
        input_output_text = ''
        # Input and output should be the same when empty value is given
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_output_text), input_output_text)

    def test_linkify_urls_with_special_characters(self):
        input_text = 'Check https://example.com/path?query=param&key=value'
        expected_output = 'Check <a href="https://example.com/path?query=param&key=value">https://example.com/path?query=param&key=value</a>'
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_text), expected_output)

    def test_linkify_urls_embedded_with_other_text(self):
        input_text = 'Link in text:before https://example.com after:text'
        expected_output = 'Link in text:before <a href="https://example.com">https://example.com</a> after:text'
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_text), expected_output)

    def test_linkify_urls_with_complex_url(self):
        input_text = 'Very link, much wow: http://www.test.com/path/to/embeded/location/many/pathsegments/?query=param&key=value#fragment'
        expected_output = 'Very link, much wow: <a href="http://www.test.com/path/to/embeded/location/many/pathsegments/?query=param&key=value#fragment">http://www.test.com/path/to/embeded/location/many/pathsegments/?query=param&key=value#fragment</a>'
        self.assertEqual(HyperlinkDelegate.linkify_urls(input_text), expected_output)

    def test_format_html_single_line(self):
        input_text = 'This is a test'
        expected_output = '<p>This is a test</p>'
        self.assertEqual(HyperlinkDelegate.format_html(input_text), expected_output)

    def test_format_html_multiple_lines(self):
        input_text = 'This is a test\nWith multiple lines\nFor formatting'
        expected_output = '<p>This is a test<br/>With multiple lines<br/>For formatting</p>'
        self.assertEqual(HyperlinkDelegate.format_html(input_text), expected_output)

    def test_format_html_empty_string(self):
        input_text = ''
        expected_output = '<p></p>'
        self.assertEqual(HyperlinkDelegate.format_html(input_text), expected_output)

    def test_format_html_newline_only(self):
        input_text = '\n\n'
        expected_output = '<p><br/><br/></p>'
        self.assertEqual(HyperlinkDelegate.format_html(input_text), expected_output)

    def test_format_html_with_a_link_in_text(self):
        input_text = 'This is a test\nWith multiple lines\nFor formatting\nhttps://example.com'
        expected_output = '<p>This is a test<br/>With multiple lines<br/>For formatting<br/><a href="https://example.com">https://example.com</a></p>'
        self.assertEqual(HyperlinkDelegate.format_html(input_text), expected_output)
