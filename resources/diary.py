from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error

class DiaryListResource(Resource):
    
    # 메모 생성하는 함수
    # JWT 토큰이 헤더에 있어야지만 이 API를 실행할수 있다는 뜻
    # JWT 토큰이 필수!!! == 로그인 한 유저만 이 API 실행 가능.
    @jwt_required()
    def post(self) :
        # 1. 클라이언트가 보내준 데이터가 있으면 그 데이터를 받아준다.
        data = request.get_json()
        # 1-1. 헤더의 JWT 토큰이 있으면, 토큰 정보도 받는다.
        userId = get_jwt_identity()
        # 2. 이 정보를 DB에 저장한다.
        try:
            ### 1. DB에 연결
            connection = get_connection()
            ### 2. 쿼리문 만들기
            query = '''insert into diary
                        (userId, title, content, date)
                        values
                        (%s, %s, %s, %s);'''
            ### 3. 쿼리에 매칭되는 변수 처리 => 튜.플.로.
            record = (userId, data['title'], data['content'], data['date'])
            ### 4. 커서를 가져온다.
            cursor = connection.cursor()
            ### 5. 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)
            ### 6. DB에 완전히 반영하기 위해서는 commit 한다.
            connection.commit()
            ### 7. 자원 해제
            cursor.close()
            connection.close()
        # 4. 클라이언트에 응답
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success'}
    
    # 메모 조회하는 함수
    @jwt_required()
    def get(self) :
        
        # 1. 클라이언트가 보낸 데이터가 있으면
        #    받아준다.
        offset = request.args.get('offset', default=0, type=int)
        limit = request.args.get('limit', default=25, type=int)

        # 1-2 JWT 토큰에서 유저아이디를 가져온다
        userId = get_jwt_identity()
        
        # 2. DB로 부터 데이터를 가져온다.
        try :
            
            connection = get_connection()

            query = '''
                    SELECT *
                    FROM diary
                    WHERE userId = %s
                    LIMIT %s, %s;'''
            record = (userId, offset, limit)

            # 딕셔너리 트루 파라미터를 설정하여 데이터를 딕셔너리로 받는다
            cursor = connection.cursor(dictionary=True)
        
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            #print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close
            return {'result' : 'fail', 'error' : str(e)}, 500
        # 3. 클라이언트에 json으로 만들어서 응답한다.
        i = 0
        for row in result_list :
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            result_list[i]['date'] = row['date'].isoformat()
            i = i + 1
        return {'result' : 'success', 'item' : result_list, 'count' : len(result_list)}
    
class DiaryResourece(Resource) :
    # 메모 수정하는 API
    @jwt_required()
    def put(self, diaryId) :
        
        data = request.get_json()
        userId = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''update diary
                    set title=%s, date = %s, content = %s
                    where id = %s and userId = %s;'''
            record = (data['title'],
                      data['date'],
                      data['content'],
                      diaryId, userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()            
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close
            return {'result' : 'fail', 'error' : str(e)}, 500

        return {'result' : 'success'}

    # 메모 1개만 가져오는 API
    @jwt_required()
    def get(self, diaryId) :
        # 1. 클라이언트로부터 데이터를 받는다.     
        userId = get_jwt_identity()
        # 2. DB로 부터 데이터를 가져온다.
        try:
            connection = get_connection()
            # '''++''' 로 작성했기에 recode = ()는 안써도 된다
            query = '''
                    select *
                    from diary
                    where id =%s and userid = %s;'''
            record = (diaryId,userId)
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
            return {'result': 'fail',
                    'error': str(e)}, 500
        
        
        # 3. 응답할 데이터를 json 으로 만든다
        i = 0
        for row in result_list :
            result_list[i]['createdAt'] = row['createdAt'].isoformat()
            result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
            result_list[i]['date'] = row['date'].isoformat()
            i = i + 1

        if len(result_list) == 1:
            # 2-2. 내 레시피인지 확인한다.
            if result_list[0]['userId'] == userId :
                return {'item' : result_list[0],
                        'result' : 'success'}
            else :
                return {'result': 'fail'}, 401
        else :
            return {'result': 'fail',
                    'error': '해당 아이디는 존재하지 않습니다.'}
        
    # 메모 삭제하는 API
    @jwt_required()
    def delete(self, diaryId) :
        userId = get_jwt_identity()

        try:
            connection = get_connection()
            query = '''delete from diary
                    where id = %s and userId = %s;'''
            record = (diaryId, userId)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close
            return {'result' : 'fail', 'error' : str(e)}, 500
        return {'result' : 'success'}