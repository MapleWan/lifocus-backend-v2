from flask_jwt_extended import get_jwt, jwt_required
from flask_restx import Resource
from app.controllers import auth_ns
from app.extension import redis_client
class LogoutResource(Resource):
    @auth_ns.doc(description="用户登出")
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        redis_client.set(jti, '', ex= 60 * 60) # 将token加入黑名单，同时设置清除时长：1 个小时
        return {'code': 200, 'message': '登出成功'}, 200