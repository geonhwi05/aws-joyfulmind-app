from email_validator import EmailNotValidError, validate_email
from flask import request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, get_jwt_identity
from mysql.connector import Error
from flask_restful import Resource
from datetime import datetime
from mysql_connection import get_connection
from utils import check_password, hash_password
from werkzeug.utils import secure_filename
import boto3


class UserRegisterResource(Resource):
    def post(self):
        data = request.get_json()

        # 데이터 유효성 검사
        if not data.get('email') or not data.get('nickname') or not data.get('password') or not data.get('gender') or not data.get('birthDate'):
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

        # 생년월일 유효성 검사 및 변환
        try:
            birthDate = datetime.strptime(data['birthDate'], '%Y-%m-%d').date()
        except ValueError:
            return {'result': 'fail', 'message': 'Invalid birthDate format, should be YYYY-MM-DD'}, 400

        # DB에 저장
        try:
            connection = get_connection()
            query = '''INSERT INTO user (email, password, nickname, gender, birthDate)
                       VALUES (%s, %s, %s, %s, %s);'''
            record = (data['email'], password, data['nickname'], data['gender'], birthDate)
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
class UserLoginResource(Resource):
    def post(self):
        # 1. 클라이언트로부터 데이터를 받는다.
        data = request.get_json()
        if 'email' not in data or 'password' not in data:
            return {'result': 'fail'}, 400
        
        if data['email'].strip() == '' or data['password'].strip() == '':
            return {'result': 'fail'}, 400

        # 2. DB로부터 이메일에 해당하는 유저 정보를 가져온다.
        try:
            connection = get_connection()
            query = '''SELECT *
                       FROM user
                       WHERE email = %s;'''
            record = (data['email'],)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500

        # 3. 회원인지 확인한다.
        if not result_list:
            return {'result': 'fail'}, 401

        # 4. 비밀번호를 체크한다.
        is_correct = check_password(data['password'], result_list[0]['password'])
        if not is_correct:
            return {'result': 'fail'}, 401

        # 5. 유저 아이디를 가져온다.
        user_id = result_list[0]['id']

        # 6. JWT 토큰을 만든다.
        access_token = create_access_token(identity=user_id)

        # 7. 클라이언트에 응답한다.
        return {'result': 'success', 'accessToken': access_token}

# 로그아웃    
jwt_blacklist = set()
class UserLogoutResource(Resource):
    @jwt_required()
    def delete(self):
        jti = get_jwt()['jti']
        jwt_blacklist.add(jti)
        return {'result': 'success'}

# 비밀번호 수정
class UserPasswordChangeResource(Resource):
    @jwt_required()
    def put(self):
        data = request.get_json()

        # 필요한 데이터 필드 확인
        if 'oldPassword' not in data or 'newPassword' not in data:
            return {'result': 'fail', 'message': 'Missing required fields'}, 400

        # 새 비밀번호 길이 유효성 검사
        if len(data['newPassword']) < 4 or len(data['newPassword']) > 12:
            return {'result': 'fail', 'message': 'Password must be between 4 and 12 characters'}, 400

        user_id = get_jwt_identity()

        try:
            # 데이터베이스 연결 및 현재 비밀번호 확인
            connection = get_connection()
            query = '''SELECT password FROM user WHERE id = %s;'''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            if not result or not check_password(data['oldPassword'], result['password']):
                cursor.close()
                connection.close()
                return {'result': 'fail', 'message': 'Incorrect old password'}, 400

            # 새 비밀번호가 현재 비밀번호와 동일한지 확인
            if check_password(data['newPassword'], result['password']):
                cursor.close()
                connection.close()
                return {'result': 'fail', 'message': 'New password must be different from the old password'}, 400

            # 새 비밀번호 암호화 및 업데이트
            new_password = hash_password(data['newPassword'])
            query = '''UPDATE user SET password = %s WHERE id = %s;'''
            cursor.execute(query, (new_password, user_id))
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500

        return {'result': 'success', 'message': 'Password updated successfully'}

# 닉네임 수정
class UserNicknameChangeResource(Resource):
    @jwt_required()
    def put(self):
        data = request.get_json()

        if 'newNickname' not in data:
            return {'result': 'fail', 'message': 'Missing required fields'}, 400

        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''UPDATE user SET nickname = %s WHERE id = %s;'''
            cursor = connection.cursor()
            cursor.execute(query, (data['newNickname'], user_id))
            connection.commit()

            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500

        return {'result': 'success'}

# 프사 수정
class UserProfileImgChangeResource(Resource):

    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()

        # S3 버킷 설정
        S3_BUCKET = 'aws-joyfulmind-app-dev-serverlessdeploymentbucket-jez8xfu2g1hu'
        S3_REGION = 'ap-northeast-2'
        S3_BASE_URL = f'https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/'
        # boto3 S3 클라이언트 초기화
        s3_client = boto3.client('s3')

        if 'profileImage' not in request.files:
            return {'result': 'fail', 'error': '파일이 없습니다'}, 400

        file = request.files['profileImage']
        
        if file.filename == '':
            return {'result': 'fail', 'error': '선택된 파일이 없습니다'}, 400

        if file:
            filename = secure_filename(file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            s3_filename = f'user_{user_id}/profile.{file_extension}'
            try:
                s3_client.upload_fileobj(
                    file,
                    S3_BUCKET,
                    s3_filename,
                    ExtraArgs={'ACL': 'public-read'}
                )
                s3_file_url = S3_BASE_URL + s3_filename

                try:
                    connection = get_connection()
                    query = '''UPDATE user SET profileImage = %s WHERE id = %s;'''
                    cursor = connection.cursor()
                    cursor.execute(query, (s3_file_url, user_id))
                    connection.commit()

                    cursor.close()
                    connection.close()

                except Error as e:
                    if cursor is not None:
                        cursor.close()
                    if connection is not None:
                        connection.close()
                    return {'result': 'fail', 'error': str(e)}, 500

                return {'result': 'success', 'file_url': s3_file_url}
            except Exception as e:
                return {'result': 'fail', 'error': str(e)}, 500
        else:
            return {'result': 'fail', 'error': '파일 업로드 실패'}, 400

# 유저 프로필 정보
class UserProfileResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''SELECT email, nickname, gender, birthDate, profileImage FROM user WHERE id = %s;'''
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            cursor.close()
            connection.close()

            if result:
                # birthDate를 문자열로 변환
                result['birthDate'] = result['birthDate'].strftime('%Y-%m-%d')
                return {'result': 'success', 'user': result}, 200
            else:
                return {'result': 'fail', 'message': 'User not found'}, 404

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
