#spark+ py
#have card
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
    client.admin.authenticate('root', '1qaz@WSX3edc')
    db = client.Recommend_card
    coll = db.hold_card
    user_card_matrix_for_rec=coll.find()
    df=pd.DataFrame(list(user_card_matrix_for_rec))
    return df


# def insert_db(data):
#     client = pymongo.MongoClient(host='123.241.175.34', port=27017)
#     client.admin.authenticate('root', '1qaz@WSX3edc')
#     x = client.Recommend_card.no_card_result
#     x.insert_one(data)


def CF_Recommend_Item_Based(records):
    client = pymongo.MongoClient(host='123.241.175.34', port=27017)
    client.admin.authenticate('root', '1qaz@WSX3edc')
    connectdb= client.Recommend_card.no_card_result
    
    for record in records:
        data=eval(record[1])

        user_id = data["id"]
        del data["id"]
        my_card = []
        for i,y in data.items():
            my_card.append(y)    
        del df['_id']
        df_T=df.T
        card_sim=cosine_similarity(df_T,df_T)
        indices = pd.Series(df_T.index)   #所有卡series
        card_index_list=[indices[indices == name].index[0] for name in my_card]  #找出各卡index
        weighted_card_rec=np.zeros(len(df_T.index))   #創全0且為卡片數量長度的array
        for  i in card_index_list:
            weighted_card_rec +=card_sim[i]           #將持有卡於其他卡的相似度相加成推薦權重
        weighted_score=pd.Series(weighted_card_rec).sort_values(ascending = False)
        top_5_indexes=weighted_score.iloc[len(my_card):len(my_card)+5].index
        rec_card=[]
        for i in top_5_indexes:
            rec_card.append(indices[i])
        result = {"id":user_id,"card1":rec_card[0],"card2":rec_card[1],"card3":rec_card[2],"card4":rec_card[3],"card5":rec_card[4]}
        connectdb.insert_one(result)
        #return result
    client.close()
if __name__ == "__main__":
    sc = SparkContext()
    ssc = StreamingContext(sc, 6)
    df=load_data()
    raw_stream = KafkaUtils.createStream(ssc, "localhost:2182", "test3", {"havecard": 1})
    #raw_stream = KafkaUtils.createStream(ssc, "kafka:9092", "test3", {"havecard": 1})
    rec_result=raw_stream.foreachRDD(lambda rdd:rdd.foreachPartition(CF_Recommend_Item_Based))
    raw_stream.pprint()
    #rec_result.pprint()
    #print(rec_result)
    # Start it
    ssc.start()
    ssc.awaitTermination()