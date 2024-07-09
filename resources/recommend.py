from flask_restful import Resource
from flask import request
from recommend import recommend_songs

class RecommendResource(Resource):
    def get(self):
        emotion = request.args.get('emotion')
        limit = request.args.get('limit', default=10, type=int)
        
        if not emotion:
            return {'message': 'Emotion cannot be blank!'}, 400
        
        songs = recommend_songs(emotion, limit)
        return {'songs': songs}, 200
