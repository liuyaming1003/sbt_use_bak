import io,sys,os,re,csv

#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

#读取word txt 试卷，只能处理选择题文件

fileencoding = "utf-8"
error = ''
questionArray = [] #一道题目数组
mtestmArray = []  #试卷数组

materialCount = 1 # 方便支持多个材料
questionNo = 1 #题号
mtestmTitle = ''
mtestmDesc = ''
mtestmTime = ''
materialArray = [] #材料数组
materialMultiLineArray = [] #处理材料开始和材料结束间的内容

def init(file, encoding='utf-8'):
    global fileencoding,error
    global questionNo,mtestmArray,materialCount,questionArray,materialArray,mtestmTitle,mtestmDesc,mtestmTime,materialMultiLineArray
    if len(encoding) > 0:
        fileencoding = encoding

    error = ''

    if not os.path.splitext(file)[1] == '.txt' :
        printError("只支持txt文件操作")
        return

    questionArray = [] #一道题目数组
    mtestmArray = []  #试卷数组

    materialCount = 1 # 方便支持多个材料
    questionNo = 1 #题号
    mtestmTitle = ''
    mtestmDesc = ''
    mtestmTime = ''
    materialArray = [] #材料数组
    materialMultiLineArray = [] #处理材料开始和材料结束间的内容
    #读取word txt 试卷，只能处理选择题文件
    f = open(file, "r", encoding=fileencoding)
    lines = f.readlines()
    f.close()

    handleLines(lines)

    #获取文件名称
    #array = os.path.split(file)
    #filename = array[1].split(".")[0]


    #dir = os.path.join(array[0], filename)

    #filename = os.path.join(dir, filename + ".csv")

    filename = os.path.splitext(file)[0] + ".csv"

    #写入csv文件
    writeCsv(filename)
    printError("csv文件已经生成，请根据错误修改csv文件")
    #print("mtestmArray", mtestmArray)

    #filename = os.path.splitext(file)[0] + "_not_match.csv"
    #filename = os.path.splitext(file)[0] + "_not_match.txt"
    #writeNotMatchTxt(filename)

def printError(string):
    global error
    error = error + string + '\n'

#def writeNotMatchTxt(filename):
#    global notMatchTxt

    #写文件
#    w_file = open(filename, "w", encoding=fileencoding)
#    w_file.write(notMatchTxt)
#    w_file.close()

def handleLines(lines):
    global questionArray,materialArray,mtestmTitle,mtestmDesc,mtestmTime,materialMultiLineArray
    materialIsStart = False
    for line in lines:
        #print("line",line)
        #获取标题
        obj = re.search('【标题】(.*)', line)
        if obj:
            mtestmTitle = obj.group(1)
            continue

        #获取描述
        obj = re.search('【描述】(.*)', line)
        if obj:
            mtestmDesc = obj.group(1)
            continue
        #获取用时
        obj = re.search('【用时】(.*)', line)
        if obj:
            mtestmTime = obj.group(1)
            continue

        #多行材料处理 需要 【M材料开始】。。。【M材料结束】
        obj = re.search('【材料开始】(.*)', line)
        if obj:
            materialIsStart = True
            materialMultiLineArray.append(obj.group(1))
            continue

        obj = re.search('【材料结束】', line)
        if obj:
            materialIsStart = False
            materialArray.append(materialMultiLineArray)
            materialMultiLineArray = []
            continue

        if materialIsStart:
            materialMultiLineArray.append(line)
            continue

        #处理材料
        obj = re.search('【材料】(.*)\n*', line)
        #print(obj)
        if obj:
            materialArray.append(obj.group(1))
            continue
        #判断是否是段落
        obj = re.search('^\s*([一二三四五六七八九十]{1,4}[、.].*)', line)
        #print(obj)
        if  obj:
            #如果材料未处理需要处理材料
            if len(materialArray) > 0:
                handleMaterial(materialArray)
                #print(isinstance(materialArray[1], list))
                materialArray = []
            #如果选择题、判断题还未处理需要优先处理
            if len(questionArray) > 0 :
                handleQuestion(questionArray)
                questionArray = []
            #是段落
            question = initQuestion(1, '')
            question["section"] = obj.group(1)
            mtestmArray.append(question)
            continue

        

        #读取内容，以数字开始读到下一个数字开始
        obj = re.match('^\d+[、\.]', line)
        if obj :
            #如果选择题、判断题还未处理需要优先处理
            if len(questionArray) > 0 :
                handleQuestion(questionArray)
                questionArray = []

            #如果材料未处理需要处理材料
            if len(materialArray) > 0:
                handleMaterial(materialArray)
                materialArray = []
        questionArray.append(line)
        #print(obj)
  
    #处理最后一题
    if len(questionArray) > 0:
        handleQuestion(questionArray)    

def initQuestion(type, no):
    #type 类型 0 材料 1 段落 2 选择题 3 判断题 4 填空题 5 简答题
    #

    question = {
        "type": type,           #题目类型
        "section":"",        #段落
        "question":"",       #题干
        "questionType":"",       #题型
        "materials":[],      #材料
        "choices":['', '', '', '', '', ''],         #选择项
        "answer":"",         #答案
        "resolve":"",       #解析
        "no":no,              #题号
    }
    return question

#处理材料
def handleMaterial(array):
    global materialCount
    question = initQuestion(0, '')
    for obj in array:
        #如果内容是数组的话需要转换成字符串
        if isinstance(obj, list):
            str = ''
            for item in obj:
                str = str + item

            question["materials"].append(str)
        else:
            question["materials"].append(obj)

    if len(array) > materialCount :
        materialCount = len(array)

    mtestmArray.append(question)

    #print("array", len(array), array)

