import socket
import ssl
# 功能函数:
# 解析url产生protocol、host、port、path
def parsed_url(url):
    protocol = "http"
    if url[:7] == "http://":
        u = url.split("://")[1]
    elif url[:8] == "https://":
        protocol = "https"
        u = url.split("://")[1]
    else:
        u = url

    # 检查默认path
    i = u.find("/")
    if i == -1:
        host = u
        path = "/"
    else:
        host = u[:i]
        path = u[i:]

    # 检查端口
    port_dict = {
        "http": 80,
        "https": 443,
    }
    # 默认端口
    port = port_dict[protocol]
    if ":" in host:
        h = host.split(":")
        host = h[0]
        port = int(h[1])

    return protocol, host, port, path


# 根据协议返回socket实例
def socket_by_protocol(protocol):
    if protocol == "http":
        s = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)             # 生成一个socket对象
        s.settimeout(10)
    else:
        # HTTPS 协议需要使用 ssl.wrap_socket 包装一下原始的 socket
        # 除此之外无其他差别
        s = ssl.wrap_socket(socket.socket(socket.AF_INET6,socket.SOCK_STREAM))
        s.settimeout(10)
    return s


# 根据socket对象接受数据
def response_by_socket(s):
    response = b""
    buffer_size = 1024
    while True:
        r = s.recv(buffer_size)
        if len(r) == 0:
            break
        response += r
    return response

# 把 response 解析出 状态码 headers body 返回
def parsed_response(r):
    header, body = r.split('\r\n\r\n', 1)
    h = header.split('\r\n')
    # headers的头部: HTTP/1.1 200 OK
    status_code = h[0].split()[1]
    status_code = int(status_code)

    headers = {}
    for line in h[1:]:
        k, v = line.split(': ')
        headers[k] = v
    return status_code, headers, body

# 主逻辑函数:
# 把向服务器发送 HTTP 请求并且获得数据这个过程封装成函数 -> 复杂的逻辑(具有重用性)封装成函数
def get(url):
    protocol, host, port, path = parsed_url(url)
    # 得到socket对象并连接服务器
    s = socket_by_protocol(protocol)
    try:
        s.connect((host, port))

        # 发送请求
        request = 'GET {} HTTP/1.1\r\nhost: {}\r\nConnection: close\r\n\r\n'.format(path, host)
        encoding = 'utf-8'
        s.send(request.encode(encoding))

        # 获得响应
        response = response_by_socket(s)
        r = response.decode(encoding)

        # 解析响应
        status_code, headers, body = parsed_response(r)
        # 当状态码为301或302时表示为重定向
        if status_code in [301, 302]:
            url = headers['Location']
            return get(url)
        if status_code==200:
            status_code ='Y'
        else:
            status_code = 'N'
    except:
        status_code='N'
        headers='N'
        body='N'
    return status_code, headers, body

# 使用:
def main():
    url = 'http://hubt.hust.edu.cn'
    # r = get(url)
    # print(r)
    status_code, headers, body = get(url)
    print("status_code: ", status_code)
    #print("headers: ", headers)
    #print("body: ", body)


if __name__ == '__main__':
    # test_parsed_url()
    # test_get()
    main()

