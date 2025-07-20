from functools import reduce
import re
import textwrap
import requests


def normalize_and_validate(raw: str) -> str:
    text = textwrap.dedent(raw).lstrip("\n")
    lines = text.splitlines()
    if not lines:
        raise ValueError("空报文")

    # 请求行校验
    req_line = lines[0].strip()
    if not re.match(
        r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH|TRACE|CONNECT) \S+ HTTP/\d\.\d$",
        req_line,
    ):
        raise ValueError(f"请求行格式错误: {req_line}")

    # 空行分隔头体
    try:
        empty_line_index = lines.index("")
    except ValueError:
        raise ValueError("请求头和请求体之间必须有空行")

    # 请求头格式校验
    headers = lines[1:empty_line_index]
    header_re = re.compile(r"^[\w-]+:\s*.+$")
    for h in headers:
        if not header_re.match(h.strip()):
            raise ValueError(f"请求头格式错误: {h}")

    # 重新组合
    normalized = lines[: empty_line_index + 1] + lines[empty_line_index + 1 :]
    return "\n".join(normalized) + "\n"


def file2ip_list(file_path: str) -> list[str]:
    with open(file_path, "r") as f:
        return [line.strip() for line in f.readlines()]


def file2http_request(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


class WebStep:
    url_prefix: str
    request_message_template: str
    need_context: list[str]  # 从context里取的变量
    pre_replace: dict[str, str]  # 键和值
    post_extract: dict[str, str]  # 键和正则
    context: dict[str, str]  # 键和值 以前的
    __response__: requests.Response

    def __init__(
        self,
        request_message_template: str,
        need_context: list[str],
        pre_replace: dict[str, str] = {},
        post_extract: dict[str, str] = {},
        url_prefix: str = "http://",
    ):
        self.url_prefix = url_prefix
        self.request_message_template = request_message_template
        self.pre_replace = pre_replace
        self.post_extract = post_extract
        self.need_context = need_context
        self.context = {}

    def set_context(self, context: dict[str, str]):
        self.context = context

    def __pre_replace_context(self) -> str:
        # check need_context
        for k in self.need_context:
            if k not in self.context:
                raise ValueError(f"缺少必要的上下文变量: {k}")

        # 里面是 键和值
        return reduce(
            lambda x, y: x.replace(y, self.context[y]),
            self.context,
            self.request_message_template,
        )

    def __pre_replace(self, rendered_template: str) -> str:
        # 里面是 键和值
        return reduce(
            lambda x, y: x.replace(y, self.pre_replace[y]),
            self.pre_replace,
            rendered_template,
        )

    def __render_template(self) -> str:
        request_message = self.__pre_replace(self.__pre_replace_context())
        return request_message

    def __post_extract(self, response: str) -> dict[str, str]:
        result = {}
        for k, v in self.post_extract.items():
            match = re.search(v, response, re.DOTALL)
            if match:
                result[k] = match.group(0)
        return result

    def parse_request(self, rendered_request: str):
        lines = rendered_request.splitlines()
        method, path, _ = lines[0].split()
        headers = {}
        body_lines = []
        empty_line_reached = False

        for line in lines[1:]:
            if line == "":
                empty_line_reached = True
                continue
            if not empty_line_reached:
                if ":" in line:
                    key, val = line.split(":", 1)
                    headers[key.strip()] = val.strip()
            else:
                body_lines.append(line)

        body = "\n".join(body_lines)
        host = headers.pop("Host", None)
        if not host:
            raise ValueError("请求头中必须包含 Host")

        url = f"{self.url_prefix}{host}{path}"

        return method, url, headers, body

    def step(self) -> dict[str, str]:
        t = self.__render_template()
        r = normalize_and_validate(t)
        method, url, headers, body = self.parse_request(r)
        response = requests.request(method, url, headers=headers, data=body)
        self.__response__ = response
        result = self.__post_extract(response.text)
        return result


class WebPayload:
    web_steps: list[WebStep]
    # 与后面步骤共享
    context: dict[str, str]

    def __init__(self, web_steps: list[WebStep]):
        self.web_steps = web_steps

    def exploit(self, context: dict[str, str]):
        self.context = context
        for ws in self.web_steps:
            ws.set_context(self.context)
            self.context.update(ws.step())
        return self

    def check(self, keys: list[str] = ["$FLAG", "$?"]):
        print(", ".join(f"{k}: {self.context.get(k, 'NOT FOUND')}" for k in keys))


# 再pre_replace 前还有一个 pre_replace_context 直接使用context里的
# pre_replace_context(数据里的变量) -> pre_replace(代码层面的变量) -> 发送请求 -> post_extract(代码层面的变量) -> 存入context
# WebPayload<context> [WebStep(data1) -> WebStep(data2) -> WebStep(data3)]
