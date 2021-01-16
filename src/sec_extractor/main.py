from typing import Iterator
import hashlib
import glob

INTERESTING_FIELDS = [
    'Assets', 'NetIncomeLoss', 'OperatingIncomeLoss', 'GrossProfit'
]

INTERESTING_FORMS = [
    '10-K', '10-Q'
]


class Record:

    def __init__(self, record_value, record_date, quarters: int):
        self.record_date = record_date
        self.record_value = record_value
        self.quarters = quarters

    def toDict(self):
        return {
            'quarters': self.quarters,
            'date': self.record_date,
            'value': self.record_value
        }


class RecordSet:

    def __init__(self, form_type):
        self._form_type = form_type
        self._records = {}

    def add_record(self, record_type, record_value, record_date, quarters):
        if record_type not in self._records:
            self._records[record_type] = []

        self._records[record_type].append(Record(record_value, record_date, quarters))

    def toDict(self):
        d = {
            "form_type": self._form_type,
            "records": {}
        }

        for record_type, records in self._records.items():
            if record_type in INTERESTING_FIELDS:
                if record_type not in d['records']:
                    d['records'][record_type] = []

                for r in records:
                    d['records'][record_type].append(r.toDict())

        return d

    @property
    def form_type(self):
        return self._form_type


class Company:
    def __init__(self, name, company_id):
        self._id = company_id
        self._name = name
        self._filings = {}
        self._records = []

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def add_filing(self, filing_id: str, filing_type: str):
        if filing_id in self._filings:
            return

        self._filings[filing_id] = RecordSet(form_type=filing_type)

    def add_record(self, record_type, record_value, record_date, filing_id, quarters):
        self._filings[filing_id].add_record(record_type, record_value, record_date, quarters)

    def toDict(self):
        forms = []

        for filing in self._filings.values():
            if filing.form_type not in INTERESTING_FORMS:
                continue

            forms.append(filing.toDict())

        return forms


def gen_company_id(name: str):
    # company name is unique and can be used as Key
    return hashlib.sha256(name.encode('utf-8')).hexdigest()


class CompaniesDB:

    def __init__(self):
        self._db = {}
        self._filing_id_to_company_id = {}

    def create_or_update_company(self, company_name: str, filing_id: str, filing_type: str):
        company_id = gen_company_id(company_name)

        if company_id not in self._db:
            self._db[company_id] = Company(company_name, company_id)

        if filing_id not in self._filing_id_to_company_id:
            self._filing_id_to_company_id[filing_id] = company_id
            self._db[company_id].add_filing(filing_id, filing_type)

    def get_company_by_id(self, company_id: str) -> Company:
        return self._db[company_id]

    def get_company_by_filing_id(self, filing_id: str):
        return self._db[self._filing_id_to_company_id[filing_id]]

    def get_company_by_name(self, name) -> Company:
        return self._db[gen_company_id(name)]

    def iter_companies(self) -> Iterator[Company]:
        for company in self._db.values():
            yield company


def load_companies(db: CompaniesDB, companies_file: str, fin_data_file: str):
    with open(companies_file, "r") as f:
        for line in f:
            values = line.split("\t")
            form_type = values[25]
            company_name = values[2]
            filing_id = values[0]
            db.create_or_update_company(company_name, filing_id, form_type)

    with open(fin_data_file, "r") as f:
        for line in f:
            values = line.split("\t")
            filing_id = values[0]
            record_type = values[1]
            record_date = values[4]
            quarters = values[5]
            record_value = values[7]
            company = db.get_company_by_filing_id(filing_id)
            company.add_record(record_type, record_value, record_date, filing_id, quarters)


if __name__ == '__main__':
    db = CompaniesDB()
    dirs = glob.glob("./data/extracted/*")
    for d in dirs:
        print(f"loading {d} ...")
        load_companies(db, f"{d}/sub.txt", f"{d}/num.txt")

    apple = db.get_company_by_name("APPLE INC")
    json = apple.toDict()
    print("done")
