from OpenKVK.Client import Client
import pytest
import unittest


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client()

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

    def test__query_divider(self):
        query = "x"

        # 1 query
        assert(self.client._query_divider(query,1) == ["x LIMIT 99 OFFSET 0"])

        # multiple queries
        assert(self.client._query_divider(query,500) == ['x LIMIT 99 OFFSET 0',
                                                   'x LIMIT 99 OFFSET 99',
                                                   'x LIMIT 99 OFFSET 198',
                                                   'x LIMIT 99 OFFSET 297',
                                                   'x LIMIT 99 OFFSET 396',
                                                   'x LIMIT 99 OFFSET 495'])

    def test__parse_query_results(self):
        self.client.setResponseFormat('json')
        # JSON - 1 query

        # JSON - multiple queries
        self.client.setResponseFormat('py')
        # PY - 1 query
        # py - multiple queries
        self.client.setResponseFormat('csv')
        # CSV - 1 query
        # CSV - multiple queries

    def test__do_query(self):
        pass

if __name__ =="__main__":
    pytest.main()