#coding=utf-8

#目录下的 html 文件重命名后缀
#for i in `find . -name "*.html"`; do mv "$i" "${i%.html}.htm"; done; 遍历目录下所有html文件，后缀修改为.htm

#目录下所有 xls 文件 移动到 9、监控专业题库/ 目录下
#for i in `find . -name "*.xls"`; do cp "$i" "9、监控专业题库/"; done

import io
import sys
import re, shutil,os

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

fileencoding = "utf-8"
content = ""
error = ""
def init(file, encoding='utf-8'):
    global fileencoding,content,error,choiceAnswers,choiceAnswerIndex,trueFalseAnswers,trueFalseAnswerIndex,fillInAnswers,fillInAnswerIndex

    error = ""
    #选择题答案
    choiceAnswers = []
    choiceAnswerIndex = -1

    #判断题答案
    trueFalseAnswers = []
    trueFalseAnswerIndex = -1

    #填空题答案
    fillInAnswers = []
    fillInAnswerIndex = -1

    if len(encoding) > 0:
        fileencoding = encoding


    print("ext", os.path.splitext(file))
    if not os.path.splitext(file)[1] == '.txt' :
        print("只支持txt文件操作")
        return
    
    #读取word txt 试卷，只能处理选择题文件
    f = open(file, "r", encoding=fileencoding)
    content = f.read()
    f.close()

    #获取答案
    handleAnswerList()

    rexTxt()

    handleTxtQuestion()



    #获取文件名称
    filearray = os.path.splitext(file)
    filename = filearray[0].split('/').pop()


    dir = filearray[0]

    print("dir", dir)
    filename = os.path.join(dir, filename + "_mtestm.txt")
    print("filename", filename)

    if not os.path.exists(dir):
        os.mkdir(dir)

    writeTxt(filename)

def printError(string):
    global error
    error = error + string + '\n'

#下文件名称
def writeTxt(filename):
    global fileencoding,content

    #console.log("filename", filename)

    #写文件
    content = re.sub('\n\s*\n', r'\n', content)

    w_file = open(filename, "w", encoding=fileencoding)
    w_file.write(content)
    w_file.close()

def rexTxt():
    global fileencoding,content
    #替换．为.
    content = re.sub('．', r'.', content)

    #替换ＡＢＣＤ
    content = re.sub('Ａ', r'A', content)
    content = re.sub('Ｂ', r'B', content)
    content = re.sub('Ｃ', r'C', content)
    content = re.sub('Ｄ', r'D', content)
    content = re.sub('Ｅ', r'E', content)
    content = re.sub('Ｆ', r'F', content)

    #题号没有、.符号的
    content = re.sub('\n\s*(\d+)([^、\.\d])', r'\n\1、\2', content)


    #题干中没有答案的 例如  1、(  ) 题干。
    content = re.sub('\n\s*(\d+[、\.].*?)\n*[\(（]\s*_*(\s*)_*[\)）](.*)', r'\n\1()\3【正确答案】', content)

    #题干中包含答案的 例如  1、题干( A )。
    content = re.sub('\n\s*(\d+[、\.].*?)\n*[\(（]\s*_*\s*([A-G]{1,5})\s*_*\s*[\)）](.*)', r'\n\1()\3【正确答案】\2', content)

    #判断题干中包含答案  例如  （错误） 
    content = re.sub('\n\s*(\d+[、\.].*?)\n*[\(（]\s*_*\s*错误\s*_*\s*[\)）](.*)', r'\n\1()\2【正确答案】错', content)

    #判断题干中包含答案  例如  （正确） 
    content = re.sub('\n\s*(\d+[、\.].*?)\n*[\(（]\s*_*\s*正确\s*_*\s*[\)）](.*)', r'\n\1()\2【正确答案】对', content)

    #判断题干中包含答案  例如  xxX 错 
    content = re.sub('\n\s*(\d+[、\.].*?)\n*[\(（]\s*_*\s*([×xX错])\s*_*\s*[\)）](.*)', r'\n\1()\3【正确答案】错', content)

    #判断题干中包含答案  例如  对
    content = re.sub('\n\s*(\d+[、\.].*?)\n*[\(（]\s*_*\s*([/√V对])\s*_*\s*[\)）](.*)', r'\n\1()\3【正确答案】对', content)

    #选项 A B C D 全部换行
    content = re.sub('[\s(（]([A-G])[、.]', r'\n\1、', content)

    #选项A B C D 中 空格， 例如 A 文字 B 文字
    content = re.sub('\n([A-G])\s+', r'\n\1、', content)
    #print('content', content)
    content = re.sub('\n[A-F].*?([B-G])\s+', r'\n\1、', content)
    #content = re.sub('[^】A-G，,]([B-G])\s+', r'\n\1、', content)

    #选项A B C D 中用括号包含起来， 例如 (A) 文字 (B) 文字
    content = re.sub('\n\s*[(（]\s*([A-G])\s*[)）]', r'\n\1、', content)

    content = re.sub('[^】A-G，,][(（]\s*([B-G])\s*[)）]', r'\n\1、', content)

    #选项和文字连在一起, 例如 A文字
    content = re.sub('\n([A-G])([^、\.])', r'\n\1、\2', content)

    #选项和文字连在一起, 例如 A文字  B文字
    content = re.sub('\n([A-G].+\s+)B([^、\.])', r'\n\1\nB、\2', content)
    content = re.sub('\n([A-G].+\s+)C([^、\.])', r'\n\1\nC、\2', content)
    content = re.sub('\n([A-G].+\s+)D([^、\.])', r'\n\1\nD、\2', content)
    content = re.sub('\n([A-G].+\s+)E([^、\.])', r'\n\1\nE、\2', content)


