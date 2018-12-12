import sublime, sublime_plugin

import imp,os,re


MTestMRex = None
MTestMCsv = None
MTestMXls = None

#word txt 格式正则处理
#支持答案在其他地方【答案开始】...【答案结束】

#将格式化的txt转换成csv文件
#支持 【标题】【描述】【用时】【材料开始】...【材料结束】【材料】【正确答案】【填空答案】【简答题】【解析】

#将 txt 用正则替换成标准格式
class MTxtRexCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global MTestMRex
        currentDir = os.path.join(sublime.packages_path(), "MTestM")
        pyDir = os.path.join(currentDir, "py")
        if not MTestMRex:
            MTestMRex = imp.load_source("MTestMRex", os.path.join(pyDir, "mtestm-rex.py"))

        #获取文件路径
        filePath = self.view.file_name()
        MTestMRex.init(filePath)

        errorView = self.view.window().new_file()
        errorView.insert(edit, 0, MTestMRex.getError())

#将 标准格式的txt文件转换成csv文件
class MTxtCsvCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global MTestMCsv
        currentDir = os.path.join(sublime.packages_path(), "MTestM")
        pyDir = os.path.join(currentDir, "py")
        if not MTestMCsv:
            MTestMCsv = imp.load_source("MTestMCsv", os.path.join(pyDir, "mtestm-csv.py"))

        #获取文件路径
        filePath = self.view.file_name()
        MTestMCsv.init(filePath)
        print('edit = ', edit.edit_token)
        errorView = self.view.window().new_file()
        errorView.insert(edit, 0, MTestMCsv.getError())

#将 csv文件转换成xls文件
class MCsvXlsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global MTestMXls
        currentDir = os.path.join(sublime.packages_path(), "MTestM")
        pyDir = os.path.join(currentDir, "py")
        if not MTestMXls:
            MTestMXls = imp.load_source("MTestMXls", os.path.join(pyDir, "mtestm-xls.py"))

        #获取文件路径
        filePath = self.view.file_name()
        MTestMXls.init(filePath)

        errorView = self.view.window().new_file()
        errorView.insert(edit, 0, MTestMXls.getError())


#执行一些正则，达到替换文本的作用
class MRunRegCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #开始编辑文件
        view = self.view


        #替换掉这个 
        reg = ['．','Ａ','Ｂ','Ｃ','Ｄ','Ｅ','Ｆ','Ｇ','Ｈ','Ｉ','Ｊ']
        replace = ['.','A','B','C','D','E','F','G','H','I','J']
        for index,value in enumerate(reg) :
            regions = view.find_all(value)
            for region in regions :
                view.replace(edit, region, replace[index]) 
        
        def replace(reg, tmpl):
            #每次替换一次
            while True:
                region = view.find(reg, 0)
                if region.empty():
                    print("找不到", reg,region)
                    break
                str = view.substr(region)
                print("替换前 = ", str)
                str = re.sub(reg, tmpl, str)
                print("替换后 = ", str)
                view.replace(edit, region, str)

        
        #修正题目格式,题号没有[.、．]隔开
        # reg = r'^\s*(\d+)(\.*)'
        # replace(reg, '\1\2') 

        reg = r'(正确答案|答案)[：:]'
        replace(reg, '【正确答案】')        

        #修改选择项格式 (B-F)
        reg = r'^\s*([^\d].*)((?:\n\s.*)*)[\(（]\s*([B-F])\s*[\)）]'
        replace(reg, r'\1\2 \3.')

        #单独处理 A
        reg = r'^\s*[\(（]\s*([A])\s*[\)）]'
        replace(reg, r'\1.')

        #将ABCDF选项左对齐
        reg = r'^\s+([A-F][\.、])'
        replace(reg, r'\1')
        
        #替换选择项格式 A B C D 连在一起
        reg = r'([^\n\s])([B-F][、\.])'
        replace(reg, r'\1 \2')


        #去除选择 [A-E][、\.]后面的空格
        reg = r'([A-F][、\.])\s+'
        replace(reg, r'\1')
        
        #正则字符串 替换选择项
        reg = r'^\s*(\d+)\s*[\.、]*\s*(.*)[\(（]\s*([A-F]{1,})\s*[\)）](.*)\nA'
        replace(reg, r'\1.\2( )\4【正确答案】\3\nA')

        #替换判断题
        reg = r'^\s*(\d+)\s*[\.、]*\s*(.*)[\(（]\s*(?:[×xX]|错误|错)\s*[\)）](.*)'
        replace(reg, r'\1.\2\3【正确答案】错')
        reg = r'^\s*(\d+)\s*[\.、]*\s*(.*)[\(（]\s*(?:[/√V]|正确|对)\s*[\)）](.*)'
        replace(reg, r'\1.\2\3【正确答案】对')


    
