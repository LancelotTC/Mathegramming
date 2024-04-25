from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.wrappers.response import Response
from flask_login import login_required, current_user
from .models import Notification, Post, User, Comment, CommentReaction, PostReaction, Appointment, Message
from . import db
from sqlalchemy import func, or_
from datetime import datetime as dt
import json as js
from datetime import datetime, timedelta
from typing import Any


views: Blueprint = Blueprint("views", __name__)

# Global variable used in views.forum
posted_data: dict = {
    "posts": None,
    "filter":
        {
            "date": (timedelta(days=999999), "All"),
            "subject": ("All", "All"),
            "category": ("All", "All")
        },
    "search_query": ""
}


def get(element_name: str) -> str | None:
    """Shorthand for request.form.get()"""

    return request.form.get(element_name)


def get_pretty_date_delta(delta: timedelta) -> str:
    """
    Function that accepts a type timedelta and returns a readable time difference.

    Feel free to rename or reassign function as name is quite long.
    Ex:
    -> get_pretty_date_delta(timedelta(seconds=54))

    -> "A few seconds ago"


    -> get_pretty_date_delta(timedelta(hours=48))

    -> "2 days ago"
    """
    from datetime import timedelta
    if delta < timedelta(seconds=59):  # Less than 1m
        return "A few seconds"
    elif delta < timedelta(hours=1):  # Less than 1h
        value = delta.seconds // 60
        unit = "minutes" if value > 1 else "minute"
    elif delta < timedelta(days=1):  # Less than 1d
        value = delta.seconds // (3600)
        unit = "hours" if value > 1 else "hour"
    elif delta < timedelta(weeks=1):  # Less than 1w
        value = delta.days
        unit = "days" if value > 1 else "day"
    elif delta < timedelta(days=30):  # Less than 1mth
        value = delta.days // 7
        unit = "weeks" if value > 1 else "week"
    elif delta < timedelta(weeks=52):  # Less than 1y
        value = delta.days // 30
        unit = "months" if value > 1 else "month"
    else:  # Above 1y
        value = delta.days // 365
        unit = "years" if value > 1 else "year"

    return f"{value} {unit}"


@views.route("/exercises", methods=["GET", "POST"])
@login_required
def exercises() -> str:
    """Renders the exercises.html page if user is logged-in."""
    return render_template("exercises.html", current_user=current_user)


@views.route("/", methods=["GET"])
def home() -> str:
    """Renders the home.html page"""
    return render_template("home.html", current_user=current_user)


@views.route("/home", methods=["GET"])
def default() -> Response:
    """
    Redirects to the views.home function.

    It's purpose is to not throw a 404 error when going to http://127.0.0.1:5000/.

    -> http://127.0.0.1:5000/ = http://127.0.0.1:5000/home
    """
    return redirect(url_for("views.home"))


@views.route("/embedded_course", methods=["GET"])
@login_required
def embedded_course() -> str:
    """Renders the embedded_course.html page"""
    return render_template("embedded_course.html", current_user=current_user, teachers=User.query.filter_by(account_type="teacher"))


@views.route("/text_course", methods=["GET"])
@login_required
def text_course() -> str:
    """Renders the text_course.html page"""
    return render_template("text_course.html", current_user=current_user, teachers=User.query.filter_by(account_type="teacher"))


@views.route("/video_course", methods=["GET"])
@login_required
def video_course() -> str:
    """Renders the video_course.html page"""
    return render_template("video_course.html", current_user=current_user, teachers=User.query.filter_by(account_type="teacher"))


@views.route("/course_finished", methods=["GET"])
@login_required
def course_finished() -> str:
    """Renders the course_finished.html page"""
    return render_template("course_finished.html", current_user=current_user)


@views.route("/pricing", methods=["GET"])
def pricing() -> str:
    """Renders the pricing.html page"""
    return render_template("pricing.html", current_user=current_user)


@views.route("/account", methods=["GET"])
@login_required
def account() -> str:
    """Renders the account.html page"""
    return render_template("account.html", current_user=current_user)


@views.route("/appearance", methods=["GET"])
@login_required
def appearance() -> str:
    """Renders the appearance.html page"""
    return render_template("appearance.html", current_user=current_user)


