import requests
from functools import lru_cache
import json
import base64
import re
from post_cypher import QueryCypher
from information import url_local, login_local, url, login, line_break


def LinkPath(entity_list):
    center_character = entity_list.pop(0)

    type_list = [t['type'] for t in entity_list]
    path_list = []
    if "Character" not in type_list and center_character["type"] != "Character":
        path_list.append([center_character])
        for entity in entity_list:
            path_list.append([entity])
    else:
        while len(entity_list) > 0:
            path = [center_character]
            start = "Character"
            flag = 1
            while flag == 1:
                query = "MATCH (n:" + start + ")-[r]-(b) RETURN DISTINCT labels(b)"
                result = QueryCypher(url_local, login_local, query)
                node_candidates = [nodes["row"][0][0] for nodes in result["results"][0]["data"]]
                flag = 0
                for index, t in enumerate(type_list):
                    if t in node_candidates:
                        type_list.pop(index)
                        node = entity_list.pop(index)
                        path.append(node)
                        flag = 1
                        start = node['type']
                        path_list.append(path)
                        if start == "Character":
                            path = [center_character]
                        else:
                            path = [node]
                        break
            if path == [center_character]:
                break
        if len(path_list) == 0:
            path_list.append([center_character])
        if len(entity_list) > 0:
            path_list.append(entity_list)
    return path_list

def find_clip(clip_id):
    query = "MATCH p = (a:Clip)--(b) where ((labels(b)[0] IN ['Character', 'Plot', 'Event','Movie', 'Scene'])) and a.id = '"+  clip_id + "' RETURN p"
    print("----生成的cypher查询语句：" + line_break + query)
    res = QueryCypher(url, login, query)
    return res

def find_frame(frame_id):
    query = "MATCH p = (d:Actor)--(b:Character)--(a:Keyframe)--(c) where (not (labels(c)[0] IN ['Clip', 'Keyframe', 'OCR', 'Object'])) and (a.id = '"+  frame_id + "') RETURN DISTINCT p"
    print("----生成的cypher查询语句：" + line_break + query)
    res = QueryCypher(url, login, query)
    return res

def find_actor(paths, answers, movie_id):
    character_list = []
    for path in paths:
        for entity in path:
            if entity["type"] == "Character":
                if not re.match("^(wh(at|o|ich|ere))", entity["entity"], re.I) and \
                        not re.match("^(什么|哪些|谁|角色)", entity["entity"], re.I):
                    character_list.append(entity["entity"])
                else:
                    if type(answers) != str:
                        answers = list(list(answers.values())[0])
                        character_list += list(answers)
    character_list = list(set(character_list))
    print("角色列表:" )
    print(character_list)
    query = "MATCH p = (m:Movie)--(a:Character)--(b:Actor) where m.id = '" + movie_id + "' and a.name IN " + str(character_list) + " RETURN p"
    print("----生成的cypher查询语句：" + line_break + query)
    res = QueryCypher(url, login, query)
    
    return res

def find_character_clips(paths, movie_id):
    character_list = []
    for path in paths:
        for entity in path:
            if entity["type"] == "Character":
                if not re.match("^(wh(at|o|ich|ere))", entity["entity"], re.I) and \
                        not re.match("^(什么|哪些|谁|角色)", entity["entity"], re.I):
                    character_list.append(entity["entity"])

    match_line = "MATCH p=(m:Movie)--(c:Clip)"
    where_line = "WHERE "
    return_line = "RETURN c.id"
    for i in range(len(character_list)):
        match_line += ", p" + str(i) + " = (c:Clip)--(a" + str(i) + ")"
        where_line += "a" + str(i) + ".name = '" + character_list[i] + "' AND "

    where_line += "m.id = '" + movie_id + "'"
    query = match_line + line_break + where_line + line_break + return_line
    print("----生成的cypher查询语句：" + line_break + query)
    res = QueryCypher(url, login, query)
    
    return res

