from passlib.hash import pbkdf2_sha256

class Config:
    SALT = "your_salt_value"

def hash_password(original_password):
    # 원본 비밀번호에 SALT 추가
    original_password = original_password + Config.SALT
    # 비밀번호 해싱
    password = pbkdf2_sha256.hash(original_password)
    return password

def check_password(original_password, hashed_password):
    # 원본 비밀번호에 SALT 추가
    original_password = original_password + Config.SALT
    # 비밀번호 검증
    return pbkdf2_sha256.verify(original_password, hashed_password)




#####################################################

hashed_password = hash_password('1234')
print("Hashed password:", hashed_password)

# 저장된 해시된 비밀번호와 비교
check = check_password('1234', hashed_password)
print("Password check result:", check)