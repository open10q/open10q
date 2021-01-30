#!/usr/bin/env python3

import glob
from etl.etl import CompaniesDB, load_companies

if __name__ == '__main__':
    db = CompaniesDB()
    dirs = glob.glob("./data/extracted/*")
    for d in dirs:
        print(f"loading {d} ...")
        load_companies(db, f"{d}/sub.txt", f"{d}/num.txt")

    apple = db.get_company_by_name("APPLE INC").toDict()
    okta = db.get_company_by_name("OKTA, INC.").toDict()
    print("done")