@views.route("/email_preferences", methods=["POST", "GET"])
@login_required
def email_prefs() -> Response:
    """Renders the emails_prefs.html page"""
    if request.method == "POST":
        security_emails = get("security-emails")
        activity_emails = get("activity-emails")
        promotional_emails = get("promotional-emails")

        user = User.query.filter_by(id=current_user.id).first()
        user.security_emails = True if security_emails == "on" else False
        user.activity_emails = True if activity_emails == "on" else False
        user.promotional_emails = True if promotional_emails == "on" else False

        db.session.commit()

        redirect(url_for("views.email_prefs"))

    return render_template("email_prefs.html", current_user=current_user)


def get_filter(date="", subject="", category="") -> dict:
    """
    This function generates a dict object that matches the expected values in forum.html
    """

    dct_date = {
        "date-all": timedelta(days=999999),  # Update in 2740 years
        "date-hour": timedelta(days=1/24),
        "date-day": timedelta(days=1),
        "date-week": timedelta(days=7),
        "date-month": timedelta(days=30),
        "date-year": timedelta(days=365)
    }

    dct_subject = {
        "subject-all": "All",
        "subject-mathematics": "Mathematics",
        "subject-physics": "Physics",
        "subject-programming": "Programming",
        "subject-other": "other"
    }

    dct_category = {
        "category-all": "All",
        "category-ask": "ask",
        "category-news": "news",
        "category-discussion": "discussion",
        "category-bug": "bug",
        "category-other": "other"
    }

    # CAUTION: filter overrides Python's built-in class filter
    filter = {
        "date": (dct_date[date], date),
        "subject": (dct_subject[subject], subject),
        "category": (dct_category[category], category),
    }
    return filter


@views.route("/forum", methods=["POST", "GET"])
@login_required
def forum() -> str | Response:
    """Renders the forum.html page and manages the post request sent by filters and search."""
  # vvvvvvvvvvvvvvvvvv See issue number 3 in GitLab
    global posted_data

    # Creates a dict where the key is the id of the post and the value is the amount of comments on said post.
    # {post_id: number_of_comments, ...}
    # Doesn't create any entries for posts that have no comments.
    # It might be a good idea to make it so that it creates these entries anyway.
    x = db.session.query(Comment.post_id, func.count(
        Comment.id)).group_by(Comment.post_id).all()
    nb_comments = {i[0]: i[1] for i in x}

    # Default filtering settings
    filter = {"date": (timedelta(days=999999), "All"), "subject": (
        "All", "All"), "category": ("All", "All")}

    if request.method == "POST":
        # data is sent with JavaScript as a JSON type.
        # If method == POST but there's no data, that means that the user clicked on "create post"
        try:
            data = js.loads(request.data)
        except js.JSONDecodeError:
            return redirect(url_for("views.forum"))  # views.create_post

        search_query = data["search_query"]

        filter = get_filter(
            date=data["by-date"], subject=data["by-subject"], category=data["category"])

        # Posts that match the search. Pattern matching and the like are done in the DB itself.
        posts = Post.query.filter(or_(Post.title.like(
            f"%{search_query}%")), Post.title.ilike(f"%{search_query}%"))

        # This is done in order to not get the values overwritten by a GET request.
        # See issue number on top of function.
        posted_data["posts"] = posts
        posted_data["filter"] = filter
        posted_data["search_query"] = search_query

    elif request.method == "GET":
        search_query = ""
        posts = Post.query

        # Retrieving previously POSTed information if there are any (again, refer to the issue on top of this function)
        # This is an ugly way of saying "if the dictionary is not equal to the default dictionary"
        # The default value of posted_data["posts"] is None. If posted_data["posts"] is None, I want to give Post.query instead.
        # Otherwise if posted_data["posts"] is something else, then it means it comes from the POST request, so I want it.
        if posted_data["posts"]:
            posts = posted_data["posts"] if posted_data["posts"] else Post.query
            filter = posted_data["filter"]
            search_query = posted_data["search_query"]

            # The default value of posts is None
            posted_data = {
                "posts": None,
                "filter": {"date": (timedelta(days=999999), "All"),
                           "subject": ("All", "All"), "category": ("All", "All")},
                "search_query": ""
            }

    return render_template(
        "forum.html",
        current_user=current_user,
        users=User.query,
        posts=posts,
        nb_comments=nb_comments,
        now=dt.utcnow,
        get_delta=get_pretty_date_delta,
        filter=filter,
        search_query=search_query
    )


