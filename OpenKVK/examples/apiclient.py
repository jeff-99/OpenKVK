from __future__ import print_function
from OpenKVK import ApiClient

client = ApiClient(onlyActiveCompanies=False,response_format="json")
print(client.get_by_kvk(27312152,fields=["bedrijfsnaam"]))
