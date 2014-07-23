from __future__ import print_function
from OpenKVK import BaseClient

client = BaseClient()
client.setResponseFormat('py')
print(client.query("SELECT * FROM kvk WHERE kvks = 27312152;"))
