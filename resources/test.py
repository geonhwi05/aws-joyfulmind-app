from flask_restful import Resource

class test(Resource):

    def get(self):
        return {"result" :  "안녕하세요"}
