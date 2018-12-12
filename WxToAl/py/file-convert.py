import io
import sys
import os,re,shutil

fileencoding = "utf-8"
programrootdir = ""  #微信小程序程序根目录
alprogramrootdir = "" #支付宝小程序根目录
error = ""
def init(file, encoding='utf-8'):
    global fileencoding,programrootdir,alprogramrootdir

    if len(encoding) > 0:
        fileencoding = encoding


    #获取文件名称
    filearray = os.path.split(file)
    filename = filearray[1]
    programrootdir = filearray[0]

    printLog("文件名" + filename)
    printLog("目录" + programrootdir)

    if not filename == 'app.js':
        printLog("不是app.js文件，不支持转换！")
        return

    alprogramrootdir = os.path.join(prevDir(programrootdir), "alprogram")
    printLog("支付宝小程序根目录" + alprogramrootdir)
    #先创建项目目录
    mkdirDir(alprogramrootdir)
    #处理app.js
    #content = readFile(file)
    #writeFile(os.path.join(alprogramrootdir, "app.js"), content)

    #处理app.json
    #content = readFile(os.path.join(programrootdir, "app.json"))

    #content = re.sub('[\"\']navigationBarBackgroundColor[\"\']', r'"titleBarColor"', content)
    #content = re.sub('[\"\']navigationBarTitleText[\"\']', r'"defaultTitle"', content)
    #content = re.sub('[\"\']enablePullDownRefresh[\"\']', r'"pullRefresh"', content)

    #tab 处理
    #content = re.sub('[\"\']color[\"\']', r'"textColor"', content)
    #content = re.sub('[\"\']list[\"\']', r'"items"', content)
    #content = re.sub('[\"\']text[\"\']', r'"name"', content)
    #content = re.sub('[\"\']iconPath[\"\']', r'"icon"', content)
    #content = re.sub('[\"\']selectedIconPath[\"\']', r'"activeIcon"', content)

    #writeFile(os.path.join(alprogramrootdir, "app.json"), content)

    #app.wxss 处理
    #content = readFile(os.path.join(programrootdir, "app.wxss"))
    #content = re.sub('app.wxss', 'app.acss', content)
    #writeFile(os.path.join(alprogramrootdir, "app.acss"), content)


    #项目配置文件,支付宝没有
    #content = readFile(os.path.join(programrootdir, "project.config.json"))

    #处理非页面文件
    #处理

    eachPath(programrootdir)

def eachPath(path):
    for filename in os.listdir(path):
        filePath = os.path.join(path, filename)
        #读取文件名称
        printLog("file=" + filename)
        #是文件就处理文件
        if os.path.isfile(filePath):
            if filename == "app.js":
                #处理app.js
                handleAppJs(filePath)
            elif filename == "app.json":
                handleAppJson(filePath)
            elif filename == "app.wxss":
                handleAppWxss(filePath)
            elif os.path.splitext(filePath)[1].lower() == '.png':
                #直接复制图片
                handlePng(filePath)
            elif os.path.splitext(filePath)[1] == '.wxml':
                handlePage(filename, filePath)
            elif os.path.splitext(filePath)[1] == '.wxss':
                printLog("wxss 不处理")
            else:
                #其他文件就判断是否存在，不存在则直接复制
                handleOtherFile(filename, filePath)


        if os.path.isdir(filePath):
            eachPath(filePath)

#处理app.js
def handleAppJs(path):
    global alprogramrootdir
    #处理app.js
    content = readFile(path)

    content = re.sub('wx.', r'my.', content);

    writeFile(os.path.join(alprogramrootdir, "app.js"), content)

#处理app.json
def handleAppJson(path):
    global alprogramrootdir
    #处理app.json
    content = readFile(path)

    content = re.sub('[\"\']navigationBarBackgroundColor[\"\']', r'"titleBarColor"', content)
    content = re.sub('[\"\']navigationBarTitleText[\"\']', r'"defaultTitle"', content)
    content = re.sub('[\"\']enablePullDownRefresh[\"\']', r'"pullRefresh"', content)

    #tab 处理
    content = re.sub('[\"\']color[\"\']', r'"textColor"', content)
    content = re.sub('[\"\']list[\"\']', r'"items"', content)
    content = re.sub('[\"\']text[\"\']', r'"name"', content)
    content = re.sub('[\"\']iconPath[\"\']', r'"icon"', content)
    content = re.sub('[\"\']selectedIconPath[\"\']', r'"activeIcon"', content)

    writeFile(os.path.join(alprogramrootdir, "app.json"), content)

#处理app.wxss
def handleAppWxss(path):
    global alprogramrootdir
    #处理app.wxss
    content = readFile(path)
    content = re.sub('app.wxss', 'app.acss', content)
    writeFile(os.path.join(alprogramrootdir, "app.acss"), content)

#处理图片
def handlePng(path):
    alPath = convertAlDir(path)

    if not os.path.isfile(alPath):
        mkdirDir(alPath)
        shutil.copyfile(path, alPath)

