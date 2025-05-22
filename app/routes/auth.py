from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.services.user_service import UserService
from app.models.user import User
from app import redis_client


auth_bp = Blueprint("Auth", "auth", url_prefix="/api/auth", description="Authentication endpoints")

@auth_bp.route("/register")
class RegisterResource(MethodView):
    @auth_bp.arguments(RegisterSchema)
    def post(self, user_data):
        user = UserService.register_user(user_data)
        if not user:
            return {"message": "Account/Email already registered"}, 409

        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        # Note:
        # Front end needs add "Bearer " before token
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": str(user.user_id),
                "account_name": user.account_name,
                "email": user.email,
                "preferred_currency": user.preferred_currency,
                "notification_opt_in": user.notification_opt_in
            }
        }, 201


@auth_bp.route("/login")
class LoginResource(MethodView):
    @auth_bp.arguments(LoginSchema)
    def post(self, credentials):
        user = UserService.authenticate(credentials["email"], credentials["password"])
        if not user:
            return {"message": "Invalid email or password"}, 401

        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        # Note:
        # Front end needs add "Bearer " before token
        # const token = localStorage.getItem("access_token")
        #   if (token) {
        #     config.headers.Authorization = `Bearer ${token}`
        #   }
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "user_id": str(user.user_id),
                "account_name": user.account_name,
                "email": user.email
            }
        }, 200

@auth_bp.route("/refresh")
class TokenRefreshResource(MethodView):
    @jwt_required(refresh=True)
    @auth_bp.doc(security=[{"BearerAuth": []}])
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)
        return {"access_token": new_access_token}, 200

@auth_bp.route("/me")
class MeResource(MethodView):
    @jwt_required()
    @auth_bp.doc(security=[{"BearerAuth": []}])
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return {"message": "User not found"}, 404

        return {
            "user_id": str(user.user_id),
            "account_name": user.account_name,
            "email": user.email,
            "preferred_currency": user.preferred_currency,
            "notification_opt_in": user.notification_opt_in,
            "risk_profile_level": user.risk_profile_level,
            "role": user.role
        }, 200

@auth_bp.route("/logout")
class LogoutResource(MethodView):
    @jwt_required()
    @auth_bp.doc(security=[{"BearerAuth": []}])
    def post(self):
        jti = get_jwt()["jti"]
        redis_client.setex(f"bl:{jti}", 3600 * 24, "revoked")  # block for 24h
        return {"message": "Successfully logged out"}, 200