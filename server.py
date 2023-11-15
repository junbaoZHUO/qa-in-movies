# -*- coding:utf-8 -*-
"""
    主调模块
"""
from flask import Flask, request, jsonify
import json
from flask_cors import CORS, cross_origin
from infer_main import answer_inference
from information import movie_list, zhuyi_dict, clip_dict
from find_path import find_clip, find_frame, find_graph, find_clip_set, find_frame_set, find_actor2frame
import random

# zhuyi_dict = {'爱国主义': ['tt0000001_001', 'tt0000001_002', 'tt0000001_003', 'tt0000001_004', 'tt0000001_005', 'tt0000001_006', 'tt0000001_007', 'tt0000001_008', 'tt0000001_009', 'tt0000001_010', 'tt0000001_011', 'tt0000001_012', 'tt0000001_013', 'tt0000001_014', 'tt0000001_015', 'tt0000001_016', 'tt0000001_017', 'tt0000001_018', 'tt0000001_019', 'tt0000001_020'], '乐观主义': ['tt0000002_001', 'tt0000002_002', 'tt0000002_003', 'tt0000002_004', 'tt0000002_005', 'tt0000002_006', 'tt0000002_007', 'tt0000002_008', 'tt0000002_009', 'tt0000002_010', 'tt0000002_011', 'tt0000002_012', 'tt0000002_013', 'tt0000002_014', 'tt0000002_015', 'tt0000002_016', 'tt0000002_017', 'tt0000002_018', 'tt0000002_019', 'tt0000002_020']}
# clip_dict = {'tt0000001_001':['tt7185492_jj_1_032_091', 'tt7185492_jj_4_551_644', 'tt7185492_jj_4_645_799'], 
# 'tt0000001_002':['tt7185492_jj_1_032_091', 'tt7185492_jj_4_551_644', 'tt7185492_jj_4_645_799'], 
# 'tt0000002_001':['tt7185492_jj_2_994_1101', 'tt7185492_jj_3_045_060', 'tt7185492_jj_3_069_085'], 
# 'tt0000002_002':['tt7185492_jj_4_867_878', 'tt7185492_jj_4_924_968', 'tt7185492_jj_3_001_013', 'tt7185492_jj_3_061_068'], 
# 'tt0000002_003':['tt7185492_jj_3_045_060', 'tt7185492_jj_3_069_085', 'tt7185492_jj_3_001_013', 'tt7185492_jj_3_061_068'], 
# 'tt0000002_004':['tt7185492_jj_3_045_060', 'tt7185492_jj_3_069_085', 'tt7185492_jj_4_867_878', 'tt7185492_jj_4_924_968']}

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/retrieve_clip', methods=['GET', 'POST'])
def clip():
    print(request)
    if request.method == 'GET':
        clip_id = request.args.get("clip_id")
        print(clip_id)
        # try:
        clip_info = find_clip(clip_id)
        return app.response_class(
            response=json.dumps({
                "clip_info": clip_info,
                "clip_id": clip_id}),
            mimetype='application/json'
        )
        # except:
        #     print("TIMEOUT ERROR, TRY AGAIN")

    return '{}'

@app.route('/retrieve_frame', methods=['GET', 'POST'])
def frame():
    print(request)
    if request.method == 'GET':
        frame_id = request.args.get("frame_id")
        print(frame_id)
        # try:
        frame_info = find_frame(frame_id)
        return app.response_class(
            response=json.dumps({
                "frame_info": frame_info,
                "frame_id": frame_id}),
            mimetype='application/json'
        )
        # except:
        #     print("TIMEOUT ERROR, TRY AGAIN")

    return '{}'

@app.route('/actor2img', methods=['GET', 'POST'])
def actor2img():
    print(request)
    if request.method == 'GET':
        actor_id = request.args.get("actor_id")
        if(type(actor_id) == str):
            actor_id = [actor_id]
        print(actor_id)
        # try:
        frame_id = find_actor2frame(actor_id)
        return app.response_class(
            response=json.dumps({
                "actor_id": actor_id,
                "frame_id": frame_id}),
            mimetype='application/json'
        )
        # except:
        #     print("TIMEOUT ERROR, TRY AGAIN")

    return '{}'

