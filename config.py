class Config :

    HOST = 'yh-db.crc6smigwvow.ap-northeast-2.rds.amazonaws.com'
    DATABASE ='jm_db'
    DB_USER = 'jm_db_user'
    DB_PASSWORD='2105'
    
    SALT = '30sdjku39#921#123'

    # JWT 관련 변수 셋팅
    JWT_SECRET_KEY = 'djaiwnb,12850sksj'
    JWT_ACCESS_TOKEN_EXPIRES = False # 유효기간 되도록 만드는 작업(True로 만들면)
    PROPAGATE_EXCEPTIONS = True