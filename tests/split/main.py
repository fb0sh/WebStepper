from .web1 import web1
from web import file2ip_list

if __name__ == "__main__":
    for ip in file2ip_list("ip.txt"):
        # web1
        for wp in web1:
            try:
                wp.exploit({"$IP": ip}).check()
            except Exception as e:
                print(e)
