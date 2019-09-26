class URL:
    auth_server_url = f"http://cas.swust.edu.cn/authserver/login?service="
    index_url = auth_server_url + 'http://my.swust.edu.cn/mht_shall/a/service/serviceFrontManage/cas'
    jwc_auth_url = auth_server_url + "https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:DEFAULT_EVENT"
    syk_auth_url = auth_server_url + "http://202.115.175.177/swust/"
    captcha_url = f'http://cas.swust.edu.cn/authserver/captcha'
    get_key_url = f'http://cas.swust.edu.cn/authserver/getKey'
    student_info_url = f'http://my.swust.edu.cn/mht_shall/a/service/studentInfo'
