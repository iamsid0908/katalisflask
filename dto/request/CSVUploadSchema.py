from marshmallow import Schema, fields


class CSVUploadSchema(Schema):
    file = fields.Raw(required=True)
