from marshmallow import Schema, fields, validate, ValidationError, validates
import json

USERNAME_INVALID = "Invalid username"
PASSWORD_INVALID = "Password is not correct"
MISSING_FILE_INVALID = "Missing field 'file' error"


# Define a schema for the nested "address" object
class DescriptionSchema(Schema):
    english = fields.String(required=True)
    bahasa = fields.String(required=False)
    hindi = fields.String(required=False)


class ImageUrlsSchema(Schema):
    imageUrls = fields.List(
        fields.Raw(
            type="file", required=False, error=MISSING_FILE_INVALID, allow_none=True
        ),
        required=True,
    )


class SaveListingSchema(Schema):
    id = fields.String(required=False)
    title = fields.String(required=True)
    imageUrls = fields.String(required=True)
    imageFiles = fields.Raw(type="file", required=False)
    description = fields.String(required=True)

    @validates("imageUrls")
    def validate_length(self, value):
        if len(value) < 1:
            raise ValidationError("image urls should not be empty")
        error = ImageUrlsSchema().validate(value)
        if error != {}:
            raise ValidationError(f"{error}")

    @validates("description")
    def validate_length(self, value):
        try:
            if len(value) < 1:
                raise ValidationError("description should not be emapty")
            error = DescriptionSchema().validate(json.loads(value))
            if error != {}:
                raise ValidationError(f"{error}")
        except json.decoder.JSONDecodeError as e:
            raise ValidationError(f"{e}")
