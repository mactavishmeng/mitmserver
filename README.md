# mitmserver
MITMServer is a "safe way" to do man-in-the-middle attack test, without using ARP attack.

MITMServer是一个无需ARP，“安全”的进行中间人攻击测试的小工具。

本工具使用Python实现了简单的反向代理服务器和DNS服务器两个功能，虽然性能上并不强大，但是日常测试是足够了。

通过设置目标设备的DNS服务器，让设备请求的DNS由本机返回，从而污染其DNS查询，将想要的流量在不使用ARP的情况下导流到本机上。

## 安装和使用

1. 从Git仓库中下载脚本：

   `git clone https://github.com/mactavishmeng/mitmserver.git`

2. 安装依赖：

   ```bash
   cd mitmserver
   pip install -r requirements.txt
   ```

3. 打开Burpsuite或Fiddler等代理抓包工具

4. 修改配置

   进入`mitmserver`文件夹，修改`mitmserver.json`：

   ```json
   {
     "proxies" : {"http": "http://127.0.0.1:8080",
                  "https":"http://127.0.0.1:8080"},
     "dns_list" : [
           {"host": "www.baidu.cn", "address": "192.168.1.3"},
           {"host": "*.baidu.cn", "address": "192.168.1.3"},
           {"host": "www.google.com", "address": "192.168.1.3"}
       ],
     "dns_query_enable" : true,
     "http_list" : [
           {"address":"0.0.0.0", "port":80, "ishttps":false},
           {"address":"0.0.0.0", "port":443, "ishttps":true, "certfile":"./certificate.crt", "keyfile":"./private_key.key"}
       ]
   }
   ```

   其中：

   `proxies` : 配置本机Burpsuite或Fiddler的地址和端口

   `dns_list`: 配置要解析的域名 (host) 的对应IP (address)，一般情况下此处的address配置成本机的局域网IP。

   `http_list`:   对外开放的HTTP服务器配置。如果需要解析HTTPS数据，需要配置 ishttps 为 true，且配置证书路径；如果仅需HTTP，则无需填写证书路径。

   `dns_query_enable`：设置为`true`表示未匹配到域名时会由python主动查询并返回结果，`false`表示不查询。如果不希望目标设备访问dns_list之外的域名，可以配置为false。

5. 运行脚本

   `python3 mitmserver.py`

6. 修改目标设备的DNS服务器，指向本机的IP（如上图配置中的`192.168.1.3`），如有必要需要清空目标设备的DNS缓存。

7. 在目标设备上访问`dns_list`列表中的域名，本机代理软件上即可抓包。

## 运行场景

IoT设备、手机设备、同局域网的其他设备需要抓取流量，而使用ARP引导有问题、效率低、抓不到包等情况。

## 问题和缺陷

1. 配置HTTPS时需要加载证书，且证书中签发的域名要与目标网站的域名一致

   由于开启的服务端是类似反向代理的功能，因此被测设备会与Python开启的端口进行HTTPS握手，如果有证书校验等环节可能会不过；

2. 每一个端口只能绑定一个域名的证书

   由于技术限制，每一个端口只能绑定一个域名所对应的证书。但是这对于日常测试应该是够用了，目前无法实现像Burpsuite那样自适应证书签名

3. 证书需要手动生成

## 声明

本工具仅供日常的授权测试使用，请勿用于非法用途！

DNS服务器的代码是参考了互联网搜索的结果，进行了部分改动。由于参考的页面上没有标注作者和出处，搜索后发现疑似为`@author: RobinTang`，侵删。

