import serverless_wsgi
import logging
from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserNicknameChangeResource,UserPasswordChangeResource,UserProfileResource, UserRegisterResource, UserLoginResource, UserLogoutResource
from resources.recommend import RecommendResource
from resources.diary import DiaryListResource, DiaryRangeResource, DiaryResource
from resources.user import jwt_blacklist

app = Flask(__name__)
app.config.from_object('config.Config')
jwt = JWTManager(app)

# 예외 로깅 설정
logging.basicConfig(level=logging.ERROR)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)

api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')
api.add_resource(RecommendResource, '/recommend')
api.add_resource(DiaryListResource, '/diary')
api.add_resource(DiaryResource, '/diary/<int:diaryId>')
api.add_resource(UserPasswordChangeResource,'/user/updatedpwd')
api.add_resource(UserNicknameChangeResource,'/user/updatednickname')
api.add_resource(UserProfileResource,'/user/profile')
api.add_resource(DiaryRangeResource, '/diary/range')

# 모든 예외를 처리하는 핸들러 추가
@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"An error occurred: {e}", exc_info=True)  # 예외 정보 포함
    return jsonify(error=str(e)), 500

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

if __name__ == '__main__':
    app.run(debug=True)
