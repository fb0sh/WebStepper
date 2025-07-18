from web import WebStep, file2http_request

flag_submitter = WebStep(
    # $IP, $FLAG
    request_message_template=file2http_request("./requests/submit_flag.txt"),
    post_extract={"$?": r"(.*)"},
)
