from marshmallow import Schema, fields, validate

USERNAME_INVALID = "Invalid username"
PASSWORD_INVALID = "Password is not correct"

class RegistrationSchema(Schema):
    fullName = fields.String(
        required=True,
        validate=[
            validate.Length(min=2, max=40)
        ]
    )
    userName = fields.Str(
        required=True,
        validate=[
            validate.Length(error=USERNAME_INVALID, min=2, max=40)
        ]
    )
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(error=PASSWORD_INVALID, min=3, max=40)
        ]
    )
    phoneNumber = fields.Str()  # You can adjust the field type and validation as needed
    email = fields.Email()  # Validates email format
    phoneVerified = fields.Bool()
    emailVerified = fields.Bool()
    usertype = fields.Str()  # You can adjust the field type and validation as needed
