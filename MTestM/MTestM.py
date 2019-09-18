import sublime, sublime_plugin

import imp,os,re,zipfile


MTestMRex = None
MTestMCsv = None
MTestMXls = None

#word txt 格式正则处理
#支持答案在其他地方【答案开始】...【答案结束】

#将格式化的txt转换成csv文件
#支持 【标题】【描述】【用时】【材料开始】...【材料结束】【材料】【正确答案】【填空答案】【简答题】【解析】

#将 txt 用正则替换成标准格式
class MTxtRegCommand(sublime_plugin.TextCommand):
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

class MZipXlsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #获取文件名称
        file = self.view.file_name()
        
        #zip文件
        zipfilename = os.path.splitext(file)[0] + ".zip"
        zipf = zipfile.ZipFile(zipfilename,'w',zipfile.ZIP_DEFLATED)
        #遍历目录下的文件，然后压缩
        print ("文件目录", os.path.dirname(file))
        dir = os.path.dirname(file)
        for root,dirs,files in os.walk(dir):
            for file in files:
                #判断文件后缀是否为xls或者png
                splitext = os.path.splitext(file)[1]
                if splitext  == '.xls' or splitext == '.png' or splitext == '.jpg':
                    #获取文件路径
                    print(os.path.join(root,file))
                    #写入到zip文件中
                    zipf.write(os.path.join(root,file),file)
        zipf.close()