#处理页面、组件文件
def handlePage(filename, path):
    alPath = convertAlDir(path)

    #获取文件名称和后缀
    array = filename.split(".");
    #是页面文件，就需要同时处理其他 json, js, wxss文件
    if array[1] == "wxml":
        alAxmlPath = os.path.splitext(alPath)[0] + ".axml"
        #if not os.path.isfile(alAxmlPath):
        mkdirDir(alAxmlPath)
        
        handlePageWxml(alAxmlPath, path)

        alAxmlPath = os.path.splitext(alPath)[0] + ".acss"
        #if not os.path.isfile(alAxmlPath):
        handlePageAcss(alAxmlPath, os.path.splitext(path)[0] + ".wxss")

        alAxmlPath = os.path.splitext(alPath)[0] + ".js"
        #if not os.path.isfile(alAxmlPath):
        handlePageJs(alAxmlPath, os.path.splitext(path)[0] + ".js")

        alAxmlPath = os.path.splitext(alPath)[0] + ".json"
        #if not os.path.isfile(alAxmlPath):
        handlePageJson(alAxmlPath, os.path.splitext(path)[0] + ".json")

def handlePageWxml(alPath, path):
    content = readFile(path)

    #替换掉wxml
    content = re.sub(r'<import\s+src=["\'](.*).wxml"', r'<import src="\1.axml"', content)
    content = re.sub(r'<include\s+src=["\'](.*).wxml"', r'<include src="\1.axml"', content)
    content = re.sub(r'<import\s+src=["\']\s*([^./].+)\.axml"', r'<import src="./\1.axml"', content)
    content = re.sub(r'<include\s+src=["\']\s*([^./].+)\.axml"', r'<include src="./\1.axml"', content)

    #判断
    content = re.sub('wx:for', r'a:for', content)
    content = re.sub('wx:for-index', r'a:for-index', content)
    content = re.sub('wx:for-item', r'a:for-item', content)
    content = re.sub('wx:key', r'a:key', content)
    content = re.sub('wx:if', r'a:if', content)
    content = re.sub('wx:else', r'a:else', content)
    content = re.sub('wx:elif', r'a:elif', content)

    #替换掉bind:tap
    content = re.sub('bindtap', r'onTap', content)
    content = re.sub('bind:tap', r'onTap', content)
    content = re.sub('catch:tap', r'catchTap', content)
    content = re.sub('catchtap', r'catchTap', content)
    content = re.sub('capture-bind:touchmove', r'catchTouchMove', content)
    content = re.sub('capture-bind:touchstart', r'catchTouchStart', content)
    content = re.sub('capture-bind:touchend', r'catchTouchEnd', content)
    content = re.sub('capture-bind:touchcancel', r'catchTouchCancel', content)
    content = re.sub('bind:touchmove', r'onTouchMove', content)
    content = re.sub('bind:touchstart', r'onTouchStart', content)
    content = re.sub('bind:touchend', r'onTouchEnd', content)
    content = re.sub('bind:touchcancel', r'onTouchCancel', content)
    content = re.sub('capture-catch:touchmove', r'catchTouchMove', content)
    content = re.sub('capture-catch:touchstart', r'catchTouchStart', content)
    content = re.sub('capture-catch:touchend', r'catchTouchEnd', content)
    content = re.sub('capture-catch:touchcancel', r'catchTouchCancel', content)


    writeFile(alPath, content)

def handlePageAcss(alPath, path):
    if not os.path.isfile(path):
        return
    content = readFile(path)

    writeFile(alPath, content)

def handlePageJs(alPath, path):
    if not os.path.isfile(path):
        return
    content = readFile(path)

    content = re.sub('currentTarget', r'target', content)

    writeFile(alPath, content)

def handlePageJson(alPath, path):
    if not os.path.isfile(path):
        return
    content = readFile(path)

    content = re.sub('[\"\']navigationBarBackgroundColor[\"\']', r'"titleBarColor"', content)
    content = re.sub('[\"\']navigationBarTitleText[\"\']', r'"defaultTitle"', content)
    content = re.sub('[\"\']enablePullDownRefresh[\"\']', r'"pullRefresh"', content)

    writeFile(alPath, content)

#处理其他文件
def handleOtherFile(filename, path):
    alPath = convertAlDir(path)

    if len(filename.split(".")[0]) == 0:
        return

    if filename == "project.config.json":
        return

    if not os.path.isfile(alPath):
        mkdirDir(alPath)
        shutil.copyfile(path, alPath)

#读取文件
def readFile(filename):
    global fileencoding
    f = open(filename, "r", encoding=fileencoding)
    content = f.read()
    f.close()

    return content

#写文件
def writeFile(filename, content):
    global fileencoding

    w_file = open(filename, "w", encoding=fileencoding)
    w_file.write(content)
    w_file.close()

#将微信小程序目录转换到支付宝小程序目录,并创建目录
def convertAlDir(path):
    global alprogramrootdir,programrootdir
    #wxDir = os.path.split(path)
    subDir = path.split(programrootdir)[1]

    printLog("微信小程序目录=" + path)
    printLog("支付宝小程序目录="+ os.path.join(alprogramrootdir, subDir))

    return alprogramrootdir + subDir #os.path.join(alprogramrootdir, subDir)

#获取上一级目录
def prevDir(path):
    array = path.split('/')
    array.pop()
    return "/".join(array)

#处理目录或者文件，如果目录或文件存在则不处理，返回false, 否则需要新建文件或目录
def mkdirDir(path):
    array = os.path.splitext(path)
    printLog("是文件" + array[0])
    if len(array[1]) > 0:
        path = os.path.split(path)[0]
        mkdirDir(path)
    
    if  not os.path.isdir(path):
        printLog("创建目录" + path)
        os.makedirs(path)
       

def printLog(string):
    print("信息", string)
    return
    global error
    error = error + string + '\n'

def getLog():
    return "小程序转换处理\n---------------------转换日志-----------------------\n" + error + "---------------------转换日志信息-----------------------\n"