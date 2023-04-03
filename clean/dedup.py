import json
import requests
from deepdiff import DeepDiff
import rapidfuzz
import config

def get_candidates(date, name):
    query = {'selector':{'Death Date ISO':date, 'Name':name}}
    response = requests.post(f'{config.db}/death-certs/_find',json=query,auth=config.db_creds)
    return response.json()

def get_deletions(candidates):
    docs = candidates['docs']
    if len(docs)==2:
        print(json.dumps(docs[0],indent=4))
        print(DeepDiff(docs[0],docs[1]).pretty())
    else:
        print(json.dumps(docs,indent=4))
    deletions = input('Which to delete? ')
    try:
        deletions = map(int,deletions.split(' '))
        deletions = [(candidates['docs'][i-1]['_id'], candidates['docs'][i-1]['_rev']) for i in deletions]
        return deletions
    except ValueError:
        return None

def delete(_id, _rev):
    response = requests.delete(f'{config.db}/death-certs/{_id}?rev={_rev}', auth=config.db_creds)
    print(response.json())

def main():
    with open('dedup2.json','r') as f:
        dups = json.load(f)
        for dup in dups:
            certs = get_candidates(dup['key'][0], dup['key'][1])
            deletions = get_deletions(certs)
            if deletions:
                for deletion in deletions:
                    delete(*deletion)
                print(deletions)

def couch_db_find(query):
    return requests.post(f'{config.db}/death-certs/_find', json=query, auth=config.db_creds).json()

def find(query):
    response = couch_db_find(query)
    while len(response['docs']) > 0:
        for doc in response['docs']:
            yield doc
        query['bookmark'] = response['bookmark']
        response = couch_db_find(query)

def update(document, field, value):
    document[field] = value
    response = requests.put(f'{config.db}/death-certs/{document["_id"]}', json=document, auth=config.db_creds)
    response.raise_for_status()

def get_suggestions(value, known_values):
    suggestions = rapidfuzz.process.extract(value, known_values)
    option = input(f"1: {value}\n2: {suggestions[0]}\n3: View More Suggestions\n4: Other\n> ")
    if option == '1':
        return value
    if option == '2':
        return suggestions[0][0]
    if option == '3':
        for i,suggestion in enumerate(suggestions[1:]):
            print(f"{i+1}: {suggestion}")
        index = input("Index or x: ")
        try:
            index = int(index)
            return suggestions[index][0]
        except (ValueError, IndexError):
            pass
    return input("Corrected Name: ")

if __name__=='__main__':
    main()
