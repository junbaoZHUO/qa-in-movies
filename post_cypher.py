import requests
import json
import base64

def QueryCypher(url, login, query):
    headers = {
    'content-type': 'application/json',
    'authorization': "Basic " + base64.b64encode(login.encode()).decode()}

    cypher_query = {
        "statements": [
        {"statement": query,
        "resultDataContents": ["graph","row"]
        }]
    }

    result = requests.post(url, data=json.dumps(cypher_query), headers=headers).json()
    return result    

if __name__ == '__main__':
    # url = "http://" + requests.get('http://jump.mivc.top:8223/getip').json()['ip'] + ":17474/db/data/transaction/commit"
    # login = "neo4j:123456"
    url = "http://10.29.51.231:7474/db/data/transaction/commit"
    login = "neo4j:123"

    query = "MATCH (n:Movie)-[r]-(b) RETURN DISTINCT labels(b)"
    # query = "MATCH p0=(a1:person)-[r0]-(b0:movie),p1=(a2:person)-[r1]-(b0:movie) WHERE ((a2.primaryName=~'(?i)Kate Winslet' AND type(r1)=~'(?i)act.*' ) and (a1.primaryName=~'(?i)Leonardo DiCaprio' AND type(r0)=~'(?i)act.*' )) RETURN p0, p1, b0.primaryTitle"

    result = QueryCypher(url, login, query)
    print(result["results"][0]["data"][1]["row"][0])

    # with open('./test.json', 'a') as f:
    #     json_dump = json.dumps(result, indent=4, ensure_ascii=False)
    #     f.write(json_dump)
