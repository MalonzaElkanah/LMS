from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from library.models import Book


class CreateBookSchema(Schema):
    isbn = fields.String(
        required=True, error_messages={"required": "fisbn is required"}
    )
    name = fields.String(required=True, error_messages={"required": "name is required"})
    author = fields.String(
        required=True, error_messages={"required": "name is required"}
    )
    edition = fields.String(
        required=True, error_messages={"required": "author is required"}
    )
    publisher = fields.String(
        required=True, error_messages={"required": "publisher is required"}
    )
    quantity = fields.Integer(
        required=True, error_messages={"required": "quantity is required"}
    )
    description = fields.String(
        required=True, error_messages={"required": "description is required"}
    )

    @validates("isbn")
    def validate_isbn(self, isbn):
        if isbn in ["", None]:
            raise ValidationError(
                "ISBN field is Empty. Enter a valid one.", field_name="isbn"
            )
        else:
            book = Book.query.filter_by(isbn=isbn).first()
            if book is not None:
                raise ValidationError(
                    f"Book with ISBN {isbn} already exist.", field_name="isbn"
                )

    @validates("quantity")
    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise ValidationError(
                "Error, Quantity field should be greater than 0.", field_name="quantity"
            )


class UpdateBookSchema(Schema):
    uuid = fields.String(required=False)
    isbn = fields.String(required=True, error_messages={"required": "isbn is required"})
    name = fields.String(required=True, error_messages={"required": "name is required"})
    author = fields.String(
        required=True, error_messages={"required": "name is required"}
    )
    edition = fields.String(
        required=True, error_messages={"required": "author is required"}
    )
    publisher = fields.String(
        required=True, error_messages={"required": "publisher is required"}
    )
    quantity = fields.Integer(
        required=True, error_messages={"required": "quantity is required"}
    )
    description = fields.String(
        required=True, error_messages={"required": "description is required"}
    )

    @validates("isbn")
    def validate_isbn(self, isbn):
        if isbn in ["", None]:
            raise ValidationError(
                "ISBN field is Empty. Enter a valid one.", field_name="isbn"
            )

    @validates("quantity")
    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise ValidationError(
                "Error, Quantity field should be greater than 0.", field_name="quantity"
            )

    @validates_schema
    def validate_update_isbn(self, data, **kwargs):
        book = Book.query.filter_by(uuid=data.get("uuid")).one_or_none()

        if book is not None:
            isbn = data.get("isbn")

            if book.isbn != isbn:
                if Book.query.filter_by(isbn=isbn).first() is not None:
                    raise ValidationError(
                        f"Book with ISBN {isbn} already exist.", field_name="isbn"
                    )
        else:
            raise ValidationError(
                "Internal Server Error, Refresh the page and try again."
            )
