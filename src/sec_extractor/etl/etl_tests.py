import unittest
import os
from etl import CompaniesDB, load_companies


class TestETL(unittest.TestCase):

    def test_etl(self):
        current_dir = os.path.dirname(__file__)
        db = CompaniesDB()
        load_companies(db, f"{current_dir}/../data/test/sub.txt", f"{current_dir}/../data/test/num.txt")

        apple = db.get_company_by_name("APPLE INC").toDict()
        self.assertTrue(len(apple) > 0)
        okta = db.get_company_by_name("OKTA, INC.").toDict()
        self.assertTrue(len(okta) > 0)


if __name__ == '__main__':
    unittest.main()
