# -*- coding:utf-8 -*-
"""
    实体、实体关系定义，问题，数据库
"""
import platform
from py2neo import Graph
import requests
import csv
import pickle

# 定制换行符
sys_str = platform.system()
if sys_str == "Windows":
    line_break = "\n"
elif sys_str == "Linux":
    line_break = "\r\n"
else:
    print("Other System tasks")

# 爱国主义和乐观主义
zhuyi_dict = pickle.load(open("movie_clip_dict.pickle",'rb'))
clip_dict = pickle.load(open("clip_containedclip.pickle", 'rb'))

# 实体列表读取
action_list = []
for action in open("english/action.txt").readlines():
    action = action.strip(line_break)
    action_list.append(action)
expression_list = []
for expression in open("english/expression.txt").readlines():
    expression = expression.strip(line_break)
    expression_list.append(expression)
event_list = []
for event in open("english/event.txt").readlines():
    event = event.strip(line_break)
    event_list.append(event)
character_list = []
for character in open("english/character.txt").readlines():
    character = character.strip(line_break)
    character_list.append(character)
interaction_list = []
for interaction in open("english/interaction.txt").readlines():
    interaction = interaction.strip(line_break)
    interaction_list.append(interaction)
relationship_list = []
for relationship in open("english/relationship.txt").readlines():
    relationship = relationship.strip(line_break)
    relationship_list.append(relationship)
scene_list = []
for scene in open("english/scene.txt").readlines():
    scene = scene.strip(line_break)
    scene_list.append(scene)

entity_dict = {        
            #"person": person_list,
            # "REQU": ['relation', 'relationship'],
            # "INTQU": ['interaction'],
}
spentity_dict = {
    "Character": character_list,
    "Interaction": interaction_list,
    "Relationship":relationship_list,
    "Event": event_list,
    "Action": action_list,
    "Scene": scene_list,
    "Expression":expression_list
}


action_list = []
for action in open("chinese/action.txt",encoding='utf-8').readlines():
    action = action.strip(line_break)
    action_list.append(action)
expression_list = []
for expression in open("chinese/expression.txt",encoding='utf-8').readlines():
    expression = expression.strip(line_break)
    expression_list.append(expression)
event_list = []
for event in open("chinese/event.txt",encoding='utf-8').readlines():
    event = event.strip(line_break)
    event_list.append(event)
character_list = []
for character in open("chinese/character.txt",encoding='utf-8').readlines():
    character = character.strip(line_break)
    character_list.append(character)
interaction_list = []
for interaction in open("chinese/interaction.txt",encoding='utf-8').readlines():
    interaction = interaction.strip(line_break)
    interaction_list.append(interaction)
relationship_list = []
for relationship in open("chinese/relationship.txt",encoding='utf-8').readlines():
    relationship = relationship.strip(line_break)
    relationship_list.append(relationship)
scene_list = []
for scene in open("chinese/scene.txt",encoding='utf-8').readlines():
    scene = scene.strip(line_break)
    scene_list.append(scene)

zentity_dict = {        
            #"person": person_list
            # "REQU": ['关系'],
            # "INTQU": ['交互'],
}
spzentity_dict = {
    "Character": character_list,
    "Interaction": interaction_list,
    "Relationship":relationship_list,
    "Event": event_list,
    "Action": action_list,
    "Scene": scene_list,
    "Expression":expression_list
}

special_type = ["REQU", "INTQU"]

## movie 2 id
movie_file = open("movie.csv","r")
reader = csv.reader(movie_file)
movie_list = {}
for item in reader:
    movie_list[item[1]] = item[0]
movie_file.close()

try: 
    # requests.get("http://" + requests.get('http://jump.mivc.top:8223/getip').json()['ip'] + ":18101", timeout=3.)
    # url_local = "http://" + requests.get('http://jump.mivc.top:8223/getip').json()['ip'] + ":18103/db/data/transaction/commit"
    # url = "http://" + requests.get('http://jump.mivc.top:8223/getip').json()['ip'] + ":18101/db/data/transaction/commit"
    requests.get("http://910.mivc.top" + ":18101", timeout=3.)
    url_local = "http://910.mivc.top" + ":18103/db/data/transaction/commit"
    url = "http://910.mivc.top" + ":18101/db/data/transaction/commit"
except:
    url_local = "http://localhost:8103/db/data/transaction/commit"
    url = "http://localhost:8101/db/data/transaction/commit"

# 子图数据库连接
print("----connecting to local database----")
print(url)
# url_local = "http://10.29.51.231:7474/db/data/transaction/commit"
login_local = "neo4j:123"
# graph_local = Graph(
#     "http://10.29.51.231:7474",
#     username="neo4j",
#     password="123"
# )
print("local database connected")
##远程数据库连接
print("----connecting to remote database----")
print(url_local)
# url = "http://10.208.40.10:7474/db/data/transaction/commit"
login = "neo4j:123"
