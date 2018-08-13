import unittest
from Tests.UnitTests.Extractors import TestDirectExtractor
from Tests.UnitTests.Extractors.TestImgurExtractor import TestImgurExtractor
from Tests.UnitTests.Extractors import TestGfycatExtractor
from Tests.UnitTests.Extractors import TestVidbleExtractor
from Tests.UnitTests.Extractors.TestExtractor import TestExtractor


def extractor_suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.makeSuite(TestDirectExtractor))
    test_suite.addTest(unittest.makeSuite(TestImgurExtractor))
    test_suite.addTest(unittest.makeSuite(TestGfycatExtractor))
    test_suite.addTest(unittest.makeSuite(TestVidbleExtractor))
    test_suite.addTest(unittest.makeSuite(TestExtractor))
    return test_suite


runner = unittest.TextTestRunner()
runner.run(extractor_suite())

# if __name__ == '__main__':
#     suite = extractor_suite()
#     runner = unittest.TextTestRunner()
#     runner.run(suite)