@lru_cache()
def find_graph(id_list):
    data = []
    node_dict = {}
    relation_dict = {}
    for id in id_list:
        query = "MATCH p = (a:MovieType)--(m:Movie)--(c:Character)--(h:Historicalpersonage) where m.id = '" + id + "'\n" + \
                "with p, a, m, c limit 15" + "\n"  + \
                "MATCH p1 = (c)--(d:Event)--(e:Clip)" + "\n" + \
                "with m, p, p1 limit 100" + "\n" + \
                "MATCH p2 = (m)--(he:Historicalevent)--(f1:Historicalevent)--(f2:Historicalevent)" + "\n" + \
                "RETURN p, p1, p2"
        print("----生成的cypher查询语句：" + line_break + query)
        result = QueryCypher(url, login, query)
        for item in result["results"][0]["data"]:
            del item['row']
            del item['meta']
            node_list_new = []
            for node in item['graph']["nodes"]:
                if node["id"] not in node_dict:
                    node_dict[node["id"]] = 1
                    node_list_new.append(node)
            item['graph']["nodes"] = node_list_new

            relation_list_new = []
            for relation in item['graph']["relationships"]:
                if relation["id"] not in relation_dict:
                    relation_dict[relation["id"]] = 1
                    relation_list_new.append(relation)
            item['graph']["relationships"] = relation_list_new

        data = data + result["results"][0]["data"]
    return data

def find_frame_set(id_list):
    frame_id = set()
    for clip_id in id_list:
        query = "MATCH p = (a:Clip)--(b:Keyframe) where a.id = '"+  clip_id + "' RETURN DISTINCT b.id LIMIT 50"
        print("----生成的cypher查询语句：" + line_break + query)
        res = QueryCypher(url, login, query)
        if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
            for r in res["results"][0]["data"]:
                frame_id.add(r["row"][0])
    return list(frame_id)

def find_clip_set(clip_set):
    query = "MATCH p = (a:Clip)--(b) where ((labels(b)[0] IN ['Character', 'Plot', 'Event','Movie', 'Scene'])) and a.id IN "+ str(clip_set) + " RETURN p"
    print("----生成的cypher查询语句：" + line_break + query)
    res = QueryCypher(url, login, query)
    return res

def find_actor2frame(id_list):
    character_list = set()
    for actor_id in id_list:
        query = "MATCH p = (a:Actor)--(b:Character) where a.actor_nconst_id = '"+  actor_id + "' RETURN DISTINCT b.id LIMIT 10"
        print("----生成的cypher查询语句：" + line_break + query)
        res = QueryCypher(url, login, query)
        print(res)
        if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
            for r in res["results"][0]["data"]:
                character_list.add(r["row"][0])
    print(character_list)

    clip_list = {}
    for character in character_list:
        query = "MATCH p = (a:Character)--(b:Clip) where a.id = '"+  character + "' RETURN DISTINCT b.id LIMIT 10"
        print("----生成的cypher查询语句：" + line_break + query)
        res = QueryCypher(url, login, query)
        if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
            for r in res["results"][0]["data"]:
                clip_list[r["row"][0]] = character
    print(clip_list)

    frame_id = set()
    for clip_id in clip_list:
        query = "MATCH p = (a:Clip)--(b:Keyframe)--(c:Character) where a.id = '"+  clip_id + "' and c.id = '" + clip_list[clip_id] + "' RETURN DISTINCT b.id LIMIT 3"
        print("----生成的cypher查询语句：" + line_break + query)
        res = QueryCypher(url, login, query)
        if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
            for r in res["results"][0]["data"]:
                frame_id.add(r["row"][0])

    return list(frame_id)

if __name__ == '__main__':
    # entity_list = [{'entity': '载垣', 'type': 'Character'}, {'entity': '桂良', 'type': 'Character'}, {'entity': '交谈', 'type': 'Interaction'}, {'entity': '生气', 'type': 'Expression'}]
    # entity_list = [{'entity': '载垣', 'type': 'Character'}, {'entity': '下跪', 'type': 'Action'}, {'entity': '生气', 'type': 'Expression'}]
    # entity_list = [{'entity': '桂良', 'type': 'Character'}, {'entity': '演讲', 'type': 'Action'}, {'entity': '高兴', 'type': 'Expression'}]
    entity_list = [{'entity': '载垣', 'type': 'Character'}, {'entity': '开会', 'type': 'Event'}, {'entity': '车站', 'type': 'Scene'}]
    path = LinkPath(entity_list)
    print(path)
