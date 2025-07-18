from flask import Flask

app = Flask(__name__)


@app.route("/backdoor", methods=["GET", "POST"])
def ret2flag():
    return "flag{824f0d5b4853473082ab8c3e3a580f43}"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
