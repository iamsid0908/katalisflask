from marshmallow import Schema, fields, validate, ValidationError

PROMPT_TYPE_INVALID = "Prompt type invalid it should be one of english or bahasa"
IMAGE_URL_INVALID = "Invalid image URL"
MISSING_FILE_INVALID = "Missing field 'file' error"
INVALID_FILE_SIZE = "Invalid file size maximum 4mb file size allowed"
MISSING_MASK_INVALID = "Missing field 'mask' error"
PROMPT_INVALID = "Invalid prompt length"


def validate_bytes(data):
    if not isinstance(data, bytes):
        raise ValidationError("Field must be bytes.")


class OpenAiImageSchema(Schema):
    image = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=INVALID_FILE_SIZE,
                min=0,
                max=3900000,
            )
        ],
    )
    mask = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=INVALID_FILE_SIZE,
                min=0,
                max=3900000,
            )
        ],
    )
    prompt = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=2,
                max=1500,
            )
        ],
    )
    imageUrl = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=IMAGE_URL_INVALID,
                min=0,
                max=4000,
            )
        ],
    )
