#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-07 14:07:33
# @Author  : liuym (liuyaming1003@gmail.com)
# @Link    : ${link}
# @Version : $Id$
# 

import sublime, sublime_plugin

#微信小程序装换成支付宝小程序
import imp,os

WxToAl = None
#转换
class WxToAlCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        global WxToAl
        currentDir = os.path.join(sublime.packages_path(), "WxToAl")
        pyDir = os.path.join(currentDir, "py")
        if not WxToAl:
            WxToAl = imp.load_source("WxToAl", os.path.join(pyDir, "file-convert.py"))

        #获取文件路径
        filePath = self.view.file_name()
        WxToAl.init(filePath)
        

        #errorView = self.view.window().new_file()
        #errorView.insert(edit, 0, WxToAl.getLog())
