from __future__ import print_function
from OpenKVK import QueryBuilder

client = QueryBuilder()
client.setResponseFormat('csv')
print(client.query("SELECT * FROM kvk WHERE kvks = 27312152;"))
