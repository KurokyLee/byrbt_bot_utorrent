# byrbt_pt_utorrent

适用于 uTorrent 的 ByrBT 自动做种机器人。项目来源于[byrbt_bot](https://github.com/ByrBT/byrbt_bot)，完成了适配 uTorrent 和一些可视化的工作。utorrent api 文档参考自[utorrent-web-api](https://github.com/LakithaRav/uTorrent-client-python)。

## Usage

1. 本项目使用的环境为Python 3.7，与byrbt_bot一致，请确保已安装相应版本的Python环境。安装依赖包：
```bash
pip install -r requirements.txt
```

2. 本项目仅支持Windows系统下的uTorrent客户端，uTorrent版本为3.3.1。请确保uTorrent开启了WebUI功能，并正确配置了用户名和密码，WebUI安装教程请参考[这里](https://www.spiral-scratch.com/utorrent_subdomain/Guides/webui.html)，下载后请在uTorrent的 <u>选项-设置-高级-网页界面</u> 中启用网页界面，同时配置默认下载目录，并设置用户名和密码，并且选择相应端口。之后在浏览器输入localhost:端口号/gui即可登陆uTorrent WebUI。

3. 请在config/config.ini中正确配置uTorrent的WebUI地址、端口号、用户名和密码，以及byrbt的账号和密码。

4. 启动机器人：
```bash
python run.py
```
5. 机器人启动后会自动连接uTorrent客户端，并开始监控种子下载情况，完成下载后会自动上传种子并开始做种。日志将输出至logs文件夹下。

## Acknowledgements

本项目大量复制了[byrbt_bot](https://github.com/ByrBT/byrbt_bot)的代码结构和逻辑，感谢原作者的贡献。

本项目参考了[utorrent-web-api](https://github.com/LakithaRav/uTorrent-client-python)项目中的uTorrent API调用方法，感谢该项目的贡献者。