@views.route("/create_post", methods=["POST", "GET"])
@login_required
def create_post() -> str | Response:
    """
    Renders create_post.html and creates posts and a notification
    to notify the user that their post has successfully been created.
    It then redirects to views.forum
    """

    if request.method == "POST":
        title = get("title")
        category = get("category")
        subject = get("subject")
        content = get("content")

        db.session.add(
            Post(
                user_id=current_user.id,
                title=title,
                category=category,
                subject=subject,
                content=content,
                score=0
            )
        )

        db.session.add(
            Notification(
                user_id=current_user.id,
                title=f"Your post {title} was posted successfully",
                description="Click here to review your posts and answers.",
                link=""
            )
        )

        db.session.commit()

        return redirect(url_for("views.forum"))

    return render_template("create_post.html", current_user=current_user)


@views.route("/post/<post_id>", methods=["POST", "GET"])
@login_required
def post(post_id) -> str | Response:
    """Renders post.html where the path is the id and also manages comment's posting on the post.

    Ex: The page's URL for a post, which id is 3, will be http://127.0.0.1:5000/post/3
    """

    # If comment is empty I want to render the page without sending the comment (I don't want to send empty comments)
    if request.method == "GET" or get("comment") == "":
        post = Post.query.filter_by(id=post_id).first()
        user = User.query.filter_by(id=post.user_id).first()
        comments = Comment.query.filter_by(post_id=post_id)

        # Get all the users that have sent comments on post_id.
        # Users can have multiple comments per post, so distinct is needed here
        users = User.query.distinct().join(Comment).filter(Comment.post_id == post_id)
        # comment_reactions = CommentReaction.query.join(Comment).filter(Comment.post_id==post_id)

        # The next 2 lines will get all CommentReaction for every Comment in Post
        # Get all the ids of the comments of the post
        comment_subquery = db.session.query(Comment.id).filter(
            Comment.post_id == post_id).subquery()
        # Then get all the reactions, from which comment_id is in the comment_subquery (line just above)
        comment_reactions = CommentReaction.query.filter(
            CommentReaction.comment_id.in_(comment_subquery))

        # PostReaction from the logged-in user.
        post_reaction = PostReaction.query.filter_by(
            user_id=current_user.id, post_id=post_id).first()

        # I have to pass in CommentReaction because
        # I iterate through the comments and I have to pass in each CommentReaction
        # It is possible to scrape off some arguments by making some changes to post.html,
        # although it might be less readable in that case.
        return render_template("post.html",
                               current_user=current_user,
                               author=user,
                               post=post,
                               comments=comments,
                               users=users,
                               post_reaction=post_reaction,
                               comment_reactions=comment_reactions,
                               CommentReaction=CommentReaction,
                               now=dt.utcnow,
                               get_delta=get_pretty_date_delta,
                               )

    # User sends a (non-empty) comment
    elif request.method == "POST":
        # CAUTION: the attribute "answer_for" is an attribute that was created
        # to implement the feature that lets users reply to other comments.
        # answer_for=post_id is just a placeholder.
        new_comment = Comment(
            user_id=current_user.id,
            post_id=post_id,
            score=0,
            content=get("comment"),
            answer_for=post_id
        )
        db.session.add(new_comment)
        db.session.commit()

        return redirect(url_for("views.post", post_id=post_id))


@views.route("/comment_vote", methods=["POST"])
@login_required
def comment_vote() -> None:
    """
    Handles comments impressions (like/dislikes).
    It is probably possible to merge comment_vote and post_vote together
    and/or make a decorator function, since they are both similar to each other.
    """
    reaction = js.loads(request.data.decode("utf-8"))
    comment_id = reaction["commentId"]
    vote_result = reaction["voteResult"]
    vote = CommentReaction.query.filter_by(
        comment_id=comment_id, user_id=current_user.id).first()
    comment = Comment.query.get(comment_id)
    if vote:
        if vote.vote == vote_result:
            db.session.delete(vote)
            comment.score -= vote_result

        else:
            vote.vote = vote_result
            comment.score += 2*vote_result

    else:
        new_comment_reaction = CommentReaction(
            user_id=current_user.id,
            vote=vote_result,
            comment_id=comment_id
        )
        db.session.add(new_comment_reaction)
        comment.score += vote_result

    db.session.commit()


@views.route("/post_vote", methods=["POST"])
@login_required
def post_vote() -> None:
    """
    Handles post impressions (like/dislikes).
    It is probably possible to merge comment_vote and post_vote together
    and/or make a decorator function, since they are both similar to each other.
    """
    reaction = js.loads(request.data.decode("utf-8"))
    post_id = reaction["postId"]
    vote_result = reaction["voteResult"]
    vote = PostReaction.query.filter_by(
        post_id=post_id, user_id=current_user.id).first()
    post = Post.query.get(post_id)
    if vote:
        if vote.vote == vote_result:
            db.session.delete(vote)
            post.score -= vote_result

        else:
            vote.vote = vote_result
            post.score += 2 * vote_result

    else:
        new_post_reaction = PostReaction(
            user_id=current_user.id,
            vote=vote_result,
            post_id=post_id
        )
        db.session.add(new_post_reaction)
        post.score += vote_result

    db.session.commit()


