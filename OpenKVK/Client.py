import math
import urllib2
import urllib
import ast
import json

class Client(object):
    """
    Python wrapper for the OpenKVK API

    """

    BASE_URL = "http://api.openkvk.nl/"
    DEFAULT_RESPONSE_FORMAT = "py"
    DEFAULT_LIMIT = 99

    def __init__(self,response_format=None,limit=None,onlyActiveCompanies=True):
        self.response_format = response_format or Client.DEFAULT_RESPONSE_FORMAT
        self.limit = limit or Client.DEFAULT_LIMIT
        self.onlyActiveCompanies = onlyActiveCompanies


    def setResponseFormat(self,format):
        """
        Set the :class:`OpenKVK.Client.Client` response format.Client

        Possible values are :
            - json : Returns json formatted string
            - py : Returns python dict
            - csv : Returns csv formatted string

        :param string format: format to set the Client response to
        """
        if format in ['json','py','csv']:
            self.response_format = format
        else:
            raise ValueError('Chosen Format is not Supported')

    def setActiveOnly(self,boolean):
        """Sets a query filter based on the company's status
        If True the results will only contain active companies.
        Set to False to disable this filter

        """
        if isinstance(boolean,bool):
            self.onlyActiveCompanies = boolean
        else:
            raise TypeError('Parameter is not a Boolean value')

    def _urlencode_query(self,query):
        """encode *query* for use in a url syntax
        :param string query: Validated SQL-92 query as a string
        """
        query =query.replace('"', "'")
        return urllib.quote(query,safe="*;%'`=&")

    def _query_divider(self,query,total):
        """
        Helper function to divide query into multiple queries to comply to the webservice limit

        :param string query: SQL-92 compliant query
        :param int total: New Limit value
        :returns: List of queries to execute
        :rtype: list
        """
        if total > Client.DEFAULT_LIMIT:
            pages = int(math.ceil(float(total) / float(Client.DEFAULT_LIMIT)))
        else:
            pages = 1

        query_buffer = []
        total = total
        offset = 0
        limit = Client.DEFAULT_LIMIT if total > Client.DEFAULT_LIMIT else total
        for i in range(pages):
            query_buffer.append("{0} LIMIT {1} OFFSET {2};".format(query,limit,offset))
            total -= limit
            offset += limit
            if total < Client.DEFAULT_LIMIT:
                limit = total

        return query_buffer

    def _query_construct_options(self,basequery,filters):
        """
        Helper function for adding filters to the request

        filters example:
            {"plaats" : "Rotterdam",
             "rechtsvorm" : "Besloten Vennootschap"}

        :param string basequery: SQL-92 compliant query base to add filters to
        :param dict filters: Dictionary containing filters
        """
        filters = filters or {}
        query = basequery
        if self.onlyActiveCompanies:
            statement = " AND isnull(status)"
            query += statement
        for key in filters:
            statement = " AND {0} = '{1}'".format(key,filters[key])
            query += statement
        return query

    def _pythonify_result(self, result):
        """
        Helper function for parsing the query result in a more pythonic format

        :param dict result: Raw (combined) result query
        :returns: List of company information dictionaries
        :rtype: list
        """
        new_result = []
        for company in result['RESULT']['ROWS']:
            new_company = {}
            for i,item in enumerate(company):
                new_company[result['RESULT']['HEADER'][i]] = item
            new_result.append(new_company)
        return new_result

    def _parse_query_results(self,response_buffer):
        """Takes raw response of :class:OpenKVK.Client.Client._do_query and parses the data to the preferred format
        :param list response_buffer: List of service responses
        """
        print response_buffer
        result = {}
        if self.response_format == 'json':
            for response in response_buffer:
                jsonpy = json.loads(response)
                if not 'RESULT' in result:
                    result['RESULT'] = jsonpy[0]['RESULT']
                else:
                    result['RESULT']['ROWS'] += jsonpy[0]['RESULT']['ROWS']
            pythonified_result = self._pythonify_result(result)
            result = json.dumps(pythonified_result)
        elif self.response_format == 'py':
            response_buffer = [ast.literal_eval(response) for response in response_buffer]
            for i in range(len(response_buffer)):
                if i == 0:
                    result['RESULT'] = response_buffer[i][0]['RESULT']
                else:
                    result['RESULT']['ROWS'] = result['RESULT']['ROWS'] + response_buffer[i][0]['RESULT']['ROWS']
            pythonified_result = self._pythonify_result(result)
            result = pythonified_result
        elif self.response_format == 'csv':
            header =[]
            records = []
            result = []
            for response in response_buffer:
                rows = response.split('\n')
                for a,line in enumerate(rows):
                    if isinstance(line,str):
                        columns = line.split(',')
                        record = []
                        for item in columns:
                            item = item.strip('"')
                            if a == 0 and len(header) < len(columns):
                                header.append(item)
                            elif a != 0:
                                record.append(item)
                            else:
                                continue
                        if not record == ['']:
                            records.append(record)
            result.append(",".join(header))
            for record in records:
                if len(record) > 0:
                    result.append(",".join(record))
            result = "\n".join(result)
        else:
            raise ValueError('Unsupported response format')

        return result

    def _do_query(self,basequery,limit,filters=None):
        """Return query results of *query*

        :param string query: SQL-92 valid query
        :param int limit: Maximum number of results
        :returns: Result set in set response format
        :rtype:
        """
        query = self._query_construct_options(basequery,filters)
        query_buffer = self._query_divider(query,limit)

        response_buffer = []
        for q in range(len(query_buffer)):
            url = Client.BASE_URL+self.response_format+"/"+self._urlencode_query(query_buffer[q])
            request = urllib2.urlopen(url)
            response = request.read()
            response_buffer.append(response)

        result = self._parse_query_results(response_buffer)
        return result

    def get_by_kvk(self, kvk, fields='*'):
        """Return company information in selected format if the the given *kvk* is found

        :param int kvk: KVK-nummer
        :param list columns: List of columns
        :returns: Company information
        """
        basequery = "SELECT {0} FROM kvk WHERE kvks = {1}".format(",".join(fields),kvk)
        return self._do_query(basequery,1)


    def get_by_name(self, name, limit=99, fields='*'):
        """Return a list of company information dicts for the given *name* limited to *limit* records

        :param string name: Name of the company
        :param int limit: Maximum number of records
        :param list fields: List of fields to return
        :rtype: list
        """
        basequery = "SELECT {0} FROM kvk WHERE bedrijfsnaam ILIKE '%{1}%'".format(",".join(fields),name)
        return self._do_query(basequery,limit)

    def get_by_sbi(self, sbi, limit=99, fields='*',filters=None):
        """Return a list of company information *sbicode* limited to *limit* records

        :param string name: Name of the company
        :param int limit: Maximum number of records
        :rtype: list
        """
        basequery = "SELECT {0} FROM kvk JOIN kvk_sbi ON kvk_sbi.kvk = kvk.kvk WHERE code = '{1}'".format(",".join(fields),sbi)
        return self._do_query(basequery,limit,filters=None)

    def get_by_city(self,city,limit=99,fields='*',filters=None):
        """Return a list of company information *sbicode* limited to *limit* records

        :param string name: Name of the company
        :param int limit: Maximum number of records
        :rtype: list
        """
        basequery = "SELECT {0} FROM kvk WHERE plaats ILIKE '%{1}%'".format(",".join(fields),city)
        return self._do_query(basequery,limit)

    def search(self, searchstring=None ):
        """
        Return a list of company information based on a fulltext search
        """
        basequery = "SELECT x.kvk, x.bedrijfsnaam, x.adres, x.postcode, x.plaats, x.type,NOT(anbikvk.kvks is null AND anbikvk.intrekking is null) AS 'anbi', status, x.kvks, x.sub FROM (SELECT kvk.kvk, kvk.bedrijfsnaam, kvk.adres, kvk.postcode, kvk.plaats, kvk.type, kvk.kvks, kvk.sub FROM sphinx_searchIndex('{0}', '{1}') AS fts, kvk WHERE kvk.kvk = fts.id) AS x LEFT JOIN anbikvk ON x.kvks = anbikvk.kvks LEFT JOIN faillissementen ON x.kvks = faillissementen.kvk".format(searchstring,'*')
        return self._do_query(basequery,limit=200)

    def get_by_postcode_distance(self,postcode,distance):
        """Return a list of companies within a postcode range
        :param string postcode: Dutch postcode
        :param int distance: Distance from postcode in kilometres

        example haversine formula :
            R = 6373.0

            lat1 = radians(52.2296756)
            lon1 = radians(21.0122287)
            lat2 = radians(52.406374)
            lon2 = radians(16.9251681)

            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c

        """
        pass

    def get_custom(self,query,limit):
        """Returns company information based on a custom query.
        for low-level interaction with the openkvk api, but with the convenience of the parsers used in this module

        :param string query: A SQL-92 query string
        :param int limit: Maximum number of records

        """
        return self._do_query(query,limit)