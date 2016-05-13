'''
@author: shwang
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
            print "The latest build is {}".format(allNames[i])
            return downloadURL
        
    return None
        
def downloadAPP(downloadURL, localPath):
    fileName = downloadURL.rsplit("/", 1)[1]

    try:
        begin_time = time.ctime()
        print "Begin to download file at {}".format(begin_time)
        # urllib.urlretrieve(download_url, local_dir + os.sep + filename, url_call_back)
        # no need to callback for now
        urllib.urlretrieve(downloadURL, localPath + fileName)
        print "Finish downloading file at {}".format(time.ctime())
        
    except:
        print "exception happened"
        return False
        
    finally:
        target_build_size = get_length_from_server(downloadURL)
        if fileName in os.listdir(localPath):
            build_size = os.path.getsize(localPath + fileName)
            #print "the build_size is:", build_size
            if build_size < target_build_size:
                if build_size < 5 * 1000:
                    print "build doesn't exist"
                    return False
                else:
                    print "download error, need to download {} again.".format(fileName)
                    os.remove(localPath + fileName) 
                return False
            else:
                print "Download successfully"
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
            print "Download unfinished. Need download again."
            os.remove(localPath + fileName)
            return False
        else:
            print "Already downloaded in the directory {}".format(localPath)
            return localPath + fileName
    else:
        print "Not download yet."
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
        print "tried downloading from {} for 3 times, but all failed.".format(downloadURL)        
    
    return res

if __name__ == "__main__":
    device = adbdevice.AdbCommands()
    rootURL = "http://115.182.214.16:8080/view/APP%E6%9E%84%E5%BB%BA/job/app_android_build/"
    # -dmtest is for test environment
    # -pre is for prerelease environment
    # -release is for release environment
    downloadURL = getDownloadURL(rootURL,"-dmtest")
    if downloadURL:
        # You can type a path to store the downloaded file. If not, the default path is the current directory.
        apkFile = isReadyForInstall(downloadURL)

        need_uninstall = False
		
        if apkFile:
            if need_uninstall:
                device.uninstall_package("com.wm.dmall")
            print "The latest APK is downloaded successfully. Will start to install it now..."    
            install = device.install_package(apkFile)
            if install:
                print "Install successfully"
    else:
        print "Can not fetch the download url currently. Please try again later"
