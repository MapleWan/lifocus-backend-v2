from flask_restx import Resource, reqparse
from app.controllers import auth_ns
from app.models import User
from app.enums import LOGIN_ERROR_MESSAGE
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token, get_jwt_identity, jwt_required
from app.utils import verify_password

def generate_token(user_id):
    access_token = create_access_token(identity=str(user_id))
    refresh_token = create_refresh_token(identity=str(user_id))
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

class LoginResource(Resource):
    @jwt_required(refresh=True)
    @auth_ns.doc(description='用户token刷新')
    def get(self):
        try:
            current_user = get_jwt_identity()
            token = generate_token(current_user)
            decoded_token = decode_token(token['access_token']) # 解码access_token，用于获取过期时间
            return {
                'code': 200, 
                'message': '刷新成功', 
                'data': {
                    **token,
                    'expire_time': decoded_token['exp'] * 1000 # 过期时间，单位 毫秒时间戳 -> 秒时间戳
                }
            }
        except Exception as e:
            return {'code': 500, 'message': f'{LOGIN_ERROR_MESSAGE["COMMON_ERROR"]}: {str(e)}'}, 500

    @auth_ns.doc(description='用户登录')
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('username', type=str, required=True, help='用户名')
            parser.add_argument('password', type=str, required=True, help='密码')
            args = parser.parse_args()

            user = User.get_user_by_username(args['username'])
            if not user:
                return {'code': 400, 'message': LOGIN_ERROR_MESSAGE['USER_NOT_FOUND']}, 400
            if not verify_password(user.password, user.salt, args['password']):
                return {'code': 400, 'message': LOGIN_ERROR_MESSAGE['PASSWORD_ERROR']}, 400
            
            token = generate_token(user.id)
            decoded_token = decode_token(token['access_token']) # 解码access_token，用于获取过期时间
            return {
                'code': 200,
                'message': '登录成功',
                'data': {
                    **token,
                    'expire_time': decoded_token['exp'] * 1000 # 过期时间，单位 毫秒时间戳 -> 秒时间戳
                }
            }
        except Exception as e:
            return { 'code': 500, 'message': f'{LOGIN_ERROR_MESSAGE['COMMON_ERROR']}: {str(e)}'}, 500