#统一处理解析
def handleResolve(str, question):
    #处理解析
    obj = re.findall('【解析】(\S+)', str)
    i = 0
    for resolve in obj:
        #print(resolve)
        if i == 0 :
            question['resolve'] = resolve
        else :
            question['resolve'] = question['resolve'] + '\n' + resolve
        i = i + 1

#处理填空题 简答题 选择题 判断题
def handleQuestion(array):
    global questionNo
    #print('array', array)
    str = ''
    for string in array:
        #处理选择题选项里面的空格问题        
        obj = re.match(r'^[A-F][、.]', string)
        if obj : 
            obj = re.search(r'\s+[A-F][、.]', string)
            if obj: 
                string = re.sub(r'(\s+[A-F][、.])', r'$\1', string)
            string += '$'
        
        str = str + ' ' +string
    str = re.sub('\n', r'', str)
    #print('str', str)

    #处理填空题
    obj = re.search('^\s*\d+[、.](.*?)【填空答案】', str)
    if obj:
        #填空题 
        question = initQuestion(4, questionNo)
        question['question'] = obj.group(1)
        #question['answer'] = obj.group(2)   
        obj = re.findall('【填空答案】\s*(\S+)\s*', str)
        
        if len(obj) > 0:
            answer = ''
            i = 0
            for item in obj:
                if i == 0:
                    answer = item
                else:
                    answer = answer + '\n' + item
                i = i + 1
            question['answer'] = answer
            handleResolve(str, question)
            mtestmArray.append(question)
            questionNo = questionNo + 1
        else:
           printError(str + '【填空题没有答案】')

        return
    #处理简答题
    obj = re.match('^\s*\d+[、.](.*)\s*【简答题】', str)
    if obj:
        question = initQuestion(5, questionNo)
        question['question'] = obj.group(1)

        #处理解析
        handleResolve(str, question)
        mtestmArray.append(question)
        questionNo = questionNo + 1
        return
    #选择题 选择题比较麻烦，1答案在题干后面 2 答案在最后面
    obj = re.match('^\s*\d+[、.](.*?)【正确答案】([A-F]{1,6})', str)
    if obj:
        #选择题 
        question = initQuestion(2, questionNo)
        question['question'] = obj.group(1)
        question['answer'] = obj.group(2)

        questionDesc = obj.group(1)
        obj = re.match('(.*)A[、.]', questionDesc)
        if obj:
            question['question'] = obj.group(1)
        #处理选项
        obj = re.findall('\s+[A-F][、.]\s*(.+?)\$', str)
        if len(obj) < 2:
            printError(str + '【选择项少于2个】')
        i = 0
        for choice in obj:
            print('choice', i, choice)
            question['choices'][i] = choice
            i = i + 1
        #处理解析
        handleResolve(str, question)
        mtestmArray.append(question)
        questionNo = questionNo + 1
        return

    #处理换行符号
    str = re.sub('\u2028', r'\n', str)
    #处理判断题 
    obj = re.findall('\d+[、.](.*?)【正确答案】([错对])', str)
    if len(obj) > 0:
        for item in obj:
            #判断题 
            question = initQuestion(3, questionNo)
            question['question'] = item[0]
            question['answer'] = item[1]
            #处理解析
            handleResolve(str, question)
            mtestmArray.append(question)
            questionNo = questionNo + 1
        return
    

    printError("【未能处理的文本】" + str + '\n')

#将数据写入xls文件

def writeCsv(filename):
    global mtestmArray,fileencoding,materialArray
    csvfile = open(filename, 'w', encoding=fileencoding)
    writer = csv.writer(csvfile, dialect='excel')

    writer.writerow(['标题', mtestmTitle])
    writer.writerow(['描述', mtestmDesc])
    writer.writerow(['用时', mtestmTime])

    materialArray = []
    materialNoneArray = []
    for i in range(materialCount):
        materialArray.append('材料')
        materialNoneArray.append('')

    writer.writerow(['段落'] + materialArray + ['题型', '题号', '题干','选择项1', '选择项2', '选择项3', '选择项4', '选择项5', '选择项6', '答案', '解析'])

    for questionObj in mtestmArray:
        type = questionObj['type']
        section =  questionObj['section']
        no = questionObj['no']
        question = questionObj['question'] 
        materials = materialNoneArray 
        choices = questionObj['choices']
        answer = questionObj['answer'].strip()
        resolve = questionObj['resolve']
        
        #题干里面包含有多个题干，需要处理
        questions = question.split('【题干】')
        question = questions[0]
        if type == 0 :
            materials = questionObj['materials']
            writer.writerow([section] + materials + ['', no, question] + questionObj['choices'] + [answer, resolve])
        elif type == 1 :
            #段落
            writer.writerow([section] + materials + ['', no, question] + questionObj['choices'] + [answer, resolve])
        elif type == 2 :
            #选择题
            writer.writerow([section] + materials + ['', no, question] + questionObj['choices'] + [answer, resolve])
        elif type == 3 :
            #判断题
            writer.writerow([section] + materials + ['', no, question] + questionObj['choices'] + [answer, resolve])
        elif type == 4 :
            #填空题
            writer.writerow([section] + materials + ['', no, question] + questionObj['choices'] + [answer, resolve])
        elif type == 5 :
            #简答题
            writer.writerow([section] + materials + ['简答', no, question] + questionObj['choices'] + [answer, resolve])

        if len(questions) > 1 :
            #需要再次写入题干
            for question in questions[1:] :
                writer.writerow([''] + materials + ['', no, question.strip(),'', '', '', '', '', '', '', ''])

    csvfile.close()

def getError():
    global questionNo
    return "试卷转成csv信息\n---------------------试卷转成csv信息 题目数量：%d" % (questionNo - 1) +"-----------------------\n" + error + "---------------------试卷转成csv信息-----------------------\n"



    