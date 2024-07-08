import serverless_wsgi

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegisterResource,UserLoginResource,UserLogoutResource
from resources.chat import ChatBot
from resources.diary import DiaryListResource,DiaryResourece


from resources.user import jwt_blacklist

app = Flask(__name__)
app.config.from_object('config.Config')
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader 
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist
api = Api(app)

api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource,'/user/logout')
api.add_resource(ChatBot, '/chatting')
api.add_resource(DiaryListResource, '/diary/<int:diaryId>')
api.add_resource(DiaryResourece, '/diary/<int:diaryId>')

def handler(event, context):
    return serverless_wsgi.handle_request(app,event,context)

if __name__== '__main__':
    app.run(debug=True)
