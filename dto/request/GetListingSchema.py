from marshmallow import Schema, fields, validate, ValidationError

USERNAME_INVALID = "Invalid username"
PASSWORD_INVALID = "Password is not correct"


class SaveListingSchema(Schema):
    imageUrls = fields.Str(
        required=True,
        validate=[
            validate.Length(error=USERNAME_INVALID, min=2, max=40),
        ],
    )
    description = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=PASSWORD_INVALID,
                min=3,
                max=40,
            )
        ],
    )
