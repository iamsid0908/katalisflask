from marshmallow import Schema, fields, validate, ValidationError

INVALID_FILE_SIZE = "Invalid id length must be b/w 0 - 60"


class ConvertBase64ImageSchema(Schema):
    base64_image = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=INVALID_FILE_SIZE,
                min=0,
                max=3900000,
            )
        ],
    )
