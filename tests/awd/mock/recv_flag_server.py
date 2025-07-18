from flask import Flask, request, jsonify

app = Flask(__name__)

received_flags = []


@app.route("/submit_flag", methods=["GET", "POST"])
def submit_flag():
    # GET 从 query 参数拿 flag，比如 /submit_flag?flag=xxx
    flag = request.args.get("flag")

    # POST 从表单或 JSON 里拿 flag
    if not flag:
        flag = request.form.get("flag")
    if not flag and request.is_json:
        json_data = request.get_json()
        flag = json_data.get("flag") if json_data else None

    if not flag:
        return jsonify({"error": "No flag provided"}), 400

    print(f"Received flag: {flag}")
    received_flags.append(flag)
    return "提交成功"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
