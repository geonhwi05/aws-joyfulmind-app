from flask_restful import Resource
from flask import request
from recommend import recommend_songs

class RecommendResource(Resource):
    def get(self):
        emotion = request.args.get('emotion')
        limit = request.args.get('limit', default=10, type=int)
        
        if not emotion:
            return {'message': 'Emotion cannot be blank!'}, 400
        
        supported_emotions = ['슬픔', '기쁨', '분노', '공포', '놀람', '극혐']
        
        if emotion not in supported_emotions:
            return {'message': f'Emotion {emotion} not supported for now.'}, 400
        
        songs = recommend_songs(emotion, limit=limit)
        
        if not songs:
            return {'message': 'No songs found for the given emotion.'}, 404
        
        return {'emotion': emotion, 'songs': songs}, 200
