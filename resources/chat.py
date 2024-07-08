from datetime import datetime
import json
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
import joblib
from mysql_connection import get_connection
from mysql.connector import Error
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import pandas as pd


class ChatBot(Resource):
    # 클래스 변수로 모델과 데이터셋을 로드
    sbert_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
    # sbert_model = joblib.load('./sbert_model/sbert_sbert_model.pkl')
    df = pd.read_csv('./data/combined_data.csv')
    df['embedding'] = df['embedding'].apply(json.loads)

    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        message = request.json.get('message')

        if not message:
            return {'result': 'fail', 'error': 'No message provided'}, 400

        # 유저가 입력한 문장을 벡터라이징
        embedding = self.sbert_model.encode(message)
        # 입력한 메시지의 유사도를 확인하여 가장 유사한 답변을 제시
        self.df['similarity'] = self.df['embedding'].map(lambda x: cosine_similarity([embedding], [x]).squeeze())
        answer_row = self.df.loc[self.df['similarity'].idxmax()]
        answer = answer_row['챗봇']  # assuming '챗봇' column contains the responses

        timestamp = datetime.now().isoformat()

        return {'result': 'success', 'answer': answer, 'timeStamp': timestamp}