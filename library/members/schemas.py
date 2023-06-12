from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from library.models import Member


class CreateMemberSchema(Schema):
    first_name = fields.String(
        required=True, error_messages={"required": "first_name is required"}
    )
    second_name = fields.String(
        required=True, error_messages={"required": "second_name is required"}
    )
    id_number = fields.Integer(
        required=True, error_messages={"required": "id_number is required"}
    )

    @validates("id_number")
    def validate_id_number(self, id_number):
        if id_number in ["", None]:
            raise ValidationError(
                "ID Number field is Empty. Enter a valid one.", field_name="id_number"
            )
        elif len(str(id_number)) != 8:
            raise ValidationError(
                "Wrong Length! ID Number is 8 digits long.", field_name="id_number"
            )
        else:
            member = Member.query.filter_by(id_number=id_number).first()
            if member is not None:
                raise ValidationError(
                    f"Member with ID Number {id_number} already exist.",
                    field_name="id_number",
                )


class UpdateMemberSchema(Schema):
    uuid = fields.String(required=False)
    first_name = fields.String(
        required=True, error_messages={"required": "first_name is required"}
    )
    second_name = fields.String(
        required=True, error_messages={"required": "second_name is required"}
    )
    id_number = fields.Integer(
        required=True, error_messages={"required": "id_number is required"}
    )

    @validates("id_number")
    def validate_id_number(self, id_number):
        if id_number in ["", None]:
            raise ValidationError(
                "ID Number field is Empty. Enter a valid one.", field_name="id_number"
            )
        elif len(str(id_number)) != 8:
            raise ValidationError(
                "Wrong Length! ID Number is 8 digits long.", field_name="id_number"
            )

    @validates_schema
    def validate_update_id(self, data, **kwargs):
        member = Member.query.filter_by(uuid=data.get("uuid")).one_or_none()

        if member is not None:
            id_number = data.get("id_number")

            if member.id_number != id_number:
                if Member.query.filter_by(id_number=id_number).first() is not None:
                    raise ValidationError(
                        f"Member with ID Number {id_number} already exist.",
                        field_name="id_number",
                    )
        else:
            raise ValidationError(
                "Internal Server Error, Refresh the page and try again."
            )
