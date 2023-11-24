from marshmallow import Schema, fields


class GetPaginatedListingSchema(Schema):
    limit = fields.Int(
        required=True,
    )
    before_id = fields.Str(
        required=False,
    )
