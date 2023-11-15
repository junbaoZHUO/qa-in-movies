"""
    精确查找
"""
import spacy
from spacy_lookup import Entity
import numpy as np
# from sentence_transformers import SentenceTransformer, util
# import torch
# from termcolor import colored
# import itertools
from information import entity_dict
from information import spentity_dict
from information import zentity_dict
from information import spzentity_dict
import copy
#from information import val_dict



# from information import remodel_dict
# import QperML

class QueryNer:
    def __init__(self):
        """
        初始化
        question: 待处理问句
        """
          # 原版spacy模型
          # 替换词表的spacy模型

        self.__dict_keys = entity_dict.keys()
        self.__spdict_keys = spentity_dict.keys()

        self.__enlp = spacy.load('en_core_web_sm')
        self.__enlp.remove_pipe('ner')
        for key, values in entity_dict.items():
            entity = Entity(keywords_list=values, label=key)
            self.__enlp.add_pipe(entity, name=key)
        self.__nlp = {}
        for key, values in spentity_dict.items():
            entity = Entity(keywords_list=values, label=key)
            self.__nlp[key] = copy.deepcopy(self.__enlp)
            self.__nlp[key].add_pipe(entity, name=key)
        
        self.__znlp = spacy.load('zh_core_web_sm')
        self.__znlp.remove_pipe('ner')
        for key, values in zentity_dict.items():
            entity = Entity(keywords_list=values, label=key)
            self.__znlp.add_pipe(entity, name=key)
        self.__nlp2 = {}
        for key, values in spzentity_dict.items():
            self.__nlp2[key] = spacy.load('zh_core_web_sm')
            self.__nlp2[key].remove_pipe('ner')
            for key1, values1 in zentity_dict.items():
                entity1 = Entity(keywords_list=values1, label=key1)
                self.__nlp2[key].add_pipe(entity1, name=key1)
            entity = Entity(keywords_list=values, label=key)
            self.__nlp2[key].add_pipe(entity, name=key)       


    def enorzh_question(self, question):
        self.__doc = question
        ch = question[0]
        if ('A'<=ch and ch<='Z')or('a'<=ch and ch<='z'):
            self.__isenglish = True
        else:
            self.__isenglish = False
        #print(self.__isenglish)
        return self.__isenglish
            
        

    def lookdoc(self):
        print()
        if self.__isenglish:
            print('english')
        else:
            print('中文')
        print(self.__doc)
        print()
        for token in self.__doc:
            print(token.text, token._.is_entity, token.ent_type_, token.dep_)
        print()
        for token in self.__doc:
            print(token.text, token.lemma_)
        print()
        

    def forward_ner(self, question):
        self.enorzh_question(question)
        nerlist = []
        countch = 0

        if self.__isenglish:
            self.__doc = self.__enlp(self.__doc)
            tempdoc = ""
            for token in self.__doc:
                if token._.is_entity:
                    nerlist.append({"entity":token.text,"type":token.ent_type_})
                    if token.ent_type_ == "Character":
                        countch = countch + 1
                else:
                    tempdoc = tempdoc + ' ' + token.text
            for key in self.__spdict_keys:
                if key in ["Interaction"] and (countch != 2):
                    continue
                #print(tempdoc)
                self.__doc = self.__nlp[key](tempdoc)
                tempdoc = ""
                for token in self.__doc:
                    if token._.is_entity:
                        nerlist.append({"entity":token.text,"type":token.ent_type_})
                        if token.ent_type_ == "Character":
                            countch = countch + 1
                    else:
                        tempdoc = tempdoc + ' ' + token.text
            #print(tempdoc)
        else:
            self.__doc = self.__znlp(self.__doc)
            # print()
            # for token in self.__doc:
                # print(token.text, token._.is_entity, token.ent_type_, token.dep_)
            # print()
            tempdoc = ""
            for token in self.__doc:
                if token._.is_entity:
                    nerlist.append({"entity":token.text,"type":token.ent_type_})
                    if token.ent_type_ == "Character":
                        countch = countch + 1
                else:
                    tempdoc = tempdoc + token.text
            for key in self.__spdict_keys:
                if key in ["Interaction","Relationship"] and (countch != 2):
                    continue
                # print(tempdoc)
                # print(self.__nlp2[key].pipe_names)
                self.__doc = self.__nlp2[key](tempdoc)
                # print()
                # for token in self.__doc:
                    # print(token.text, token._.is_entity, token.ent_type_, token.dep_)
                # print()
                tempdoc = ""
                for token in self.__doc:
                    if token._.is_entity:
                        nerlist.append({"entity":token.text,"type":token.ent_type_})
                        if token.ent_type_ == "Character":
                            countch = countch + 1
                    else:
                        tempdoc = tempdoc + token.text
            # print(tempdoc)
        return nerlist
       

if __name__=="__main__":
    # question = "载垣和桂良有什么交互？"
    question = "载垣和桂良有在交谈？"
    # question = "waht is the relation between Whip Whitaker Nicole？"
    # question = "Whip Whitaker lover prepares for flight is and Whip Whitaker the talk on the phone or talks to while Angry?"
    #question = "what movies is that?"
    # question = "载垣旁观了巴夏礼在皇帝登基时生气地在故宫里和同事桂良站在一起"

    test = QueryNer()
    nerlist = test.forward_ner(question)
    print(nerlist)
    #test.lookdoc()
