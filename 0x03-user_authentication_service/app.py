#!/usr/bin/env python3
"""Flask Application."""
from flask import Flask, jsonify, request, abort, make_response, redirect
from auth import Auth


app = Flask(__name__)
AUTH = Auth()


@app.route("/", methods=["GET"], strict_slashes=False)
def index():
    """
    Handle GET requests to the root URL ("/").

    Returns:
        Response: A JSON response containing a welcome message.
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"], strict_slashes=False)
def register_user():
    """
    Handle POST requests to /users to register a new user.

    Expects form data fields: "email" and "password".

    Returns:
        Response: A JSON response indicating success or failure.
    """

    try:
        email = request.form.get("email")
        password = request.form.get("password")

        # Attempt to register the user
        user = AUTH.register_user(email, password)

        # Return success response
        return jsonify({"email": email, "message": "user created"})
    except ValueError as e:
        # Return error response if user already exists
        return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login():
    """
    Handle POST requests to /sessions to log in a user.

    Expects form data fields: "email" and "password".

    Returns:
        Response: A JSON response indicating success or failure.
    """
    email = request.form.get("email")
    password = request.form.get("password")

    # Check if login information is correct
    if AUTH.valid_login(email, password):
        # Create a new session for the user
        session_id = AUTH.create_session(email)
        if session_id:
            # Set session ID as a cookie in the response
            response = make_response(
                    jsonify({"email": email, "message": "logged in"})
                    )
            response.set_cookie("session_id", session_id)
            return response
        else:
            # If session ID couldn't be created, return an error
            return jsonify({"message": "Unable to create session"}), 500
    else:
        # If login information is incorrect, return a 401 Unauthorized error
        abort(401)


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout():
    """
    Handle DELETE requests to /sessions to log out a user.

    Expects session ID as a cookie with key "session_id".

    Returns:
        Response: A redirect response to GET / or
                    a JSON response indicating failure.
    """
    # Get session ID from cookie
    session_id = request.cookies.get("session_id")

    # Find user with the requested session ID
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        # If user exists, destroy the session
        AUTH.destroy_session(user.id)
        # Redirect user to GET /
        return redirect("/")
    else:
        # If user does not exist, respond with a 403 Forbidden error
        abort(403)


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile():
    """
    Handle GET requests to /profile to retrieve user profile information.

    Expects session ID as a cookie.

    Returns:
        Response: A JSON response containing the user's email
                    or a 403 Forbidden error.
    """
    # Get session ID from cookie
    session_id = request.cookies.get("session_id")

    # Find user with the requested session ID
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        # If user exists, respond with user's email and 200 HTTP status
        return jsonify({"email": user.email}), 200
    else:
        # If session ID is invalid or user does not exist, respond with 403
        # Forbidden error
        abort(403)


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def reset_password():
    """
    Handle POST requests to /reset_password to generate a reset
    password token.

    Expects form data with "email" field.

    Returns:
        Response: A JSON response containing the user's email and reset
                    token or a 403 Forbidden error.
    """
    # Get email from form data
    email = request.form.get("email")

    # Generate reset password token
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        # If email is not registered, respond with 403 Forbidden error
        abort(403)

    # Respond with user's email and reset token
    return jsonify({"email": email, "reset_token": reset_token}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