#判断题处理

#content = re.sub('\n(\d+[、.])(.+)[^【正确答案】]', r'\n\1\2【正确答案】错\n', content);

#content = f.readlines()

#填入选择题答案，如果选择题有答案则放弃填入答案

#选择题答案
choiceAnswers = []
choiceAnswerIndex = -1

#判断题答案
trueFalseAnswers = []
trueFalseAnswerIndex = -1

#填空题答案
fillInAnswers = []
fillInAnswerIndex = -1

#获取答案
#题号1重复次数
def handleAnswer(answerStr):
    global choiceAnswers,trueFalseAnswers,fillInAnswers

    answerStr = re.sub('\n', r' ', answerStr)
    #print("答案", answerStr)

    choiceAnswer = re.search('【选择】(.*?)【选择】', answerStr)
    if choiceAnswer:
        #添加选择题答案
        findAlls = re.findall('(\d+)[\.、\s]([A-F]{1,6})', choiceAnswer.group(1), re.M);
        array = {}
        for item in findAlls:
            array[item[0]] = item[1]
        #print("选择答案",choiceAnswer.group(1))

        choiceAnswers.append(array)


    trueFalseAnswer = re.search('【判断】(.*?)【判断】', answerStr)
    if trueFalseAnswer:
        #添加判断题答案
        #获取判断题答案列表 例如  1.错 2.对 3.错
        array = {}
        findAlls = re.findall('(\d+)[\.、\s]([错对])', trueFalseAnswer.group(1), re.M);
        for item in findAlls:
            array[item[0]] = item[1]

        if len(findAlls) == 0:

            findAlls = re.findall('([错对])', trueFalseAnswer.group(1), re.M);
            n = 1
            for item in findAlls:
                #print("item", item)
                array[str(n)] = item
                n = n + 1

        trueFalseAnswers.append(array)

    fillInAnswer = re.search('【填空】(.*?)【填空】', answerStr)
    if fillInAnswer:
        fillInAnswerStr = re.sub('(\d+)[.、\s]', r'\n\1.', fillInAnswer.group(1))
        findAlls = re.findall('(\d+)[\.、\s](.*)', fillInAnswerStr, re.M);
        array = {}
        for item in findAlls:

            array[item[0]] = item[1].strip().split("；")
        fillInAnswers.append(array)
    return 
    #获取选择题答案列表
    selectAnswerArray = re.findall('(\d+)[\.、\s]([A-F]{1,6})', answerStr, re.M);

    array = {}
    for item in selectAnswerArray:
        if item[0] == '1':
            array = {}
            answerArray.append(array)
            #print("题号为1") 
        array[item[0]] = item[1]

    #获取判断题答案列表 例如  1.错 2.对 3.错
    truFalseAnswerArray = re.findall('(\d+)[\.、\s]([错对])', answerStr, re.M);
    for item in truFalseAnswerArray:
        if item[0] == '1':
            array = {}
            answerArray.append(array)
            #print("题号为1") 
        array[item[0]] = item[1]

    if len(truFalseAnswerArray) == 0:

        truFalseAnswerArray = re.findall('([错对])', answerStr, re.M);
        n = 1
        array = {}
        answerArray.append(array)
        for item in truFalseAnswerArray:
            #print("item", item)
            array[str(n)] = item
            n = n + 1
