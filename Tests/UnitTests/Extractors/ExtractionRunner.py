import unittest
from Tests.UnitTests.Extractors.DirectExtractorTest import DirectExtractorTest
from Tests.UnitTests.Extractors.ImgurExtractorTest import ImgurExtractorTest
from Tests.UnitTests.Extractors.GfycatExtractorTest import GfycatExtractorTest
from Tests.UnitTests.Extractors.VidbleExtractorTest import VidbleExtractorTest
from Tests.UnitTests.Extractors.ExtractorTest import ExtractorTest


def extractor_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(DirectExtractorTest))
    test_suite.addTest(unittest.makeSuite(ImgurExtractorTest))
    test_suite.addTest(unittest.makeSuite(GfycatExtractorTest))
    test_suite.addTest(unittest.makeSuite(VidbleExtractorTest))
    test_suite.addTest(unittest.makeSuite(ExtractorTest))
    return test_suite


# runner = unittest.TextTestRunner()
# runner.run(extractor_suite())

if __name__ == '__main__':
    suite = extractor_suite()
    runner = unittest.TextTestRunner()
    runner.run(suite)