@views.route("/contact_us", methods=["POST", "GET"])
def contact_us() -> str | Response:
    """Renders the contact_us.html page and creates a Message object in DB and a Notification"""
    if request.method == "POST":
        db.session.add(
            Message(
                user_id=current_user.id,
                phone_number=get("phone-number"),
                reason=get("reason"),
                title=get("title"),
                message=get("message")
            ),
        )
        db.session.add(
            Notification(
                user_id=current_user.id,
                title="Your message was successfully sent",
                description="You will receive an answer in under 2 working days.",
                link=url_for("views.activity_information")
            )
        )
        db.session.commit()
        return redirect(url_for("views.contact_us_finalized"))

    return render_template("contact_us.html", current_user=current_user)


@views.route("/contact_us_finalized", methods=["GET"])
def contact_us_finalized() -> str:
    """Renders the contact_us_finalized.html page."""
    return render_template("contact_us_finalized.html", current_user=current_user)


@views.route("/appointment", methods=["POST", "GET"])
@login_required
def appointment() -> str | Response:
    """Renders the appointment.html page and creates an Appointment object in DB and a Notification"""
    if request.method == "POST":
        date = get("date")
        start_time = datetime.strptime(get("start-time"), "%H:%M").time()
        db.session.add(
            Appointment(
                user_id=current_user.id,
                teacher_name=get("teacher"),
                subject_name=get("subject"),
                description=get("description"),
                date=datetime.strptime(get("date"), "%Y-%m-%d").date(),
                # I put get("start_time") in variable because referenced 2 times
                start_time=start_time,
                end_time=datetime.strptime(
                    get("end-time"), "%H:%M").time()
            )
        )

        # Add notification for the user who scheduled the appointment
        db.session.add(
            Notification(
                user_id=current_user.id,
                title="Your appointment was successfully scheduled",
                description=f"Your appointment was successfully scheduled for the {date} at {start_time}",
                link=url_for("views.activity_information")
            )
        )

        # Add notification for the selected teacher
        db.session.add(
            Notification(
                # Placeholder. Change with the id of the selected teacher.
                # User.query.filter_by(username=get("teacher_name"))
                user_id=current_user.id-1,
                title=f"You have an appointment with {User.query.filter_by(id=current_user.id).first().username}",
                description=f"Your appointment was scheduled for the {date} at {start_time}",
                link=url_for("views.activity_information")
            )
        )
        db.session.commit()
        return redirect(url_for("views.appointment_finalized"))
    return render_template("appointment.html", current_user=current_user, teachers=User.query.filter_by(account_type="teacher"))


@views.route("/appointment_finalized", methods=["GET"])
@login_required
def appointment_finalized() -> str:
    """Renders the appointment_finalized.html page."""
    return render_template("appointment_finalized.html", current_user=current_user)


@views.route("/about_us", methods=["GET"])
def about_us() -> str:
    """Renders the about_us.html page."""
    return render_template("about_us.html", current_user=current_user)


@views.route("/clear_all_notifications", methods=["POST"])
@login_required
def clear_all_notifications() -> Response:
    """Deletes all of the User's Notifications from DB"""
    notifications = Notification.query.filter_by(user_id=current_user.id)
    for i in notifications:
        db.session.delete(i)
    db.session.commit()
    return redirect(url_for("views.home"))


@views.route("/activity_information", methods=["GET"])
@login_required
def activity_information() -> str:
    """Renders the activity_information.html page"""

    # Getting all the information that will be displayed to the user.
    comments = Comment.query.filter_by(user_id=current_user.id)
    posts = Post.query.filter_by(user_id=current_user.id)
    messages = Message.query.filter_by(user_id=current_user.id)
    appointments = Appointment.query.filter_by(user_id=current_user.id)
    subquery = db.session.query(
        Comment.post_id).filter_by(user_id=current_user.id)
    posts_of_comments = Post.query.filter(Post.id.in_(subquery))

    # I will need the built-in enumerate to display the list index of all the elements
    return render_template("activity_information.html",
                           current_user=current_user, comments=comments,
                           posts=posts, messages=messages,
                           appointments=appointments,
                           posts_of_comments=posts_of_comments,
                           enumerate=enumerate
                           )
