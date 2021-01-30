import unittest

from etl import CompaniesDB, load_companies


class TestETL(unittest.TestCase):

    def test_etl(self):
        db = CompaniesDB()
        load_companies(db, "../data/test/sub.txt", "../data/test/num.txt")

        apple = db.get_company_by_name("APPLE INC").toDict()
        self.assertTrue(len(apple) > 0)
        okta = db.get_company_by_name("OKTA, INC.").toDict()
        self.assertTrue(len(okta) > 0)


if __name__ == '__main__':
    unittest.main()