@app.route('/qa_in_movie', methods=['GET', 'POST'])
def qa():
    print(request)
    if request.method == 'GET':
        question = request.args.get("question")
        movie_id = request.args.get("movie_id")
        print(question)
        print(movie_id)
        try:
            answer, clip, cypher, frame, actor_info = answer_inference(movie_id, question)
        except:
            print("TIMEOUT ERROR, TRY AGAIN")

        if answer == 'question cannot be answered':
            return {}
        
        elif len(answer) == 0:
            return app.response_class(
                response=json.dumps({
                    "answer": [],
                    "clip_id": list(clip),
                    "cypher": cypher,
                    "frame_id": list(frame),
                    "actor_info": actor_info}),
                mimetype='application/json'
            )

        else:
            for k, v in answer.items():
                answer[k] = list(v)
            print(answer)
            return app.response_class(
                response=json.dumps({
                    "answer": list(answer.values()),
                    "clip_id": list(clip),
                    "cypher": cypher,
                    "frame_id": list(frame),
                    "actor_info": actor_info}),
                mimetype='application/json'
            )

    return '{}'

@app.route('/retrieve_in_movie', methods=['GET', 'POST'])
def retrieve():
    print(request)
    if request.method == 'GET':
        query = request.args.get("question")
        print(query)

        ll = 0
        if "乐观主义" in query:
            p_list = zhuyi_dict["乐观主义"]
            ll = len(p_list)
        elif "爱国主义" in query:
            p_list = zhuyi_dict["爱国主义"]
            ll = len(p_list)

        if ll > 0:
            video_id = random.choice(p_list)
            clips = clip_dict[video_id]

            cypher = find_clip_set(clips)
            frame_id = find_frame_set(clips)

            return app.response_class(
                response=json.dumps({
                    "answer": [],
                    "clip_id": [video_id],
                    "cypher": cypher,
                    "frame_id": list(frame_id),
                    "actor_info": []}),
                mimetype='application/json'
            )


        query = query.split('+')
        if len(query) == 1:
            query[0].split('"：') 
        if len(query) == 1:
            query[0].split('":') 
        else: 
            movie_id = movie_list[query[0].strip('"')]
            movie_id = movie_list[query[0].strip('“')]
            question = query[1]
        
        if len(query) == 1:
            query = query[0]
            if query.startswith('电影'):
                q = query[2:]
                for movie in movie_list.keys():
                    if q.startswith(movie):
                        movie_id = movie_list[movie]
                        question = q.lstrip(movie + '中')
                        break
            elif 'in movie ' in query or 'In movie ' in query:
                q = query.strip('?')
                q = q.lstrip('in movie ')
                q = q.lstrip('In movie ')
                for movie in movie_list.keys():
                    if q.startswith(movie):
                        movie_id = movie_list[movie]
                        question = q.lstrip(movie)
                        question = question.strip(', ')
                        break                

        print(question)
        print(movie_id)
        try:
            answer, clip, cypher, frame, actor_info = answer_inference(movie_id, question)
        except:
            print("TIMEOUT ERROR, TRY AGAIN")

        if answer == 'question cannot be answered':
            return {}
        
        elif len(answer) == 0:
            return app.response_class(
                response=json.dumps({
                    "answer": [],
                    "clip_id": list(clip),
                    "cypher": cypher,
                    "frame_id": list(frame),
                    "actor_info": actor_info}),
                mimetype='application/json'
            )

        else:
            for k, v in answer.items():
                answer[k] = list(v)
            print(answer)
            return app.response_class(
                response=json.dumps({
                    "answer": list(answer.values()),
                    "clip_id": list(clip),
                    "cypher": cypher,
                    "frame_id": list(frame),
                    "actor_info": actor_info}),
                mimetype='application/json'
            )

    return '{}'

@app.route('/query_graph', methods=['GET', 'POST'])
def query_graph():
    print(request)
    id_list = ("tt1699513", "tt7185492", "tt1438461", "tt4976086", "tt0085703", "tt1772230")
    if request.method == 'GET':
        
        data = find_graph(id_list)

        if len(data) > 0:
            return app.response_class(
                response=json.dumps({
                    "data": data}),
                mimetype='application/json'
            )


    return '{}'


app.run(host='0.0.0.0', port=8204, debug=True)
