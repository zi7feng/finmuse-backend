from marshmallow import Schema, fields, validates_schema, ValidationError
import re

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{2,50}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z]).{8,}$")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

class RegisterSchema(Schema):
    account_name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    preferred_currency = fields.Str(load_default="CAD")
    notification_opt_in = fields.Boolean(load_default=True)

    @validates_schema
    def validate_all(self, data, **kwargs):
        errors = {}

        if not USERNAME_REGEX.match(data["account_name"]):
            errors["account_name"] = [
                "Username must be 2-50 characters long and only contain letters, numbers, and underscores."
            ]

        if not EMAIL_REGEX.match(data["email"]):
            errors["email"] = ["Invalid email format."]

        if not PASSWORD_REGEX.match(data["password"]):
            errors["password"] = [
                "Password must be at least 8 characters long and contain at least one uppercase letter."
            ]

        if errors:
            raise ValidationError(errors)



class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
