import json
import requests
import dateparser
import argparse
import config

def load_file(filename: str) -> list[list[dict]]:
    with open(filename, 'r') as f:
        certs = []
        duplicate_count = 0
        for line in f:
            data = json.loads(line)
            record = data[0]
            value = data[1]
            if value[0] == 'duplicate':
                duplicate_count += 1
            else:
                if len(certs)>0:
                    for cert in certs[-1]:
                        cert['Duplicates After'] = duplicate_count
                for cert in value:
                    cert['Filename'] = filename
                    cert['Roll Number'] = record
                    cert['Duplicates Before'] = duplicate_count
                duplicate_count = 0
                certs.append(value)
        return certs

def flatten_list(certs: list[list[dict]]) -> list[dict]:
    new_certs = [old_cert for cert_list in certs for old_cert in cert_list]
    return new_certs
        
def clean_cert(cert: dict) -> dict:
    new_cert = {}
    for key, value in cert.items():
        if key in ['']:
            continue
        if key in ['Duplicates After', 'Duplicates Before', 'Roll Number']:
            new_cert[key] = value
        else:
            new_cert[key] = value.strip()
    return new_cert 

def parse_date(date: str) -> str|None:
    try:
        return dateparser.parse(date).isoformat()
    except AttributeError:
        return None

def parse_dates(cert: dict) -> dict:
    return cert | {key+" ISO": parse_date(value) for key,value in cert.items() if 'Date' in key}

def write_file(filename: str, certs: list) -> None:
    with open(filename,'w') as f:
        for cert in certs:
            f.writelines(json.dumps(cert)+'\n')

def get_uuid() -> str:
    while True:
        response = requests.get(f'{config.db}/_uuids?count=10')
        for uuid in response.json()['uuids']:
            yield uuid
        
def write_to_db(cert:dict,uuid_gen=get_uuid()) -> None:
    uuid = next(uuid_gen)
    try:
        response = requests.put(f'{config.db}/death-certs/{uuid}', json=cert, auth=config.db_creds)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(cert)
        raise
def already_stored(cert:dict) -> bool:
    query = {"selector":{"Name": cert["Name"], "Death Date ISO": cert["Death Date ISO"]}}
    response = requests.post(f'{config.db}/death-certs/_find', json=query, auth=config.db_creds)
    return len(response.json()["docs"]) > 0

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Load Death Certificate files to couchdb')
    parser.add_argument('filename', nargs='+', help='Files to process')
    parser.add_argument('-r', '--reprocess', action='store_true')
    args = parser.parse_args()
    for file in args.filename:
        certs = load_file(file)
        flat_certs = flatten_list(certs)
        clean_certs = map(clean_cert, flat_certs)
        dated_certs = map(parse_dates, clean_certs)
        for cert in dated_certs:
            if not args.reprocess or not already_stored(cert): 
                write_to_db(cert)
