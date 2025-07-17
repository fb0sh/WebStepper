from web import WebPayload, WebStep, file2http_request
from .flag_submitter import flag_submitter

web1 = [
    WebPayload(
        [
            WebStep(
                # $IP
                request_message_template=file2http_request(
                    "./requests/web1_backdoor.http"
                ),
                post_extract={"$FLAG": r"flag{.*?}"},
            ),
            flag_submitter,
        ],
    )
]
