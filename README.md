# QA in movies

事理图谱的中英文问答

## Install
```
conda create -n qa_transformer python=3.6
conda activate qa_transformer
pip install -r requirements.txt
```

## Pretrained models
若可以翻墙
```shell
python -m spacy download en_core_web_sm

python -m spacy download zh_core_web_sm
```

不能翻墙
```shell
# en_core_web_sm：
pip --default-timeout=10000 install https://github.com.cnpmjs.org/explosion/spacy-models/releases/download/en_core_web_sm-2.3.0/en_core_web_sm-2.3.0.tar.gz
# 中文支持
# zh_core_web_sm:
pip --default-timeout=10000 install https://github.com.cnpmjs.org/explosion/spacy-models/releases/download/zh_core_web_sm-2.3.0/zh_core_web_sm-2.3.0.tar.gz
pip install jieba
pip install pkuseg
```

## Demo
```shell
python infer_main.py
```

## FLASK服务
```shell
python server.py
```

输入请求
```
requests.get('http://${910ip}:18204/qa_in_movie?movie_id=' + movie_id + "&question=' + question).json()
requests.get('http://${910ip}:18204/retrieve_in_movie?question=' + question).json()
```
对于检索服务，输入格式为电影名+问题
```
返回数据结构为json文件
```
{
    "answer": list, #答案列表list
    "clip_id": list, #相关clip的列表
    "cypher": json, #json文件（字典），用于可视化，查询路径上图谱内容存放于"graph"键值
}
```

## Related Works
spacy
