# -*- coding: utf-8 -*-
'''
@author: shoubo.wang@dmall.com
'''
import urllib
import os
import time
import re
import adbdevice

def getLatestBuildID(rootURL):
    
    content = urllib.urlopen(rootURL).read()
    buildList = re.findall("#\d{2}|#\d{3}", content)
    latestBuild = sorted(buildList,reverse=True)
    
    return latestBuild[0].strip("#")
    
def getDownloadURL(rootURL, env="-dmtest"):
    latestBuildID = getLatestBuildID(rootURL)
    optionBuildID = int(latestBuildID) - 1
    downloadPath = rootURL + latestBuildID + "/artifact/Dmall2/build/outputs/apk/"
    content = urllib.urlopen(downloadPath)
    if content.getcode() == 404:
        downloadPath = rootURL + str(optionBuildID) + "/artifact/Dmall2/build/outputs/apk/"
        
    contents = urllib.urlopen(downloadPath).read()
    
    pattern = re.compile(r'com.wm.dmall.+?apk')
    buildNames = re.findall(pattern, contents)
    allNames = list(set(buildNames))

    for i in range(len(allNames)):
        if env in allNames[i]:
            downloadURL = downloadPath + allNames[i]
            print "当前Jenkins最新编译出的android app版本包是：{}".format(allNames[i])
            return downloadURL
        
    return None
        
def downloadAPP(downloadURL, localPath):
    fileName = downloadURL.rsplit("/", 1)[1]

    try:
        begin_time = time.ctime()
        print "开始下载文件： {}".format(begin_time)
        # urllib.urlretrieve(download_url, local_dir + os.sep + filename, url_call_back)
        # no need to callback for now
        urllib.urlretrieve(downloadURL, localPath + fileName)
        print "完成下载文件： {}".format(time.ctime())
        
    except:
        print "下载异常，请稍后再试"
        return False
        
    finally:
        target_build_size = get_length_from_server(downloadURL)
        if fileName in os.listdir(localPath):
            build_size = os.path.getsize(localPath + fileName)
            #print "the build_size is:", build_size
            if build_size < target_build_size:
                if build_size < 5 * 1000:
                    print "版本不存在，下载失败"
                    return False
                else:
                    print "{}文件下载失败，重试中.".format(fileName)
                    os.remove(localPath + fileName) 
                return False
            else:
                print "文件下载成功。保存位置为：{}".format(localPath)
                return localPath + fileName     
        

def get_length_from_server(downloadURL):
    page = urllib.urlopen(downloadURL)
    # the Content-Length part is something like: 'Content-Length: 27107189'
    result_list = re.findall("Content-Length: \d+", str(page.headers))
    if len(result_list) != 1:
        print "get the length of %r failed, return 0 as the result" % downloadURL
        return 0
    else:
        length = "".join(result_list).split(":")[1].strip()
        return int(length)
    
def isDownloaded(downloadURL, localPath):
    fileName = downloadURL.rsplit("/", 1)[1]
    if os.path.exists(localPath + fileName):
        if os.path.getsize(localPath + fileName) != get_length_from_server(downloadURL):
            print "文件下载未完成，需要重新下载."
            os.remove(localPath + fileName)
            return False
        else:
            print "文件已经在目录 {}中存在".format(localPath)
            return localPath + fileName
    else:
        print "文件尚未下载。"
        return False
    
def isReadyForInstall(downloadURL, localPath=os.getcwd() + os.path.sep):
    res = isDownloaded(downloadURL, localPath)
    retry = 3
    while retry > 0:
        if not res:
            ret = downloadAPP(downloadURL, localPath)
            if ret:
                res = ret
                break
            else: 
                retry -= 1
        else:
            break
    if not res:    
        print "文件 {}下载尝试了三次，均失败，退出下载.".format(downloadURL)        
    
    return res

if __name__ == "__main__":
    device = adbdevice.AdbCommands()
    rootURL = "http://192.168.90.98:8080/job/app_android_build/"
    flag = True # 判断当前网页链接当前是否连通
    pureInstall = False # 可配置，设置为True时为全新安装，False为覆盖安装。
    if urllib.urlopen(rootURL).getcode() == 404:
        rootURL = "http://115.182.214.16:8080/view/APP%E6%9E%84%E5%BB%BA/job/app_android_build/"
        if urllib.urlopen(rootURL).getcode() == 404:
            flag = False
            print "目前Jenkins服务不可用，请稍后再试。"
    
    if flag:
        # 需要输入想要下载测试版本的环境：
        # 测试环境：-dmtest 
        # 预发环境：-pre 
        # 正式环境：-release 
        downloadURL = getDownloadURL(rootURL,"-dmtest")
        if downloadURL:
            # 可在下面函数指定文件下载位置，不指定时默认为当前位置。
            apkFile = isReadyForInstall(downloadURL)
            if apkFile:
                if pureInstall:
                    print "你选择了全新安装，安装之前会自动卸载手机上已安装的多点App。"
                    device.uninstall_package("com.wm.dmall")
                    
                print "安装包已经就绪，马上安装。。。"    
                install = device.install_package(apkFile)
                if install:
                    print "文件安装成功。3秒后退出。"
                    time.sleep(3)
        else:
            print "下载链接获取失败，请稍后再试。"
