from flask_smorest import Blueprint
from flask import make_response, request
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
        resp = make_response({
            "access_token": access_token,
            "user": {
                "user_id": str(user.user_id),
                "account_name": user.account_name,
                "email": user.email,
                "preferred_currency": user.preferred_currency,
                "notification_opt_in": user.notification_opt_in
            }
        })

        # Store the refresh token in an HTTP-only cookie
        # This enhances security by preventing JavaScript access (XSS protection)
        resp.set_cookie(
            "refresh_token",  # Cookie name
            refresh_token,  # Cookie value
            httponly=True,  # Prevent JavaScript access (mitigates XSS)
            secure=False,  # Set to True in production (HTTPS only)
            samesite='Lax',  # Controls cross-site sending behavior; use 'None' + secure=True for full cross-origin
            max_age=7 * 24 * 60 * 60,# Cookie lifespan in seconds (7 days)
            path="/api/auth/refresh",
        )

        return resp

@auth_bp.route("/login")
class LoginResource(MethodView):
    @auth_bp.arguments(LoginSchema)
    def post(self, credentials):
        user = UserService.authenticate(credentials["email"], credentials["password"])
        if not user:
            return {"message": "Invalid email or password"}, 401

        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        resp = make_response({
            "access_token": access_token,
            "user": {
                "user_id": str(user.user_id),
                "account_name": user.account_name,
                "email": user.email,
                "preferred_currency": user.preferred_currency,
                "notification_opt_in": user.notification_opt_in
            }
        })

        # Store the refresh token in an HTTP-only cookie
        # This enhances security by preventing JavaScript access (XSS protection)
        resp.set_cookie(
            "refresh_token",  # Cookie name
            refresh_token,  # Cookie value
            httponly=True,  # Prevent JavaScript access (mitigates XSS)
            secure=False,  # Set to True in production (HTTPS only)
            samesite='Lax',  # Controls cross-site sending behavior; use 'None' + secure=True for full cross-origin
            max_age=7 * 24 * 60 * 60,  # Cookie lifespan in seconds (7 days)
            path="/api/auth/refresh",
        )

        # Note:
        # Front end needs add "Bearer " before token
        # const token = localStorage.getItem("access_token")
        #   if (token) {
        #     config.headers.Authorization = `Bearer ${token}`
        #   }
        return resp


@auth_bp.route("/refresh")
class TokenRefreshResource(MethodView):
    @jwt_required(refresh=True)
    @auth_bp.doc(security=[{"BearerAuth": []}])
    def post(self):
        # ✅ 新增：调试日志
        print(f"Refresh token request cookies: {request.cookies}")
        print(f"Refresh token from cookie: {request.cookies.get('refresh_token')}")

        current_user_id = get_jwt_identity()
        print(f"Current user ID from refresh token: {current_user_id}")

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
        resp = make_response({"message": "Successfully logged out"})
        resp.set_cookie("refresh_token", "", expires=0, path='/')
        return resp