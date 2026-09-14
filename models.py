from database import db


class Donor(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    address = db.Column(db.String(200))

    city = db.Column(db.String(50))

    state = db.Column(db.String(50))

    pincode = db.Column(db.String(10))

    date_of_birth = db.Column(db.String(20))

    gender = db.Column(db.String(20))

    blood_group = db.Column(db.String(10))

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )


class Cause(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(300)
    )

    target_amount = db.Column(
        db.Float,
        nullable=False
    )

    collected_amount = db.Column(
        db.Float,
        default=0.0
    )

    category = db.Column(
        db.String(50)
    )

    location = db.Column(
        db.String(100)
    )

    start_date = db.Column(
        db.String(20)
    )

    end_date = db.Column(
        db.String(20)
    )

    status = db.Column(
        db.String(30),
        default="Active"
    )

    created_at = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )


class DonationTransaction(db.Model):
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    donor_id = db.Column(
        db.Integer,
        db.ForeignKey("donor.id"),
        nullable=False
    )

    cause_id = db.Column(
        db.Integer,
        db.ForeignKey("cause.id"),
        nullable=False
    )

    # Relationships
    donor = db.relationship("Donor")
    cause = db.relationship("Cause")

    amount = db.Column(
        db.Float,
        nullable=False
    )

    payment_method = db.Column(
        db.String(50)
    )

    transaction_date = db.Column(
        db.DateTime,
        default=db.func.current_timestamp()
    )

    transaction_status = db.Column(
        db.String(30),
        default="Completed"
    )

    receipt_number = db.Column(
        db.String(100),
        unique=True
    )