# -*- coding:utf-8 -*-
"""
    主调模块
"""
from functools import lru_cache
from information import line_break
from Qner import QueryNer
from find_path import LinkPath
from answer_generator import Path2Answer
parse_blk = QueryNer()
t2a_blk = Path2Answer()


# @lru_cache()
def answer_inference(movie, question):
    # NER,输入问题，输出所有识别实体
    nerlist = parse_blk.forward_ner(question)
    paths = LinkPath(nerlist)
    print(paths)
    # 答案生成
    # 输入电影ttconst, 问题提取的实体组，构成路径，进行查询
    ans, clip_set, visual_ans, frame_id, actor_info = t2a_blk.get_answer(movie, paths)
    return ans, clip_set, visual_ans, frame_id, actor_info


if __name__ == '__main__':
    question = open("question.txt", encoding="UTF-8", errors="ignore").readline()
    question = question.strip(line_break)
    print(question)
    movie = "tt1699513"
    answers, clip_set, visual_answer, frame_id, actor_info = answer_inference(movie, question)

    print("**the answer:")
    if type(answers) == str:
        print(answers)
    else:
        for v in answers.values():
            for i in v:
                print(i)

    print(clip_set)
    print(frame_id)

    input(actor_info)

    print("**json for visualization:")
    print(visual_answer)
