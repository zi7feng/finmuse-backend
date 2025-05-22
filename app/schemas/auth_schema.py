from marshmallow import Schema, fields, validates, ValidationError
import re

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{2,50}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[A-Z]).{8,}$")
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

class RegisterSchema(Schema):
    account_name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True)
    preferred_currency = fields.Str(required=False, load_default="CAD")
    notification_opt_in = fields.Boolean(required=False, load_default=True)

    @validates("account_name")
    def validate_account_name(self, value):
        if not USERNAME_REGEX.match(value):
            raise ValidationError("Username must be 2-50 characters long and only contain letters, numbers, and underscores.")

    @validates("email")
    def validate_email(self, value):
        if not EMAIL_REGEX.match(value):
            raise ValidationError("Invalid email format.")

    @validates("password")
    def validate_password(self, value):
        if not PASSWORD_REGEX.match(value):
            raise ValidationError("Password must be at least 8 characters long and contain at least one uppercase letter.")


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)
