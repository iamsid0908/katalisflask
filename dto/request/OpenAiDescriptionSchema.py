from marshmallow import Schema, fields, validate, ValidationError

PROMPT_INVALID = "Invalid prompt length"
PROMPT_TYPE_INVALID = "Prompt type invalid it should be one of english or bahasa"


class OpenAiDescriptionSchema(Schema):
    language = fields.Str(
        required=True,
        validate=[
            validate.Regexp(regex=r"^(english|bahasa|hindi)", error=PROMPT_TYPE_INVALID)
        ],
    )
    prompt = fields.Str(
        required=True,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=2,
                max=8000,
            )
        ],
    )

    promptSetting = fields.Str(
        required=False,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=0,
                max=4000,
            )
        ],
    )
    brandVoice = fields.Str(
        required=False,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=0,
                max=4000,
            )
        ],
    )
    keywords = fields.List(
        fields.Str(),
        required=False,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=0,
                max=4000,
            )
        ],
    )
    keyPoints = fields.List(
        fields.Str(),
        required=False,
        validate=[
            validate.Length(
                error=PROMPT_INVALID,
                min=0,
                max=4000,
            )
        ],
    )
