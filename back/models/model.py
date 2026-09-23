from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


case_tags = db.Table(
    "case_tags",

    db.Column(
        "case_id",
        db.Integer,
        db.ForeignKey("cases.id"),
        primary_key=True
    ),

    db.Column(
        "tag_id",
        db.Integer,
        db.ForeignKey("tags.id"),
        primary_key=True
    )
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    google_id = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )

    name = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False,
        default="user"
    )


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    dob = db.Column(
        db.Date,
        nullable=False
    )

    tob = db.Column(
        db.Time,
        nullable=True
    )

    gender = db.Column(
        db.String(20),
        nullable=True
    )

    place = db.Column(
        db.String(100),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    state = db.Column(
        db.String(100),
        nullable=False
    )

    story = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING"
    )

    verification_status = db.Column(
        db.String(20),
        nullable=False,
        default="UNVERIFIED"
    )

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    tags = db.relationship(
        "Tag",
        secondary=case_tags,
        back_populates="cases"
    )


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    slug = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    cases = db.relationship(
        "Case",
        secondary=case_tags,
        back_populates="tags"
    )
