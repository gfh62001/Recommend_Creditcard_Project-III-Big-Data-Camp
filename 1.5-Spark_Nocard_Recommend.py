#no card
import pandas as pd
import json
import re
import pymongo
import operator
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import uuid
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


def load_data():
    client = pymongo.MongoClient(host='123.241.175.34', port=27017)
    client.admin.authenticate('root','1qaz@WSX3edc')
    db = client.Recommend_card
    coll = db.no_card
    mondata = list(coll.find())
    card_df = pd.DataFrame(mondata)
    card_df.set_index('卡名', inplace=True)
    del card_df['_id']
    return card_df
def insert_db(result):
    client = pymongo.MongoClient(host='123.241.175.34', port=27017)
    client.admin.authenticate('root','1qaz@WSX3edc')
    db = client.Recommend_card
    coll2 = db.no_card_result

def no_card_recommend(records):
    client = pymongo.MongoClient(host='123.241.175.34', port=27017)
    client.admin.authenticate('root', '1qaz@WSX3edc')
    connectdb= client.Recommend_card.no_card_result
    for record in records:
        data = eval(record[1])
        user_id = data["id"]
        a = data["卡活動"]
        b = data["保險"]
        c = data["加油"]
        d = data["行動支付"]
        e = data["超商"]
        f = data["交通"]
        g = data["電影"]
        h = data["旅遊機票飯店"]
        i = data["網購"]
        j = data["繳稅繳費"]
        k = data["現金回饋"]
        list01 = [a, b, c, d, e, f, g, h, i, j, k]
        for n, i in enumerate(list01):
            if i == '':
                list01[n] = 0
            else:
                list01[n] = int(i)
        INP = pd.DataFrame(columns=['卡活動', '保險', '加油', '行動支付', '超商', '交通', '電影', '旅遊機票飯店', '網購', '繳稅繳費', '現金回饋'])
        list02 = []
        if sum(list01) == 0:
            list02 = [0] * len(INP.columns)
            INP.loc[0] = list02

        else:
            for i in list01:
                l02 = i / sum(list01)
                list02.append(l02)
            INP.loc[0] = list02
        # 計算相似度
        x = cosine_similarity(card_df, INP)
        # print(x)
        a = list(x)
        b = sorted(a, reverse=True)
        blist = b[0:5]
        blist
        c = []
        if sum(blist) == 0:
            #print(card_df.index[[12, 77, 101, 121, 196]])
            result = {"id": user_id, "card1": card_df.index[12], "card2": card_df.index[77], "card3": card_df.index[101],
                      "card4": card_df.index[121], "card5": card_df.index[196]}
            connectdb.insert_one(result)
            #return result
    
      

    else:
        for i in blist:
            d = a.index(i)
            c.append(d)
        #print(list(card_df.index[c]))
        card = list(card_df.index[c])
        result = {"id": user_id, "card1": card[0], "card2": card[1], "card3": card[2], "card4": card[3],"card5": card[4]}
        connectdb.insert_one(result)
        #return result


if __name__ == "__main__":
    sc = SparkContext()
    ssc = StreamingContext(sc, 3)
    card_df=load_data()
    #raw_stream = KafkaUtils.createStream(ssc, "localhost:2182", "test3", {"nocard": 1})
    raw_stream = KafkaUtils.createStream(ssc, "kafka:9092", "test3", {"nocard": 1})
    #rec_result=raw_stream.map(no_card_recommend)
    rec_result=raw_stream.foreachRDD(lambda rdd:rdd.foreachPartition(no_card_recommend))
    #raw_stream.pprint()
    #rec_result.pprint()
    #print(rec_result)
    # Start it
    ssc.start()
    ssc.awaitTermination()

    
    
