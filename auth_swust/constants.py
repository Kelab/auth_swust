import socket

my_swust_url = 'my.swust.edu.cn'
dean_url = 'matrix.dean.swust.edu.cn'
cas_swust_url = "cas.swust.edu.cn"

cas_swust_ip = socket.gethostbyname(cas_swust_url)
_ = socket.gethostbyname(my_swust_url)
_ = socket.gethostbyname(dean_url)


class URL():
    auth_server = f"http://{cas_swust_ip}/"
    auth_server_url = f"http://{cas_swust_ip}/authserver/login?service="
    index_url = auth_server_url + 'http://my.swust.edu.cn/mht_shall/a/service/serviceFrontManage/cas'
    jwc_auth_url = auth_server_url + "https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:DEFAULT_EVENT"
    syk_auth_url = auth_server_url + "http://202.115.175.177/swust/"
    captcha_url = f'http://{cas_swust_ip}/authserver/captcha'
    get_key_url = f'http://{cas_swust_ip}/authserver/getKey'
    student_info_url = f'http://{my_swust_url}/mht_shall/a/service/studentInfo'
