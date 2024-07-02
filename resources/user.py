from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from mysql.connector import Error
from flask_restful import Resource

from mysql_connection import get_connection
from utils import check_password, hash_password

class UserRegisterResource(Resource):
    def post(self):
        data = request.get_json()

        # 데이터 유효성 검사
        if not data.get('email') or not data.get('nickname') or not data.get('password') or not data.get('gender') or not data.get('age'):
            return {"result": "fail", "message": "Missing required fields"}, 400

        # 이메일 유효성 검사
        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return {"result": "fail", "error": str(e)}, 400

        # 비밀번호 길이 유효성 검사
        if len(data['password']) < 4 or len(data['password']) > 12:
            return {'result': 'fail', 'message': 'Password must be between 4 and 12 characters'}, 400



        # 비밀번호 암호화
        password = hash_password(data['password'])

        # DB에 저장
        try:
            connection = get_connection()
            query = '''INSERT INTO user (email, password,nickname, age, gender)
                       VALUES (%s, %s, %s, %s, %s);'''
            record = (data['email'], password,data['nickname'],data['age'],data['gender'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500

        # JWT 토큰 생성
        access_token = create_access_token(identity=user_id)
        
        return {"result": "success", "accessToken": access_token}
# 로그인    
class UserLoginResource(Resource) :
    def post(self) :
        
        # 1. 클라이언트로부터 데이터를 받는다.
        data = request.get_json()
        print(data)
        if 'email' not in data or 'password' not in data :
            return {'result' : 'fail'} , 400
        
        if data['email'].strip() == '' or data['password'].strip() == '':
            return {'result' : 'fail'} , 400

        # 2. DB로부터 이메일에 해당하는 유저 정보를 가져온다.
        try:
            connection = get_connection()
            query = '''select *
                    from user
                    where email = %s;'''
            record = (data['email'], )
            print(record)
            cursor = connection.cursor(dictionary=True)
            print(cursor)
            cursor.execute(query,record)
            print(cursor)
            result_list = cursor.fetchall()
            print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result':'fail','error':str(e)}, 500

        # 3. 회원인지 확인한다.
        if result_list == [] :
            return {'result' : 'fail'} , 401

        # 4. 비밀번호를 체크한다.
        # 유저가 입력한 비번 data['password']
        # DB에 암호화된 비번 result_lsit[0]['password']
        isCorrect = check_password(data['password'], result_list[0]['password'])
        if isCorrect != True :
            return {'result' : 'fail'} , 401

        # 5. 유저 아이디를 가져온다.
        user_id = result_list[0]['id']

        # 6. JWT 토큰을 만든다.
        # access_token = create_access_token(user_id, 
        #                                    expires_delta= datetime.timedelta(minutes= 3))
        access_token = create_access_token(user_id) 

        # 7. 클라이언트에 응답한다.
        
        return {'result' : 'success', 'accessToken':access_token}

# 로그아웃    
# 로그아웃 된 토큰을 저장할, set 을 만든다.
jwt_blacklist= set()
class UserLogoutResource(Resource):
    @jwt_required()
    def delete(self):
        
        jti = get_jwt()['jti']
        jwt_blacklist.add(jti)

        return {'result' : 'success'}