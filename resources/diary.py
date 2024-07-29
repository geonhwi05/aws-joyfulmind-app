from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error

class DiaryListResource(Resource):
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            query = '''INSERT INTO diary (userId, title, content, createdAt)
                       VALUES (%s, %s, %s, NOW());'''
            record = (userId, data['title'], data['content'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        
        return {'result': 'success'}

    @jwt_required()
    def get(self):
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            query = '''SELECT * FROM diary WHERE userId = %s;'''
            record = (userId,)
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        for row in result_list:
            row['createdAt'] = row['createdAt'].isoformat()
            row['updatedAt'] = row['updatedAt'].isoformat()
        
        return {'result': 'success', 'items': result_list, 'count': len(result_list)}

class DiaryResource(Resource):

    @jwt_required()
    def put(self, diaryId):
        data = request.get_json()
        userId = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''UPDATE diary SET title = %s, content = %s, updatedAt = NOW()
                       WHERE id = %s AND userId = %s;'''
            record = (data['title'], data['content'], diaryId, userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return {'result': 'success'}

    @jwt_required()
    def get(self, diaryId):
        userId = get_jwt_identity()
        
        try:
            connection = get_connection()
            query = '''SELECT * FROM diary WHERE id = %s AND userId = %s;'''
            record = (diaryId, userId)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        if len(result_list) == 1:
            result = result_list[0]
            result['createdAt'] = result['createdAt'].isoformat()
            result['updatedAt'] = result['updatedAt'].isoformat()
            return {'item': result, 'result': 'success'}
        else:
            return {'result': 'fail', 'error': '해당 아이디는 존재하지 않습니다.'}

    @jwt_required()
    def delete(self, diaryId):
        userId = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''DELETE FROM diary WHERE id = %s AND userId = %s;'''
            record = (diaryId, userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return {'result': 'success'}

class DiaryRangeResource(Resource):

    @jwt_required()
    def get(self):
        userId = get_jwt_identity()
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        try:
            connection = get_connection()
            query = '''SELECT * FROM diary WHERE userId = %s AND createdAt BETWEEN %s AND %s;'''
            record = (userId, start_date, end_date)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
        except Error as e:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            return {'result': 'fail', 'error': str(e)}, 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        for row in result_list:
            row['createdAt'] = row['createdAt'].isoformat()
            row['updatedAt'] = row['updatedAt'].isoformat()

        return {'result': 'success', 'items': result_list, 'count': len(result_list)}