#执行一些正则，达到替换文本的作用
class MRunRegCommand(sublime_plugin.TextCommand):
    content = ""
    def run(self, edit):
        global content
        #开始编辑文件
        view = self.view

        #获取文本区域 
        viewRegion = sublime.Region(0, view.size())
        content = view.substr(viewRegion)

        #替换掉全角字符
        #替换．为.
        content = re.sub('．', r'.', content)

        #替换ＡＢＣＤ
        content = re.sub('Ａ', r'A', content)
        content = re.sub('Ｂ', r'B', content)
        content = re.sub('Ｃ', r'C', content)
        content = re.sub('Ｄ', r'D', content)
        content = re.sub('Ｅ', r'E', content)
        content = re.sub('Ｆ', r'F', content)

        #替换掉这个 
        """
        reg = ['．','Ａ','Ｂ','Ｃ','Ｄ','Ｅ','Ｆ','Ｇ','Ｈ','Ｉ','Ｊ']
        replace = ['.','A','B','C','D','E','F','G','H','I','J']
        for index,value in enumerate(reg) :
            regions = view.find_all(value)
            for region in regions :
                view.replace(edit, region, replace[index]) 
        """
        def replace(reg, tmpl):
            global content
            content = re.sub(reg, tmpl, content)
            """
            prevRegion = sublime.Region(0,0)
            while True:
                region = view.find(reg, 0)
                if region.begin() == prevRegion.begin() and region.end() == prevRegion.end():
                    print("问题正则 ---------", reg)
                    print("问题字符串 ---------", regview.substr(region))
                    break
                prevRegion = region
                if region.empty():
                    print("找不到", reg,region)
                    break
                str = view.substr(region)
                print("替换前 = ", str)
                str = re.sub(reg, tmpl, str)
                print("替换后 = ", str)
                view.replace(edit, region, str)
                # break
            """
        #修正题目格式,题号没有[.、．]隔开
        # reg = r'^\s*(\d+)(\.*)'
        # replace(reg, '\1\2') 

        #替换前面空格
        reg = r'^\s+'
        replace(reg, '')    

        reg = r'(正确答案|参考答案|答案)[：:]'
        replace(reg, '【正确答案】')

        #答案后面为 （ABCD） 
        reg = r'【正确答案】\s*[\(（]([A-F]{1,})\s*[\)）]'
        replace(reg, r'【正确答案】\1')

        #将题号做对齐
        #reg = r'^\s+(\d+[、\.])'
        #replace(reg, r'\1') 

        #将段落左对齐
        #reg = r'^\s+([一二三四五六七八九十]{1,}、)'
        #replace(reg, r'\1') 

        #修改选择项格式 (B-F)
        reg = r'\n\s*([^\d].*)((?:\n\s*[^\d].*)*)[\(（]\s*([B-F])\s*[\)）]'
        #replace(reg, r'\1\2 \3.')

        #单独处理 A
        reg = r'\n\s*[\(（]\s*([A])\s*[\)）]'
        replace(reg, r'\n\1.')

        #将ABCDF选项左对齐
        #reg = r'^\s+([A-F])'
        #replace(reg, r'\1')
        
        #替换选择项格式 A B C D 连在一起
        reg = r'([^\n\s])([B-F][、\.])'
        replace(reg, r'\1 \2')

        #替换选择项与ABCDEF没有、.分割
        reg = r'\n([A-F])([^\.、])'
        replace(reg, r'\n\1.\2')

        reg = r'\n([A-E].+[B-F])([^\.、])'
        replace(reg, r'\n\1.\2')

        #去除选择 [A-E][、\.]后面的空格
        reg = r'([A-F][、\.])\s+'
        replace(reg, r'\1')
        
        #括号里面有答案为A B C D 或者  A、B、C、D、E、
        reg = r'[\(（]\s*([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]*\s*[\)）]'
        replace(reg, r'(\1\2\3\4\5)')
        reg = r'[\(（]\s*([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]*\s*[\)）]'
        replace(reg, r'(\1\2\3\4)')
        reg = r'[\(（]\s*([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]*\s*[\)）]'
        replace(reg, r'(\1\2\3)')
        reg = r'[\(（]\s*([A-F])[\s、，,]([A-F])[\s、，,]*\s*[\)）]'
        replace(reg, r'(\1\2)')

        reg = r'正确答案[：:]\s*'
        replace(reg, r'【正确答案】')

        #正确答案里面的多选
        reg = r'【正确答案】\s*([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]([A-F])'
        replace(reg, r'【正确答案】\1\2\3\4\5')
        reg = r'【正确答案】\s*([A-F])[\s、，,]([A-F])[\s、，,]([A-F])[\s、，,]([A-F])'
        replace(reg, r'【正确答案】\1\2\3\4')
        reg = r'【正确答案】\s*([A-F])[\s、，,]([A-F])[\s、，,]([A-F])'
        replace(reg, r'【正确答案】\1\2\3')
        reg = r'【正确答案】\s*([A-F])[\s、，,]([A-F])'
        replace(reg, r'【正确答案】\1\2')

        #正则字符串 替换选择项
        reg = r'\n\s*(\d+)\s*[\.、]*\s*(.*)[\(（]\s*([A-F]{1,})\s*[\)）](.*)\nA'
        replace(reg, r'\n\1.\2( )\4【正确答案】\3\nA')

        #替换判断题
        reg = r'\n\s*(\d+)\s*[\.、]*\s*(.*)[\(（]\s*(?:[×xX]|错误|错)\s*[\)）](.*)'
        replace(reg, r'\n\1.\2\3【正确答案】错')
        reg = r'\n\s*(\d+)\s*[\.、]*\s*(.*)[\(（]\s*(?:[/√V]|正确|对)\s*[\)）](.*)'
        replace(reg, r'\n\1.\2\3【正确答案】对')

        #清除答案里面的空格
        reg = r'(【正确答案】)\s+'
        replace(reg, r'\1')

        #清理选择项出现的 .. .、问题
        reg = r'([A-F])[\.、]{2,}'
        replace(reg, r'\1.')

        #替换掉文本内容
        view.replace(edit, sublime.Region(0, view.size()), content)

#执行一些正则，达到替换文本的作用
class MHtmlRegCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        #开始编辑文件
        view = self.view    

        viewRegion = sublime.Region(0, view.size())
        content = view.substr(viewRegion)

        #提取html里面的图片 
        content = re.sub(r'<img[^>]+(image\d+.jpg|image\d+.png)[^>]+>', r'【题干】\1', content)

        #替换掉html标签
        content = re.sub(r'<[^>]+>', r'', content)

        #替换掉换行加空行
        content = re.sub(r'·*&nbsp;', r' ', content)

        #替换掉换行符
        content = re.sub(r'\n\s*', r'\n', content)

        #替换掉文本内容
        view.replace(edit, sublime.Region(0, view.size()), content)
