from marshmallow import (
    Schema,
    fields,
    validates,
    validate,
    ValidationError,
    validates_schema,
)

from library.models import User


class UserRegisterSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[validate.Length(min=8, max=50)],
        error_messages={"required": "email is required"},
    )
    password = fields.String(
        required=True,
        load_only=True,
        validate=[validate.Length(min=8)],
        error_messages={"required": "password is required"},
    )
    confirm_password = fields.String(
        required=True,
        load_only=True,
        validate=[validate.Length(min=8)],
        error_messages={"required": "Confirm password is required"},
    )

    @validates("email")
    def validate_email(self, email):
        if email in ["", None]:
            raise ValidationError(
                "Email field is Empty. Enter a valid one.", field_name="email"
            )
        else:
            user = User.query.filter_by(email=email).first()
            if user is not None:
                raise ValidationError("Email already exist.", field_name="email")

    @validates("password")
    def validate_password(self, password):
        if password in ["", None]:
            raise ValidationError(
                "Password field is Empty. Enter a valid password.",
                field_name="password",
            )

    @validates_schema
    def validate_confirm_password(self, data, **kwargs):
        if data.get("password") != data.get("confirm_password"):
            raise ValidationError(
                "Password and confirm password do not match",
                field_name="confirm_password",
            )


class UserLoginSchema(Schema):
    email = fields.Email(
        required=True,
        validate=[validate.Length(min=8, max=50)],
        error_messages={"required": "email is required"},
    )
    password = fields.String(
        required=True,
        load_only=True,
        validate=[validate.Length(min=8)],
        error_messages={"required": "password is required"},
    )

    @validates("email")
    def validate_email(self, email):
        if email in ["", None]:
            raise ValidationError(
                "Email field is Empty. Enter a valid email.", field_name="email"
            )
        else:
            # Check if email exists
            user = User.query.filter_by(email=email).one_or_none()
            if user is None:
                raise ValidationError(
                    "Invalid Email or Password.", field_name="password"
                )

    @validates("password")
    def validate_password(self, password):
        if password in ["", None]:
            raise ValidationError(
                "Password field is Empty. Enter a valid password.",
                field_name="password",
            )