#获取答案列表
def handleAnswerList():
    global content

    #获取答案 答案信息在【答案开始】【答案结束】之间
    #
    pos = 0
    while True:
        answerStart = re.compile('【答案开始】')
        answerEnd = re.compile('【答案结束】')

        searchObj = answerStart.search(content,pos)
        if searchObj:
            print("发现答案开始")
            start = searchObj.end()
            searchObj = answerEnd.search(content,start)
            if searchObj:
                print("发现答案结束")
                pos = searchObj.end()
                #获取答案内容，处理答案
                answerStr = content[start:searchObj.start()]
                #print("answerStr", start, searchObj.start(),answerStr)

                handleAnswer(answerStr)
        else:
            break

    printError("【选择题答案】{}".format(choiceAnswers))
    printError("【判断题答案】{}".format(trueFalseAnswers))
    printError("【填空题答案】{}".format(fillInAnswers))

#插入选择题答案
def insertChoiceAnswerAtPos(content, searchObj):
    global choiceAnswers,choiceAnswerIndex
    #获得答案
    key = searchObj.group(1)
    if key == '1':
        #题号1出现后，answerIndex 加1
        choiceAnswerIndex = choiceAnswerIndex + 1
        #print('choiceAnswerIndex', choiceAnswerIndex)

    pos = searchObj.end()

    answer = ''
    if len(choiceAnswers) > choiceAnswerIndex:
        answer = choiceAnswers[choiceAnswerIndex].get(key)
        #print('answer = ', answer)

    return content[:pos] + answer + content[pos:]

#插入判断题答案
def insertTrueFalseAnswerAtPos(content, searchObj):
    global trueFalseAnswers, trueFalseAnswerIndex
    #获得答案
    key = searchObj.group(1)
    if key == '1':
        #题号1出现后，answerIndex 加1
        trueFalseAnswerIndex = trueFalseAnswerIndex + 1
        #print('trueFalseAnswerIndex', trueFalseAnswerIndex)

    pos = searchObj.end()

    answer = ''
    if len(trueFalseAnswers) > trueFalseAnswerIndex:
        answer = trueFalseAnswers[trueFalseAnswerIndex].get(key)
        #print('answer = ', answer)

    return content[:pos] + answer + content[pos:]

#处理选择题答案
def handleSelectQuestion():
    global content,answerArray
    
    #填入答案
    pattern = re.compile(r'\n(\d+)([、\.].*[\(（]\s*_*\s*\s*_*[\)）].*)\n*A[、.]')

    choicePattern = re.compile(r'\n(\d+)([、\.].*[\(（]\s*_*\s*\s*_*[\)）].*)')

    pos = 0
    while True:
        searchObj = pattern.search(content, pos)
        if not searchObj:
            #print("选择题完成")
            break

        else:
            #如果选择题没有答案，需要重新匹配填入答案位置
            searchObj = choicePattern.search(content, pos)

        pos = searchObj.end()

        content = insertChoiceAnswerAtPos(content, searchObj)

#处理判断题答案
def handleTrueFalseQuestion():
    global content,answerArray
    
    #填入答案
    pattern = re.compile(r'\n(\d+)([、\.].*[\(（]\s*_*\s*\s*_*[\)）].*【正确答案】)\n*[^A]')

    trueFalsePattern = re.compile(r'\n(\d+)([、\.].*[\(（]\s*_*\s*\s*_*[\)）].*)')

    pos = 0
    while True:
        searchObj = pattern.search(content, pos)
        if not searchObj:
            #print("判断题完成")
            break
        else:
            #如果选择题没有答案，需要重新匹配填入答案位置
            searchObj = trueFalsePattern.search(content, pos)
        pos = searchObj.end()

        content = insertTrueFalseAnswerAtPos(content, searchObj)

