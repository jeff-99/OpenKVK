from OpenKVK import BaseClient, QueryBuilder, ApiClient
import pytest
import unittest
import pickle
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

    def test__parse_query_results(self):
        json_py_result = ['[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Kinkrsoftware"]]}}]']
        csv_result = ['"bedrijfsnaam"\n"Kinkrsoftware"\n']

        json_py_multiple_query_result = ['[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Friesland Bank N.V."],["Jegro B.V."],["Koninklijke Doeksen B.V."],["B.V. Effectenbeleggingsmaatschappij G. Doeksen en Zonen"],["Batenburg Installatietechniek B.V."],["Van der Heide Bliksembeveiliging"],["Poort Waerachtig B.V."],["De Fakkel, christelijke boekwinkel"],["RIS Materieel B.V."],["N.V. Stedin Noord-Oost Friesland"],["Vliestroom B.V."],["BIONAL Nederland B.V."],["BIONAL International B.V."],["Be One"],["Jansen Holding B.V."],["Pras Houdster B.V."],["Uitgeverij Ridaire"],["H.G. Transport B.V."],["Protect Vochtwering"],["N.V. Stedin Netten Noord-Oost Friesland"],["De Incasso Alliantie Studiefinanciering Curacao B.V."],["Llacer Y. Navarro Internationaal Transport & Expeditie B.V."],["InterCollege Business School B.V."],["Oostvogel Charters B.V."],["Jong Oranje concept\\/copy"],["Firma Zaanen en Koning"],["ARAS Shipbrokers B.V."],["NOF Gasnetwerk B.V."],["Nemixx II B.V."],["Van Krimpen Fotografie B.V."],["Budgetcam"],["Meijer Groenvoorziening"],["SoundtillSunday"],["J.R. Oostra Beheer B.V."],["Stichting Graffonds Andries Bouwes"],["V.O.F. Scheepvaartbedrijf Edson"],["Stichting Friends of Mto Moyoni"],["ODIRIS Holdings B.V."],["Empire Marketing Group B.V."],["Tandartsenpraktijk Laan op Zuid"],["ODIRIS Networking & Security"],["ODIRIS ICT GROUP B.V."],["ODIRIS Flexforce GROUP B.V."],["ODIRIS Database Consultancy B.V."],["ODIRIS Flexforce # 1 B.V."],["ODIRIS Flexforce # 2 B.V."],["ODIRIS Systems Consultancy B.V."],["ODIRIS Middleware Consultancy B.V."],["ODIRIS Flexforce # 3 B.V."],["ODIRIS Ports & Terminals B.V."],["Stichting Jessour"],["Foodinvest B.V."],["S.V. van Brakel Onroerend Goed"],["Coast B.V."],["Clafis Engineering West B.V."],["Exobreedingcenter"],["Creators & Creations"],["iBenK B.V."],["Rastra Welding Consultancy"],["Magische Snaren"],["M. Obrocki"],["Visionair Dienstverlening B.V."],["SPAVA B.V."],["Nemixx Holding B.V."],["My Utmost Web Design"],["De Internet Compagnie"],["Clubkappers Rotterdam-hoogstraat"],["Clubkappers Rotterdam-peppelweg"],["Clubkappers Rotterdam Overschie"],["Clubkappers Rotterdam Schiebroek"],["Clubkappers Rotterdam Zuidwijk"],["Clubkappers Rotterdam Ommoord"],["Clubkappers Rotterdam Centrum"],["Hair Power Filialen B.V."],["Hung Translations"],["4za Grafische Communicatie"],["Charterama B.V."],["B.C.M. Theuns"],["Hermit"],["Schoonmaakbedrijf Djaner"],["Cortizo Entertainment"],["Kerskunst"],["Desired Media"],["Nel Linssen"],["LereN-eN. nl"],["Hypodomus Elst B.V."],["Hypodomus Alkmaar B.V."],["Grimsv\xc3\xb6tn 9 B.V."],["Grimsv\xc3\xb6tn 7 B.V."],["Grimsv\xc3\xb6tn 12 B.V."],["Grimsv\xc3\xb6tn 11 B.V."],["Grimsv\xc3\xb6tn 10 B.V."],["Grimsv\xc3\xb6tn 1 B.V."],["Grimsv\xc3\xb6tn 2 B.V."],["Grimsv\xc3\xb6tn 4 B.V."],["Grimsv\xc3\xb6tn 3 B.V."],["Solinox Rotterdam B.V."],["M.R. Graveland"],["E. van \'t Hart"]]}}]', '[{"RESULT":{"TYPES":["varchar"],"HEADER":["bedrijfsnaam"],"ROWS":[["Bineko-export B.V."],["Bytefabriek"],["AS Multimedia"],["Lok Productions"],["KUMBA ASSOCIATION IN THE NETHERLANDS"],["Mirazh"],["Stichting Administratiekantoor Combi Computer Service Franeker"],["Vereniging van eigenaars Gebouw \\"Prins Hendrikstaete\\" te Veendam"],["Pieter (Jolke) de Jong, dierenarts"],["Future-models"],["Swint Beeldend Kunstenaar"],["Stichting dezeruimte.nl"],["C4 Networks"],["Stichting Administratiekantoor IBA"],["Stichting City Beheer"],["Goedkopebanden.nu B.V."],["N.V. Nederlandse Gasunie"],["A.D. Boekholt B.V."],["V.O.F. van der Klei-Abels"],["Maintec B.V."],["G.H. Knoop Beheer B.V."],["De Zwarte Hond B.V."],["V.O.F. Bornrif"],["All-Round Kleurstudio J.A. Douma"],["M.S. Pirana"],["Intraval, Buro voor Onderzoek & Advies"],["Scheepvaartbedrijf Woortman B.V."],["Visser Vervoersmanagement Systemen B.V."],["Rolls-Royce Marine Benelux B.V."],["Vitol Anker International B.V."],["Doorduin Beheer B.V."],["Lideke Detmers Fotografie"],["Marker International B.V."],["Argos Storage B.V."],["MultiFlexx B.V."],["KAW architecten en adviseurs 2"],["Stichting Internet & Pay"],["HKB Stedenbouwkundigen B.V."],["W. Woortman Beheer B.V."],["De Jongens Ronner"],["Stichting AESIS Network"],["Foodservice Grootverbruik Laurens Terpstra B.V."],["Stichting Leklicht"],["Vertaalbureau Raisa"],["Stichting Tellerlikker"],["Adheera Webbouw"],["Stichting Vrienden van Gummen.org"],["Stichting Sofia"],["Joey Ruchtie"],["Bouma Beheer Onderneming B.V."],["Flex FD Support B.V."]]}}]']
        csv_multiple_query_result = ['"bedrijfsnaam"\n"Friesland Bank N.V."\n"Jegro B.V."\n"Koninklijke Doeksen B.V."\n"B.V. Effectenbeleggingsmaatschappij G. Doeksen en Zonen"\n"Batenburg Installatietechniek B.V."\n"Van der Heide Bliksembeveiliging"\n"Poort Waerachtig B.V."\n"De Fakkel, christelijke boekwinkel"\n"RIS Materieel B.V."\n"N.V. Stedin Noord-Oost Friesland"\n"Vliestroom B.V."\n"BIONAL Nederland B.V."\n"BIONAL International B.V."\n"Be One"\n"Jansen Holding B.V."\n"Pras Houdster B.V."\n"Uitgeverij Ridaire"\n"H.G. Transport B.V."\n"Protect Vochtwering"\n"N.V. Stedin Netten Noord-Oost Friesland"\n"De Incasso Alliantie Studiefinanciering Curacao B.V."\n"Llacer Y. Navarro Internationaal Transport & Expeditie B.V."\n"InterCollege Business School B.V."\n"Oostvogel Charters B.V."\n"Jong Oranje concept\\/copy"\n"Firma Zaanen en Koning"\n"ARAS Shipbrokers B.V."\n"NOF Gasnetwerk B.V."\n"Nemixx II B.V."\n"Van Krimpen Fotografie B.V."\n"Budgetcam"\n"Meijer Groenvoorziening"\n"SoundtillSunday"\n"J.R. Oostra Beheer B.V."\n"Stichting Graffonds Andries Bouwes"\n"V.O.F. Scheepvaartbedrijf Edson"\n"Stichting Friends of Mto Moyoni"\n"ODIRIS Holdings B.V."\n"Empire Marketing Group B.V."\n"Tandartsenpraktijk Laan op Zuid"\n"ODIRIS Networking & Security"\n"ODIRIS ICT GROUP B.V."\n"ODIRIS Flexforce GROUP B.V."\n"ODIRIS Database Consultancy B.V."\n"ODIRIS Flexforce # 1 B.V."\n"ODIRIS Flexforce # 2 B.V."\n"ODIRIS Systems Consultancy B.V."\n"ODIRIS Middleware Consultancy B.V."\n"ODIRIS Flexforce # 3 B.V."\n"ODIRIS Ports & Terminals B.V."\n"Stichting Jessour"\n"Foodinvest B.V."\n"S.V. van Brakel Onroerend Goed"\n"Coast B.V."\n"Clafis Engineering West B.V."\n"Exobreedingcenter"\n"Creators & Creations"\n"iBenK B.V."\n"Rastra Welding Consultancy"\n"Magische Snaren"\n"M. Obrocki"\n"Visionair Dienstverlening B.V."\n"SPAVA B.V."\n"Nemixx Holding B.V."\n"My Utmost Web Design"\n"De Internet Compagnie"\n"Clubkappers Rotterdam-hoogstraat"\n"Clubkappers Rotterdam-peppelweg"\n"Clubkappers Rotterdam Overschie"\n"Clubkappers Rotterdam Schiebroek"\n"Clubkappers Rotterdam Zuidwijk"\n"Clubkappers Rotterdam Ommoord"\n"Clubkappers Rotterdam Centrum"\n"Hair Power Filialen B.V."\n"Hung Translations"\n"4za Grafische Communicatie"\n"Charterama B.V."\n"B.C.M. Theuns"\n"Hermit"\n"Schoonmaakbedrijf Djaner"\n"Cortizo Entertainment"\n"Kerskunst"\n"Desired Media"\n"Nel Linssen"\n"LereN-eN. nl"\n"Hypodomus Elst B.V."\n"Hypodomus Alkmaar B.V."\n"Grimsv\xc3\xb6tn 9 B.V."\n"Grimsv\xc3\xb6tn 7 B.V."\n"Grimsv\xc3\xb6tn 12 B.V."\n"Grimsv\xc3\xb6tn 11 B.V."\n"Grimsv\xc3\xb6tn 10 B.V."\n"Grimsv\xc3\xb6tn 1 B.V."\n"Grimsv\xc3\xb6tn 2 B.V."\n"Grimsv\xc3\xb6tn 4 B.V."\n"Grimsv\xc3\xb6tn 3 B.V."\n"Solinox Rotterdam B.V."\n"M.R. Graveland"\n"E. van \'t Hart"\n', '"bedrijfsnaam"\n"Bineko-export B.V."\n"Bytefabriek"\n"AS Multimedia"\n"Lok Productions"\n"KUMBA ASSOCIATION IN THE NETHERLANDS"\n"Mirazh"\n"Stichting Administratiekantoor Combi Computer Service Franeker"\n"Vereniging van eigenaars Gebouw \\"Prins Hendrikstaete\\" te Veendam"\n"Pieter (Jolke) de Jong, dierenarts"\n"Future-models"\n"Swint Beeldend Kunstenaar"\n"Stichting dezeruimte.nl"\n"C4 Networks"\n"Stichting Administratiekantoor IBA"\n"Stichting City Beheer"\n"Goedkopebanden.nu B.V."\n"N.V. Nederlandse Gasunie"\n"A.D. Boekholt B.V."\n"V.O.F. van der Klei-Abels"\n"Maintec B.V."\n"G.H. Knoop Beheer B.V."\n"De Zwarte Hond B.V."\n"V.O.F. Bornrif"\n"All-Round Kleurstudio J.A. Douma"\n"M.S. Pirana"\n"Intraval, Buro voor Onderzoek & Advies"\n"Scheepvaartbedrijf Woortman B.V."\n"Visser Vervoersmanagement Systemen B.V."\n"Rolls-Royce Marine Benelux B.V."\n"Vitol Anker International B.V."\n"Doorduin Beheer B.V."\n"Lideke Detmers Fotografie"\n"Marker International B.V."\n"Argos Storage B.V."\n"MultiFlexx B.V."\n"KAW architecten en adviseurs 2"\n"Stichting Internet & Pay"\n"HKB Stedenbouwkundigen B.V."\n"W. Woortman Beheer B.V."\n"De Jongens Ronner"\n"Stichting AESIS Network"\n"Foodservice Grootverbruik Laurens Terpstra B.V."\n"Stichting Leklicht"\n"Vertaalbureau Raisa"\n"Stichting Tellerlikker"\n"Adheera Webbouw"\n"Stichting Vrienden van Gummen.org"\n"Stichting Sofia"\n"Joey Ruchtie"\n"Bouma Beheer Onderneming B.V."\n"Flex FD Support B.V."\n']

        # JSON FORMAT TEST
        self.client.setResponseFormat('json')
        # JSON - 1 query
        assert(self.client._parse_query_results(json_py_result) == '[{"bedrijfsnaam": "Kinkrsoftware"}]')
        # JSON - multiple queries
        os.path.dirname(__file__)
        with open(self.dir+'/multiple_query_results.json', 'r') as f1:
            result1 = f1.read()
        assert(self.client._parse_query_results(json_py_multiple_query_result) == result1)

        # PYTHON FORMAT TEST
        self.client.setResponseFormat('py')
        # PY - 1 query
        assert(self.client._parse_query_results(json_py_result) == [{"bedrijfsnaam": "Kinkrsoftware"}])
        # py - multiple queries
        result2 = pickle.load(open(self.dir+'/multiple_query_results.pickle','rb'))
        assert(self.client._parse_query_results(json_py_multiple_query_result) == result2)

        # CSV FORMAT TEST
        self.client.setResponseFormat('csv')
        # CSV - 1 query
        assert(self.client._parse_query_results(csv_result) == 'bedrijfsnaam\nKinkrsoftware')
        # CSV - multiple queries
        with open(self.dir+'/multiple_query_results.csv', 'r') as f3:
            result3 = f3.read()
        assert(self.client._parse_query_results(csv_multiple_query_result) == result3)

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