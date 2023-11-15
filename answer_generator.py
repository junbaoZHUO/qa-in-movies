# -*- coding:utf-8 -*-
"""
    答案生成，可视化cypher语句生成模块
"""
from information import url, login, line_break
from post_cypher import QueryCypher
import re
from find_path import find_actor, find_character_clips


class Path2Answer:
    def __init__(self):
        self.__cypher = ""
        self.cypher = ""

    def __match_node__(self, movie, paths):
        """
        查询符合要求的尾实体属性值
        :return: 返回查询结果，即尾实体属性值
        """
        print("-----enter node match section-----")
        match_line = "MATCH p=(m:Movie)--(n:Clip)"
        where_line = ""
        return_line = ""
        return_phrase = ""
        return_cnt = 0

        return_frame = ""
        frame_type = {"Expression": 0, "Action": 0, "Interaction": 0, "Character": 0, "Event":0, "Scene":0}

        entity_name_list = []
        entity_match_list = []
        character_cnt = 0

        entity_sum_cnt = 0
        path_cnt = 0
        for path in paths:
            # match
            match_line = match_line + ",p" + str(path_cnt) + "="
            # if path[0]["type"] in ["Relationship", "Action", "Expression", "Interaction"]:
            #     match_line = match_line + "(c:Character)--"
            return_line = return_line + ",p" + str(path_cnt)
            entity_cnt = 0
            for entity in path:
                entity_sum_cnt = entity_sum_cnt + 1
                cmp = entity["type"] + entity["entity"]
                if cmp in entity_name_list:
                    match_phrase = entity_match_list[entity_name_list.index(cmp)]
                else:
                    if entity['type'] == "Character":
                        character_cnt = character_cnt + 1
                    match_phrase = "(a" + str(path_cnt) + "a" + str(entity_cnt) + ":" + entity["type"] + ")--"
                    entity_name_list.append(cmp)
                    entity_match_list.append(match_phrase)
                    if entity['type'] in ["Character", "Expression", "Interaction", "Action", "Event", "Scene"]:
                        frame_type[entity['type']] = frame_type[entity['type']] + 1
                    # where & return
                    property_type = "name" if entity["type"] in ["Movie", "Character", "Actor"] else "value"
                    # 若为疑问词
                    if re.match("^(wh(at|o|ich|ere))", entity["entity"], re.I) or \
                            re.match("^(什么|哪些|谁|角色|动作|事件|表情|交互|关系|场景)", entity["entity"], re.I):
                        return_phrase = return_phrase + ",a" + str(path_cnt) + "a" + str(
                            entity_cnt) + "." + property_type
                        return_cnt = return_cnt + 1
                    # 若非疑问词
                    else:
                        where_line = where_line + " AND a" + str(path_cnt) + "a" + str(entity_cnt) + "." + \
                                     property_type + "=~'(?i)" + entity["entity"] + "'"
                match_line = match_line + match_phrase
                entity_cnt = entity_cnt + 1
            match_line = match_line[:-2]
            if entity["type"] != ["Actor"]: #and entity_cnt > 1:
                match_line = match_line + "--(n:Clip)"
            path_cnt = path_cnt + 1
        # if character_cnt > 1:
        #     match_line = match_line + ",(m)--(a0a0)"
        cnt = 0
        # for k, v in character2actor.items():
        #     match_line = match_line + ",(" + k + ":Character)-[rr" + str(cnt) + "]-(ac" + str(cnt) + ":Actor)"
        #     return_phrase = return_phrase + ",ac" + str(cnt) + ".name"
        #     cnt = cnt + 1
        self.__cypher = match_line + line_break +\
                        "WHERE m.id='" + movie + "'" + where_line + line_break + \
                        "RETURN n.id" + return_frame + ",p" + return_line + return_phrase
        print("----生成的cypher查询语句：" + line_break + self.__cypher)
        print("----Querying Remote Database: It may take some time")
        res = QueryCypher(url, login, self.__cypher)
        if len(res["results"][0]["data"]) == 0:
            self.__cypher = match_line + ", (m)--(a0a0)" + line_break +\
                        "WHERE m.id='" + movie + "'" + where_line + line_break + \
                        "RETURN n.id" + return_frame + ",p" + return_line + return_phrase
            res = QueryCypher(url, login, self.__cypher)
        visual_ans = res
        # 结果处理
        ans = {}
        clip_set = set()
        if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
            if return_cnt > 0:
                for i in range(-cnt - 1, -cnt - return_cnt - 1, -1):
                    res_type = res["results"][0]["columns"][i]
                    ans[res_type] = {res["results"][0]["data"][0]["row"][i]}
                    for j in range(1, len(res["results"][0]["data"])):
                        (ans[res_type]).add(res["results"][0]["data"][j]["row"][i])
            for r in res["results"][0]["data"]:
                clip_set.add(r["row"][0])

        # 若查询为空
        if len(clip_set) == 0:
            ans = "question cannot be answered" if entity_sum_cnt != character_cnt else {}
            print("\n----enter character re-query section----")
            clip_res = find_character_clips(paths, movie)
            if (len(clip_res["results"]) != 0) and (len(clip_res["results"][0]["data"]) != 0):
                for r in clip_res["results"][0]["data"]:
                    clip_set.add(r["row"][0])

        # frame_id
        frame_id = set()
        for k in ["Expression", "Action", "Interaction", "Character"]:
            id_list = set()
            if frame_type[k] > 0:
                for r in res["results"][0]["data"]:
                    for node in r["graph"]["nodes"]:
                        if k in node["labels"]:
                            id_list.add(int(node["id"]))
                id_list = list(id_list)
                print("\n----keyframe query section----")
                self.__cypher = "MATCH (n:Clip)--(k:Keyframe)--(a:" + k + ")" + line_break +\
                                "WHERE n.id in " + str(list(clip_set)) + " and id(a) in " + str(id_list) + line_break +\
                                "RETURN k.id LIMIT 100"
                print("----生成的cypher查询语句：" + line_break + self.__cypher)
                print("----Querying Remote Database: It may take some time")
                res = QueryCypher(url, login, self.__cypher)
                if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
                    for r in res["results"][0]["data"]:
                        frame_id.add(r["row"][0])
                if len(frame_id) > 0:
                    break
        if len(frame_id) == 0:
            for k in ["Event", "Scene"]:
                id_list = set()
                if frame_type[k] > 0:
                    for r in res["results"][0]["data"]:
                        for node in r["graph"]["nodes"]:
                            if k in node["labels"]:
                                id_list.add(int(node["id"]))
                    id_list = list(id_list)
                    print("\n----keyframe query event and scene----")
                    self.__cypher = "MATCH (k:Keyframe)--(n:Clip)--(a:" + k + ")" + line_break +\
                                    "WHERE n.id in " + str(list(clip_set)) + " and id(a) in " + str(id_list) + line_break +\
                                    "RETURN k.id LIMIT 100"
                    print("----生成的cypher查询语句：" + line_break + self.__cypher)
                    print("----Querying Remote Database: It may take some time")
                    res = QueryCypher(url, login, self.__cypher)
                    if (len(res["results"]) != 0) and (len(res["results"][0]["data"]) != 0):
                        for r in res["results"][0]["data"]:
                            frame_id.add(r["row"][0])
                    if len(frame_id) > 0:
                        break

        print("\n----enter actor info query section----")
        actor_info = find_actor(paths, ans, movie)

        return ans, clip_set, visual_ans, frame_id, actor_info

    def get_answer(self, movie, paths):
        """
        获得问题的查询结果
        :param: movie的ttconst
        :param: 实体列表
        :return: 返回输入问题的答案
        """
        if len(paths) > 0:
            ans, clip_set, visual_ans, frame_id, actor_info = self.__match_node__(movie, paths)
        else:
            raise ValueError("path parsing error")
        return ans, clip_set, visual_ans, frame_id, actor_info
