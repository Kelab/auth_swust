class URL():
    auth_server_url = "http://cas.swust.edu.cn/authserver/login?service="
    index_url = auth_server_url + 'http://my.swust.edu.cn/mht_shall/a/service/serviceFrontManage/cas'
    jwc_auth_url = auth_server_url + "https://matrix.dean.swust.edu.cn/acadmicManager/index.cfm?event=studentPortal:DEFAULT_EVENT"
    captcha_url = 'http://cas.swust.edu.cn/authserver/captcha'
    student_info_url = 'http://my.swust.edu.cn/mht_shall/a/service/studentInfo'
    get_key_url = 'http://cas.swust.edu.cn/authserver/getKey'
