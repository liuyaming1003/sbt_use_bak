import io,sys,os,re,csv

sys.path.append(os.path.join(os.path.dirname(__file__), "xlwt-1.3.0"))
import xlwt

fileencoding = "utf-8"
error = ''
def init(file, encoding='utf-8'):
    global fileencoding
    if len(encoding) > 0:
        fileencoding = encoding

    error = ''
    if not os.path.splitext(file)[1] == '.csv' :
        printError("只支持csv文件操作")
        return

    #生成文件名称
    filename = os.path.splitext(file)[0] + ".xls"

    csvToXls(file, filename)
    printError("将csv文件转换成xls文件")

def printError(string):
    global error
    error = error + string + '\n'

def csvToXls(csvFilePath, xlsFilePath):
    global fileencoding
    #打开csv文件
    csvFile = open(csvFilePath, "r", encoding=fileencoding)

    reader = csv.reader(csvFile)


    #新建excel文件
    mtestmexcel = xlwt.Workbook()
    #新建sheet页
    mysheet = mtestmexcel.add_sheet("磨题帮试卷")

    l = 0
    #通过循环获取单行信息
    for line in reader:
        r = 0
        #通过双重循环获取单个单元信息
        for i in line:
            #通过双重循环写入excel表格
            mysheet.write(l,r,i)
            r=r+1
        l=l+1
    #最后保存到excel
    mtestmexcel.save(xlsFilePath)

def getError():
    return "试卷转成xls信息\n---------------------试卷转成xls信息-----------------------\n" + error + "---------------------试卷转成xls信息-----------------------\n"



