from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from typing import Optional
import datetime


# When type hinting Optional variables (for ex: id: Optional[int] = ...) it might throw an error when inheriting.
# Just in case, don't use the Optional type

# Course is a base class that the other "course" classes can inherit from
# (avoids having to type id:, title, etc every single time)
class Course:
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.Text)
    thumbnail_link: str = db.Column(db.Text)
    link: str = db.Column(db.Text)


class EmbeddedCourse(Course):
    link: str = db.Column(db.Text)


class TextCourse(Course):
    ...


class VideoCourse(Course):
    link: str = db.Column(db.Text)


class CommentReaction(db.Model):
    """
    Likes and dislikes for Comment models.

    Attributes
    -

    * id: Optional[int] - the id of the CommentReaction in the db (auto-generated by the DB).
    * user_id: int - the id of the user who posted a Reaction (Inherited from Reaction).
    * comment_id: int - The id of the comment associated with the Reaction.
    * vote: int[1, -1] - A like or a dislike (Inherited from Reaction).
    """
    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    comment_id: int = db.Column(db.Integer, db.ForeignKey("comment.id"))
    vote: int = db.Column(db.Integer)


class PostReaction(db.Model):
    """
    Likes and dislikes for Post models.

    Attributes
    -

    * id: Optional[int] - the id of the PostReaction in the db (auto-generated by the DB).
    * user_id: int - the id of the user who posted a Reaction - (Inherited from Reaction).
    * post_id: int - The id of the post associated with the Reaction.
    * vote: int[1, -1] - A like or a dislike - (Inherited from Reaction).
    """
    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id: int = db.Column(db.Integer, db.ForeignKey("post.id"))
    vote: int = db.Column(db.Integer)


class Comment(db.Model):
    """Comment model for posts.

    Attributes
    -

    * id: Optional[int] - the id of the comment in the db.
    * user_id: int - the id of the user who created the comment.
    * post_id: int - the id of the post on with which the comment is associated.
    * score: int - total score (can be either positive or negative).
    * content: str - content of the comment.
    * answer_for: int - id of the comment that this comment is replying to
    (CAUTION, placeholder value post_id is being fed to this attribute in views.post).
    * created: datetime.datetime - date & time of creation (auto-generated by the DB).
    """
    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    post_id: int = db.Column(db.Integer, db.ForeignKey("post.id"))

    content: str = db.Column(db.Text)
    score: int = db.Column(db.Integer)
    answer_for: int = db.Column(db.Integer)
    created: datetime.datetime = db.Column(db.DateTime, default=func.now())


class Post(db.Model):
    """Post model.

    Attributes
    -

    * id: Optional[int] - the id of the post in the db (auto-generated by the DB).
    * user_id: int - the id of the user who created the post.
    * title: str - the title of the post.
    * content: str - content of the comment.
    * score: int - total score (can be either positive or negative).
    * category: str["all", "ask", "news", "discussion", "bug", "other"] - category
    * subject: str["all", "mathematics", "physics", "programming", "other"] - subject
    * created: datetime.datetime - date & time of creation (auto-generated by the DB).
    """

    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    title: str = db.Column(db.String(70))
    content: str = db.Column(db.Text)

    category: str = db.Column(db.String(20))
    subject: str = db.Column(db.String(20))

    score: int = db.Column(db.Integer)
    created: datetime.datetime = db.Column(db.DateTime, default=func.now())

    comments = db.relationship("Comment")


class Appointment(db.Model):
    """
    Appointment model.

    Attributes
    -
    * id: Optional[int] - the id of the Appointment in the db (auto-generated by the DB).
    * user_id: int - the id of the user who scheduled the Appointment.
    * teacher_name: str - Name of the teacher that was selected for the appointment.
    * subject_name: str["all", "mathematics", "physics", "programming", "other"] - Name of the subject the teacher is going to cover.
    * description: str - Small description of what the modelives for the appointment is or
    which specific field is to be covered.
    * date: datetime.date = Due date of the appointment
    * start_time: datetime.time = Start time of the appointment
    * end_time: datetime.time = End time of the appointment
    """

    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    teacher_name: str = db.Column(db.String(150))
    subject_name: str = db.Column(db.String(150))
    description: str = db.Column(db.String(150))
    date: datetime.date = db.Column(db.Date)
    start_time: datetime.time = db.Column(db.Time)
    end_time: datetime.time = db.Column(db.Time)