#填空题填入答案
def handleFillInAnswer():
    global content,fillInAnswers, fillInAnswerIndex


    fillPattern = re.compile(r'\n(\d+)([、\.].*【填空答案】)')
    pos = 0
    while True:
        searchObj = fillPattern.search(content, pos)
        if not searchObj:
            #print("填空题完成")
            break
        else:
            #如果选择题没有答案，需要重新匹配填入答案位置
            startPos = searchObj.start();
            pos = searchObj.end()

            #获得答案
            key = searchObj.group(1)
            if key == '1':
                #题号1出现后，answerIndex 加1
                fillInAnswerIndex = fillInAnswerIndex + 1
                print('fillInAnswerIndex', fillInAnswerIndex)

            if len(fillInAnswers) > fillInAnswerIndex:
                answers = fillInAnswers[fillInAnswerIndex].get(key)

                fillInQuestion = searchObj.group(1) + searchObj.group(2)


                findAlls = re.findall(r'【填空答案】', fillInQuestion)

                #print("fillInQuestion", fillInQuestion)
                #print("判断", len(findAlls) == len(answers))
                if findAlls and answers and len(findAlls) == len(answers):
                    answer = ''
                    for string in answers:
                        answer = answer + "【填空答案】" + string + '\n'

                    fillInQuestion = re.sub(r'【填空答案】', '', fillInQuestion)
                    content = content[:startPos] + '\n' + fillInQuestion + answer + content[pos:]
                else:
                    printError("填空题填入答案有误，位置是【{}】".format(fillInQuestion))
                #print('answer = ', answer)
        

#处理填空题
def handleFillBlackQuestion():
    global content,answerArray
    #填空题处理
    content = re.sub('[\n。][<>]', r'\n', content)

    content = re.sub('\n\s*[<>]', r'\n', content)


    #填空题没有答案 例如 <   >
    fillSearchObj = re.search('\n(\d+[、\.]).*?<\s+>', content)
    if fillSearchObj:
        #填空题没有答案 例如 <   >
        content = re.sub('\n(\d+[、\.].*?)<\s+>(.*)', r'\n\1______\2【填空答案】', content)
        #填空题里面不包含答案 重复5次
        content = re.sub('\n(\d+[、\.].*?)<\s+>(.*)', r'\n\1______\2【填空答案】', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+>(.*)', r'\n\1______\2【填空答案】', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+>(.*)', r'\n\1______\2【填空答案】', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+>(.*)', r'\n\1______\2【填空答案】', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+>(.*)', r'\n\1______\2【填空答案】', content)

        handleFillInAnswer()

    #填空题里面包含答案 例如 < 填空题答案 > 。
    fillSearchObj = re.search('\n\s*>*<*(\d+[、\.]).*?<\s+(\S+)\s+>', content)
    if fillSearchObj:

        #填空题里面包含答案 例如 < 填空题答案 > 。
        content = re.sub('\n\s*>*<*(\d+[、\.].*?)<\s+(\S+)\s+>(.*)', r'\n\1______\3【填空答案】\2', content)

        #填空题里面包含答案 重复5次
        content = re.sub('\n(\d+[、\.].*?)<\s+(\S+)\s+>(.*)', r'\n\1______\3&&【填空答案】\2', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+(\S+)\s+>(.*)', r'\n\1______\3&&【填空答案】\2', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+(\S+)\s+>(.*)', r'\n\1______\3&&【填空答案】\2', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+(\S+)\s+>(.*)', r'\n\1______\3&&【填空答案】\2', content)
        content = re.sub('\n(\d+[、\.].*?)<\s+(\S+)\s+>(.*)', r'\n\1______\3&&【填空答案】\2', content)


    

    content = re.sub('&&', r'\n', content)

def handleTxtQuestion():
    global content
    #处理选择题
    searchObj = re.search('\n(\d+[、\.]).*[\(（]\s*_*(\s*)\s*_*[\)）](.*?)【正确答案】\nA[、.]',  content)
    if searchObj:
        printError("选择题中没有答案，需要填入答案【{}】".format(searchObj.group()))
        handleSelectQuestion()
    else:
        printError("选项中已经包含答案了或者没有选择题")

    #处理判断题
    searchObj = re.search('\n(\d+[、\.]).*[\(（]\s*_*(\s*)\s*_*[\)）](.*?)【正确答案】\n(\d+[.、])',  content)
    if searchObj:
        printError("判断题中没有答案，需要填入答案【{}】".format(searchObj.group()))
        handleTrueFalseQuestion()
    else:
        printError("判断题中已经包含答案了或者没有判断题")

    #处理填空题
    searchObj = re.search('\n(\d+[、\.]).*?<\s+(\s+|\S+)\s+>', content)
    if searchObj:
        printError("处理填空题【{}】".format(searchObj.group()))
        handleFillBlackQuestion()

def getError():
    return "试卷正则处理信息\n---------------------试卷正则处理信息-----------------------\n" + error + "---------------------试卷正则处理信息-----------------------\n"
