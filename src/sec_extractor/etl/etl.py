from typing import Iterator
import hashlib

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

    def __init__(self, record_type):
        self._record_type = record_type
        self._records = []
        self._records_keys = {}

    def add_record(self, record_value, record_date, quarters):
        record_key = f"{record_date}-{record_value}-{quarters}"
        if record_key not in self._records_keys:
            self._records_keys[record_key] = 1
            self._records.append(Record(record_value, record_date, quarters))
            return

        self._records_keys[record_key] += 1

    def toDict(self):
        d = {
            "record_type": self._record_type,
            "records": []
        }

        for r in self._records:
            d['records'].append(r.toDict())

        d['records'] = sorted(d['records'], key=lambda record: int(record['date']))
        return d

    @property
    def record_type(self):
        return self._record_type


class Company:
    def __init__(self, name, company_id):
        self._id = company_id
        self._name = name
        self._records_sets = {}

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    def add_record(self, record_type, record_value, record_date, quarters):
        if record_type not in self._records_sets:
            self._records_sets[record_type] = RecordSet(record_type=record_type)

        self._records_sets[record_type].add_record(record_value, record_date, quarters)

    def toDict(self):
        forms = []

        for record_set in self._records_sets.values():
            forms.append(record_set.toDict())

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
            if company_name not in ["APPLE INC", "OKTA, INC."]:
                continue

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
            try:
                company = db.get_company_by_filing_id(filing_id)
            except KeyError:
                continue

            company.add_record(record_type, record_value, record_date, quarters)