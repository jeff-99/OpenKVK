import math
import urllib2
import urllib
import ast
import json
import re

class BaseClient(object):
    """
    The Base client is the absolute basic client to the OpenKVK API
    It sets the basic configuration of the Client

    :param string response_format: Sets the format of the responses
    :param bool onlyActiveCompanies: Set's up the client to only query active companies
    """

    BASE_URL = "http://api.openkvk.nl/"
    DEFAULT_RESPONSE_FORMAT = "py"
    DEFAULT_LIMIT = 99

    def __init__(self,response_format=None,onlyActiveCompanies=True):
        self.response_format = response_format or BaseClient.DEFAULT_RESPONSE_FORMAT
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

    def request(self,query):
        """
        Returns the raw response of the OpenKVK API.
        You could use this method as a minimalistic wrapper for the API, it should save you 3-4 lines of code
        """
        url = BaseClient.BASE_URL+self.response_format+"/"+self._urlencode_query(query)
        request = urllib2.urlopen(url)
        response = request.read()
        return response


class QueryBuilder(BaseClient):
    """
    Class to handle all of the query building, formatting and communication with the BaseClient
    With this class you could perform a custom query, with the additional convenience of a result parser

    """
    def _query_divider(self,query,total):
        """
        Helper function to divide query into multiple queries to comply to the webservice limit

        :param string query: SQL-92 compliant query
        :param int total: New Limit value
        :returns: List of queries to execute
        :rtype: list
        """
        if total > BaseClient.DEFAULT_LIMIT:
            pages = int(math.ceil(float(total) / float(BaseClient.DEFAULT_LIMIT)))
        else:
            pages = 1

        query_buffer = []
        total = total
        offset = 0
        limit = BaseClient.DEFAULT_LIMIT if total > BaseClient.DEFAULT_LIMIT else total
        for i in range(pages):
            query_buffer.append("{0} LIMIT {1} OFFSET {2};".format(query,limit,offset))
            total -= limit
            offset += limit
            if total < BaseClient.DEFAULT_LIMIT:
                limit = total

        return query_buffer

    def _build_query(self,basequery,**kwargs):
        """
        Helper function for adding filters to the request

        possible filters:
            - plaats (="Rotterdam")
            - rechtsvorm (="Besloten Vennootschap")

        :param string basequery: SQL-92 compliant query base to add filters to
        :param dict filters: Dictionary containing filters
        """
        query = basequery
        if self.onlyActiveCompanies:
            statement = " AND isnull(status)"
            query += statement
        for key in kwargs:
            query += " AND {0} = '{1}'".format(key,kwargs[key])
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

    def do_query(self,basequery,limit,**kwargs):
        """Return query results of *query*

        :param string query: SQL-92 valid query
        :param int limit: Maximum number of results
        :returns: Result set in set response format
        :rtype:
        """
        query = self._build_query(basequery,**kwargs)
        query_buffer = self._query_divider(query,limit)

        response_buffer = []
        for q in range(len(query_buffer)):
            response = self.request(query_buffer[q])
            response_buffer.append(response)

        result = self._parse_query_results(response_buffer)
        return result

    def query(self,query):
        """Returns company information based on a custom query.
        for direct interaction with the openkvk api, but with the convenience of the parsers used in this module

        :param string query: A SQL-92 query string
        """
        if isinstance(query,basestring):
            low = query.lower()
            if 'limit' in low:
                match = re.findall(r'limit \d+',low)[0]
                key,value = match.split(' ')
                limit = int(value)
                query = low.replace(match, "")
            else:
                limit = 99
            return self.do_query(query,limit)
        else:
            raise(ValueError('Query parameter should be a string'))

class ApiClient(QueryBuilder):
    """
    The ApiClient is the complete python wrapper for the OpenKVK API.

    :param string response_format: Sets the format of the responses
    :param bool onlyActiveCompanies: Set's up the client to only query active companies
    """
    def get_by_kvk(self, kvk, fields='*'):
        """Return company information in selected format if the the given *kvk* is found

        :param int kvk: KVK-nummer
        :param list columns: List of columns
        :returns: Company information
        """
        basequery = "SELECT {0} FROM kvk WHERE kvks = {1}".format(",".join(fields),kvk)
        return self.do_query(basequery,1)


    def get_by_name(self, name, limit=99, fields='*'):
        """Return a list of company information dicts for the given *name* limited to *limit* records

        :param string name: Name of the company
        :param int limit: Maximum number of records
        :param list fields: List of fields to return
        :rtype: list
        """
        basequery = "SELECT {0} FROM kvk WHERE bedrijfsnaam ILIKE '%{1}%'".format(",".join(fields),name)
        return self.do_query(basequery,limit)

    def get_by_sbi(self, sbi, limit=99, fields='*',**kwargs):
        """Return a list of company information *sbicode* limited to *limit* records

        :param string name: Name of the company
        :param int limit: Maximum number of records
        :rtype: list
        """
        basequery = "SELECT {0} FROM kvk JOIN kvk_sbi ON kvk_sbi.kvk = kvk.kvk WHERE code = '{1}'".format(",".join(fields),sbi)
        return self.do_query(basequery,limit,**kwargs)

    def get_by_city(self,city,limit=99,fields='*',**kwargs):
        """Return a list of company information *sbicode* limited to *limit* records

        :param string name: Name of the company
        :param int limit: Maximum number of records
        :rtype: list
        """
        basequery = "SELECT {0} FROM kvk WHERE plaats ILIKE '%{1}%'".format(",".join(fields),city)
        return self.do_query(basequery,limit,**kwargs)

    def get_bankruptcies(self,fields='*',limit=99,**kwargs):
        """Returns list of bankrupt companies by specified parameters
        method should at least contain one of the following parameters:
            - kvk
            - plaats
            - rechtbank
        :param int kvk: KVK number
        :param string plaats: City name (case insensitive)
        :param string rechtbank: Name of the court that issued the bankruptcy (case insensitive)
        :param int limit: Maximum number of records
        :param list fields: List of company information fields to return
        :rtype: list
        """
        basequery = "SELECT {0} FROM fallissementen ".format(",".join(fields))

        if 'kvk' in kwargs:
            basequery += "WHERE kvks = {0} ".format(kwargs['kvk'])
            kwargs.pop('kvk',None)
        elif 'plaats' in kwargs:
            basequery += "WHERE plaats ILIKE '%{0}%' ".format(kwargs['plaats'])
            kwargs.pop('plaats',None)
        elif 'rechtbank' in kwargs:
            basequery += "WHERE rechtbank ILIKE '%{0}%' ".format(kwargs['rechtbank'])
            kwargs.pop('rechtbank', None)
        else:
            raise KeyError('Method should at least contain one of the following parameters: "kvk","plaats","rechtbank"')

        return self.do_query(basequery,limit,**kwargs)