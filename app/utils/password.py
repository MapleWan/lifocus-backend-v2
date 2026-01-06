import secrets
import hashlib
import re

password_pattern = r"^(?=.*[a-zA-Z])(?=.*\d).{8,}$"

def valid_password(password):
    # Define a regex pattern for password rules
    pattern = password_pattern
    # Check if the password matches the pattern
    if re.match(pattern, password) is not None:
        return True
    return False


# 哈希加密示例
def hash_password(password):
    valid_password(password)
    # 生成随机盐值
    salt = secrets.token_hex(16)
    # 加盐哈希
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 8070)
    return salt, hashed.hex()

# 验证密码
def verify_password(stored_password, salt, provided_password):
    hash_attempt = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt.encode('utf-8'), 8070)
    return hash_attempt.hex() == stored_password

def verify_password_with_salt(stored_password_with_salt, provided_password):
    salt = stored_password_with_salt[:32]
    stored_password = stored_password_with_salt[32:]
    return verify_password(stored_password, salt, provided_password)
