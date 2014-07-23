from OpenKVK import BaseClient, QueryBuilder, ApiClient
import pytest
import unittest
import os


class TestBaseClient(unittest.TestCase):
    def setUp(self):
        self.client = BaseClient()

    def test_client_urlencode_query(self):

        query1 = "SELECT * FROM KVK;"
        assert(self.client._urlencode_query(query1) == "SELECT%20*%20FROM%20KVK;")

        query2 = "SELECT * FROM KVK WHERE naam = 'something'"
        assert(self.client._urlencode_query(query2) == "SELECT%20*%20FROM%20KVK%20WHERE%20naam%20=%20'something'")

        query3 = 'SELECT * FROM KVK WHERE naam = "something"'
        assert(self.client._urlencode_query(query3) == "SELECT%20*%20FROM%20KVK%20WHERE%20naam%20=%20'something'")

    def test_response_format(self):
        with pytest.raises(ValueError):
            self.client.setResponseFormat('unsupportedformat')


class TestQueryBuilder(unittest.TestCase):
    def setUp(self):
        self.client = QueryBuilder()
        self.dir = os.path.dirname(__file__)

    def test__query_divider(self):
        query = "x"

        # 1 query
        assert(self.client._query_divider(query,1) == ["x LIMIT 1 OFFSET 0;"])

        # multiple queries
        assert(self.client._query_divider(query,500) == ['x LIMIT 99 OFFSET 0;',
                                                   'x LIMIT 99 OFFSET 99;',
                                                   'x LIMIT 99 OFFSET 198;',
                                                   'x LIMIT 99 OFFSET 297;',
                                                   'x LIMIT 99 OFFSET 396;',
                                                   'x LIMIT 5 OFFSET 495;'])

    def test__parse_query_results_json(self):
        json_result = [u'[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Kinkrsoftware"]]}}]']
        json_multiple_query_result = ['[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Friesland Bank N.V."]]}}]', '[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Bineko-export B.V."],["Bytefabriek"]]}}]']


        # JSON FORMAT TEST
        self.client.setResponseFormat('json')
        # JSON - 1 query
        assert(self.client._parse_query_results(json_result) == '[{"bedrijfsnaam": "Kinkrsoftware"}]')
        # JSON - multiple queries
        assert(self.client._parse_query_results(json_multiple_query_result) == '[{"bedrijfsnaam": "Friesland Bank N.V."}, {"bedrijfsnaam": "Bineko-export B.V."}, {"bedrijfsnaam": "Bytefabriek"}]')

    def test_parse_query_results_py(self):
        py_result = ['[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Kinkrsoftware"]]}}]']
        py_multiple_query_result = ['[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Friesland Bank N.V."]]}}]', '[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Bineko-export B.V."],["Bytefabriek"]]}}]']
        # PYTHON FORMAT TEST
        self.client.setResponseFormat('py')
        # PY - 1 query
        assert(self.client._parse_query_results(py_result) == [{"bedrijfsnaam": "Kinkrsoftware"}])
        # py - multiple queries
        assert(self.client._parse_query_results(py_multiple_query_result) == [{"bedrijfsnaam": "Friesland Bank N.V."},{"bedrijfsnaam": "Bineko-export B.V."},{"bedrijfsnaam": "Bytefabriek"}])

    def test_parse_query_results_csv(self):
        csv_result = ['"bedrijfsnaam"\n"Kinkrsoftware"\n']
        csv_multiple_query_result = ['"bedrijfsnaam"\n"Friesland Bank N.V."\n"', '"bedrijfsnaam"\n"Bineko-export B.V."\n"Bytefabriek"\n']
        # CSV FORMAT TEST
        self.client.setResponseFormat('csv')
        # CSV - 1 query
        assert(self.client._parse_query_results(csv_result) == 'bedrijfsnaam\nKinkrsoftware')
        # CSV - multiple queries
        assert(self.client._parse_query_results(csv_multiple_query_result) == 'bedrijfsnaam\nFriesland Bank N.V.\nBineko-export B.V.\nBytefabriek')

    def test__do_query(self):
        pass

    def test_query(self):
        with pytest.raises(ValueError):
            self.client.query(1)

class TestApiClient(unittest.TestCase):
    def setUp(self):
        self.client = ApiClient()
        self.client.setResponseFormat('json')

    def test_get_by_kvk(self):
        assert(self.client.get_by_kvk(27312152,fields=['bedrijfsnaam'])=='[{"bedrijfsnaam": "Kinkrsoftware"}]')

    def test_get_by_name(self):
        assert(self.client.get_by_name("Kinkrsoftware",limit=1,fields=['bedrijfsnaam'])=='[{"bedrijfsnaam": "Kinkrsoftware"}]')

    def test_get_banktruptcies(self):
        with pytest.raises(KeyError):
            self.client.get_bankruptcies()


if __name__ =="__main__":
    pytest.main()