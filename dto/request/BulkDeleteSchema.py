from marshmallow import Schema, fields, validate, ValidationError

PROMPT_INVALID = "Invalid id length must be b/w 0 - 60"


class BulkDeleteSchema(Schema):
    ids = fields.List(
        fields.Str(),
        required=True,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=0,
                max=60,
            )
        ],
    )
