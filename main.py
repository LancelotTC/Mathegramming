from website import create_app

app = create_app()


if __name__ == "__main__":

    app.run(debug=True, port=5000)
    # Use the next line instead if you're getting an error related to port 5000 (in PythonAnywhere especially)
    # app.run(debug=True, port=5001)
