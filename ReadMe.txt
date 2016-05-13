autoDownloadDamll for Android

@author shoubo.wang@dmall.com
@date 2016-5-12
@version V1.0
@程序主入口：installDmall.py

本程序主要的功能为自动从jenkins上下载并安装最新编译的android apk包，运行环境为python 2.x版本，
并兼容Windows，Linux和Mac系统。

预置条件：
1、Android手机在开发者选项中开启了允许USB调试；
2、Windows系统上可能需要安装好该手机的驱动程序（连接手机后一般都会自动安装，安装一次即可）；
3、python环境，建议使用2.7.x的版本。

运行参数说明：
1、downloadURL = getDownloadURL(rootURL,"-dmtest")
该函数第二个参数位置支持三个参数，分别为"-dmtest"（测试环境），“-pre”（预发环境）和“-release”(正式环境）

2、apkFile = isReadyForInstall(downloadURL)
该函数也是支持两个参数的，第二个参数是指app下载目录，默认（不填写）为脚本运行的目录，但也支持指定目录，如apkFile = isReadyForInstall(downloadURL, "D:\\Softwares\\")

3、need_uninstall = False
该参数默认为False，即为覆盖安装，这种安装会保留之前版本的数据。在如下几种情况下需要将该参数设置为True：
a、需要全新安装
b、手机上装有更高的版本（android不支持直接降级安装）
c、需要装另外环境的包。由于不同环境的包签名不一样，所以这种情况下也只能走全新安装的流程，比如手机装有测试环境的包，但现在需要安装正式环境的包。


其他说明：
此程序依赖于目前jekins的参数配置，如果遇到jekins更改部分参数设置或者jekins服务不可用时，本程序有可能会直接出错，请知悉。