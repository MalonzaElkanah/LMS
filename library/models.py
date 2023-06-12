import uuid
import datetime as dt

from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy

from config import Config


db = SQLAlchemy()


class User(db.Model):
    uuid = db.Column(db.String(40), primary_key=True, default=str(uuid.uuid1()))
    email = db.Column(db.String(50), nullable=False, index=True, unique=True)
    password = db.Column(db.String, nullable=False)

    date_created = db.Column(db.DateTime, default=dt.datetime.now().astimezone)
    date_modified = db.Column(db.DateTime, onupdate=dt.datetime.now().astimezone)

    members_added = db.relationship(
        "Member",
        backref="user_added_by",
        lazy="dynamic",
        cascade="save-update, merge, refresh-expire, expunge",
        order_by="desc(Member.date_created)",
        foreign_keys="Member.added_by",
    )
    books_added = db.relationship(
        "Book",
        backref="user_added_by",
        lazy="dynamic",
        cascade="save-update, merge, refresh-expire, expunge",
        order_by="desc(Book.date_created)",
        foreign_keys="Book.added_by",
    )
    rent_transactions = db.relationship(
        "Transaction",
        backref="user_rent",
        lazy="dynamic",
        cascade="save-update, merge, refresh-expire, expunge",
        order_by="desc(Transaction.date_created)",
        foreign_keys="Transaction.rented_by",
    )
    returned_transactions = db.relationship(
        "Transaction",
        backref="user_return",
        lazy="dynamic",
        cascade="save-update, merge, refresh-expire, expunge",
        order_by="desc(Transaction.date_created)",
        foreign_keys="Transaction.returned_by",
    )

    def __repr__(self):
        return f"<User: {self.email}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Member(db.Model):
    STATUS = ("ACTIVE", "INACTIVE", "DEFAULTED")

    uuid = db.Column(db.String(40), primary_key=True, default=str(uuid.uuid1()))
    first_name = db.Column(db.String(50), nullable=False)
    second_name = db.Column(db.String(50), nullable=True)
    id_number = db.Column(db.Integer, nullable=False, index=True, unique=True)

    date_created = db.Column(db.DateTime, default=dt.datetime.now().astimezone)
    date_modified = db.Column(db.DateTime, onupdate=dt.datetime.now().astimezone)

    added_by = db.Column(db.String(36), db.ForeignKey("user.uuid"))

    transactions = db.relationship(
        "Transaction",
        backref="member_rent",
        lazy="dynamic",
        cascade="save-update, merge, refresh-expire, expunge",
        order_by="desc(Transaction.date_created)",
        foreign_keys="Transaction.member",
    )

    def __repr__(self):
        return f"<Member: {self.first_name} {self.second_name}"

    @property
    def name(self):
        return f"{self.first_name} {self.second_name}"

    @property
    def status(self):
        if self.outstanding_fee >= Config.OUTSTANDING_DEBT:
            return "DEFAULTED"

        return "ACTIVE"

    @property
    def outstanding_fee(self):
        outstanding_fee = 0

        for item in self.transactions.filter_by(rent_paid=False):
            outstanding_fee += item.rent_fee

        return outstanding_fee


class Book(db.Model):
    STATUS = ("AVAILABLE", "UNAVAILABLE")

    uuid = db.Column(db.String(40), primary_key=True, default=str(uuid.uuid1()))
    isbn = db.Column(db.String(40), nullable=False, index=True, unique=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    author = db.Column(db.String(50), nullable=False)
    edition = db.Column(db.String(50), nullable=True, default="First")
    publisher = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String, nullable=True)
    quantity = db.Column(db.Integer, default=1)

    date_created = db.Column(db.DateTime, default=dt.datetime.now().astimezone)
    date_modified = db.Column(db.DateTime, onupdate=dt.datetime.now().astimezone)

    added_by = db.Column(db.String(36), db.ForeignKey("user.uuid"))

    transactions = db.relationship(
        "Transaction",
        backref="book_rent",
        lazy="dynamic",
        cascade="save-update, merge, refresh-expire, expunge",
        order_by="desc(Transaction.date_created)",
        foreign_keys="Transaction.book",
    )

    def __repr__(self):
        return f"<Book: {self.name}>"

    @property
    def status(self):
        if self.number_issued >= self.quantity:
            return "UNAVAILABLE"

        return "AVAILABLE"

    @property
    def number_issued(self):
        number_issued = len(list(self.transactions.filter_by(return_date=None)))

        return number_issued

    @property
    def number_available(self):
        return self.quantity - self.number_issued


class Transaction(db.Model):
    STATUS = ("RENTED", "RETURNED", "OVERDUE", "OVERDUE_NOTPAID", "OVERDUE_PAYED")

    uuid = db.Column(db.String(40), primary_key=True, default=str(uuid.uuid1()))
    rent_date = db.Column(db.DateTime, default=dt.datetime.now().astimezone)
    return_date = db.Column(db.DateTime, nullable=True)
    rate_per_day = db.Column(db.Float, default=20.0)
    rent_paid = db.Column(db.Boolean, default=False)

    date_created = db.Column(db.DateTime, default=dt.datetime.now().astimezone)
    date_modified = db.Column(db.DateTime, onupdate=dt.datetime.now().astimezone)

    book = db.Column(db.String(36), db.ForeignKey("book.uuid"))
    member = db.Column(db.String(36), db.ForeignKey("member.uuid"))
    rented_by = db.Column(db.String(36), db.ForeignKey("user.uuid"))
    returned_by = db.Column(db.String(36), db.ForeignKey("user.uuid"))

    def __repr__(self):
        return f"<Transaction: {self.uuid}>"

    @property
    def rent_fee(self):
        rate_per_day = self.rate_per_day
        rent_date = self.rent_date

        if self.return_date is not None:
            rent_days = self.return_date - rent_date
        else:
            rent_days = dt.datetime.now().astimezone() - rent_date.astimezone()

        if rent_days.days > 0:
            return rent_days.days * rate_per_day

        return rate_per_day

    @property
    def rent_days(self):
        rent_date = self.rent_date

        if self.return_date is not None:
            rent_days = self.return_date - rent_date
        else:
            rent_days = dt.datetime.now().astimezone() - rent_date.astimezone()

        if rent_days.days > 0:
            return rent_days.days

        return 1

    @property
    def status(self):
        if self.return_date is not None:
            return "RETURNED"
            # if self.rent_fee > 500 and rent_paid:
            # return "OVERDUE_PAID"
            # elif self.rent_fee > 500:
            # return "OVERDUE_NOTPAID"
            # elif self.rent_fee > 500:
            # return "OVERDUE"
        else:
            return "RENTED"
