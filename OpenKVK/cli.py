import argparse
from OpenKVK import ApiClient


parser = argparse.ArgumentParser()
parser.add_argument('--kvk','-k',type=int, help="zoek via kvk nummer")
parser.add_argument('--bedrijfsnaam', '-b',type=str , help="Zoek bedrijf via naam")
parser.add_argument('--plaats', '-p', type=str,help="zoek per plaats")
parser.add_argument('--output', '-o',type=str,help="output destination")
parser.add_argument('--format','-f', type=str, help="output format", default="csv")

def main():
    args = parser.parse_args()
    client = ApiClient(response_format=args.format)
    result = None
    if args.kvk:
        result = client.get_by_kvk(kvk=args.kvk)
    elif args.bedrijfsnaam:
        result = client.get_by_name(args.bedrijfsnaam)
    elif args.plaats:
        result = client.get_by_city(args.plaats,limit=1)
    else:
        print "Je hebt geen argumenten ingevoerd"

    if args.output:
        with open(args.output, 'w') as o:
            o.write(result)

if __name__ == '__main__':
    main()