class Message(db.Model):
    """
    Message model.

    Attributes
    -
    * id: Optional[int] - the id of the Message in the db (auto-generated by the DB).
    * user_id: int - the id of the user who sent the Message.
    * phone_number: int - phone number of the user.
    * reason: str - purpose of the message.
    * title: str - title of the message.
    * message: str - the message.
    """
    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    phone_number: int = db.Column(db.Integer)
    reason: str = db.Column(db.String(150))
    title: str = db.Column(db.String(150))
    message: str = db.Column(db.Text(150))


class Notification(db.Model):
    """
    Notification model.

    Attributes
    -
    * id: Optional[int] - the id of the Notification in the db (auto-generated by the DB).
    * user_id: int - the id of the user to who the Notification is associated.
    * title: str - the title of the Notification
    * description: str - the description of the Notification
    * link: str - the link of the Notification (where the Notification should bring the user on click)
    * received: datetime.datetime - receival date (auto-generated by the DB).
    """
    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))

    title: str = db.Column(db.String(150))
    description: str = db.Column(db.Text(150))
    link: str = db.Column(db.String(150))
    received: datetime.datetime = db.Column(db.DateTime, default=func.now())


class UserSettings(db.Model):
    """
    UserSettings model.
    Attributes
    -
    * id: Optional[int] - the id of the UserSettings in the db (auto-generated by the DB).
    * user_id: int - the id of the user to who the UserSettings is associated.
    * security_emails: int[1, 0] - Whether to send security emails.
    * activity_emails: int[1, 0] - Whether to send activity emails.
    * promotional_emails: int[1, 0] - Whether to send promotional emails.
    """

    id: Optional[int] = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"))
    security_emails: int = db.Column(db.Integer)
    activity_emails: int = db.Column(db.Integer)
    promotional_emails: int = db.Column(db.Integer)


class User(db.Model, UserMixin):
    """
    User model.

    Attributes
    -
    * id: Optional[int] - the id of the User in the db (auto-generated by the DB).
    * email: str - email of the user
    * password: str - password of the user
    * two_FA: bool - whether the user has 2-Factor Authentication (phone number required)
    * account_type: str - account_type of the user
    * first_name: Optional[str] - first name of user
    * last_name: Optional[str] - last name of user
    * birthday: Optional[str] | Optional[datetime.datetime] - birthday of the user
    * gender: Optional[str] - gender of the user
    * phone_number: Optional[int] - phone_number of the user
    * Region: Optional[str] - Region of the user
    * created: Optional[datetime.datetime] - date & time of creation (auto-generated by the DB).
    """

    id: Optional[int] = db.Column(db.Integer, primary_key=True)

    username: str = db.Column(db.String(150))
    first_name: Optional[str] = db.Column(db.String(150))
    last_name: Optional[str] = db.Column(db.String(150))
    # Replace 'db.String(150)' with 'db.DateTime' when supported
    birthday = db.Column(db.String(150))
    gender: Optional[str] = db.Column(db.String(150))
    description: Optional[str] = db.Column(db.Text(150))

    email: str = db.Column(db.String(150), unique=True)
    password: str = db.Column(db.String(150))
    phone_number: int = db.Column(db.Integer)
    two_FA: bool = db.Column(db.Integer)
    region: Optional[str] = db.Column(db.String(150))

    account_type: str = db.Column(db.String(150))

    created: datetime.datetime = db.Column(db.DateTime, default=func.now())

    settings = db.relationship("UserSettings")
    notifications = db.relationship("Notification")
    posts = db.relationship("Post")
    comments = db.relationship("Comment")
    post_reactions = db.relationship("PostReaction")
    comment_reactions = db.relationship("CommentReaction")
