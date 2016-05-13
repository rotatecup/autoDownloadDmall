# -*- coding: utf-8 -*-
import time,os,sys
import subprocess
import logging
import thread
import platform

def adb_path():
    cur_path = os.path.dirname(os.path.abspath(__file__))
    osName = platform.system()
    if osName == "Windows":
        return os.path.join(cur_path, 'windows', 'adb.exe ')
    elif osName == "Linux":
        return os.path.join(cur_path, 'linux', 'adb ')
    elif osName == "Darwin":
        return os.path.join(cur_path, 'mac', 'adb ')
    else:
        print "unknown system" 
        return
    
class AdbCommands():
    def __init__(self, adbArgv=None):
        """
        @param adbArgv:adb
        @author: shwang
        @sample: 
        adbd = AdbCommands("-s 015F3EE203017013")
        """
        self.adb=adb_path()
        if adbArgv:
            self.adb = self.adb + adbArgv + " "
        
    def timer(self,process,timeout):
        num=0
        while process.poll()==None and num<timeout*10:
            num+=1
            time.sleep(0.1)
        if process.poll()==None:
            os.system("taskkill /T /F /PID %d"%process.pid)
            print "%d process timeout ,be killed！"%process.pid
        thread.exit_thread()

    def runShellCmd(self,Cmd,TimeOut=3):
        return self.runCmd("shell \"%s\" "%Cmd, TimeOut)
    
    def runCmdOnce(self,Cmd,TimeOut=3):
        process=subprocess.Popen(self.adb+Cmd,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True)
        thread.start_new_thread(self.timer,(process,TimeOut))   
        res=process.stdout.read()
        process.wait()
        if process.poll() != 0:
            error=process.stderr.read()
            print error
            if "killing" in (res or error):
                print 
                sys.exit(1)
            if ("device not found" or "offline") in (res or error):
                print 'Please confirm you phone have connect to PC!!!'
                sys.exit(1)
            if "Android Debug Bridge version" in (res or error):
                print 'Adb cmd error!!!! Please check you adb cmd!!!'
                sys.exit(1)
            if "more than one" in (res or error):
                print 'More then one device, Please set -d option '
                sys.exit(1)
            sys.exit(1)
        res=res.replace("\r\n","\n").splitlines()
        return res
        
    def runCmd(self,Cmd,TimeOut=3,Retry=3):
        while Retry>=0:
            res=self.runCmdOnce(Cmd, TimeOut)
            if res!=None:
                break
            Retry-=1
        return res
        
    def install_package(self,path,TimeOut=30):
        res=self.runCmd("install -r \"%s\""%path, TimeOut)
        if res==None or "Failure" in res[1]:
            logging.log(logging.WARN,"Failed to install application.")
            return False
        else:
            #logging.log(logging.WARN,"Install:%s successfully"%path)
            return True
    
    def uninstall_package(self,package,TimeOut=30):
        if self.runCmd("uninstall %s"%package, TimeOut)==None:
            logging.log(logging.WARN,"Failed to uninstall application.")
            return False
        logging.log(logging.WARN,"Uninstall:%s"%package)
        return True

        
class AndroidDevice(AdbCommands):
    
    def __init__(self,serialNumber = None):
        if serialNumber:
            AdbCommands.__init__(self,"-s %s"%self.serialNumber)
        else:
            AdbCommands.__init__(self)

    
    