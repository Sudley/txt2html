#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: Sudley
# ctime: 2020/05/12

import sys, re
from handlers import *
from util import *
from rules import *

class Parser:
    """
    Parser读取文本文件，应用规则并控制处理程序
    """
    def __init__(self, handler):
        self.handler = handler
        self.rules = []
        self.filters = []
    def addRule(self, rule):
        self.rules.append(rule)
    def addFilter(self, pattern, name):
        def filter(block, handler):
            return re.sub(pattern, handler.sub(name), block)
        self.filters.append(filter)

    def parse(self, file):
        self.handler.start('document')
        for block in blocks(file):
            for filter in self.filters:
                block = filter(block, self.handler)    
            for rule in self.rules:
                if rule.condition(block):
                    last = rule.action(block, self.handler)
                    if last: break
        self.handler.end('document')

class BasicTextParser(Parser):
    """
    在构造函数中添加规则和过滤器的Parser子类
    """
    def __init__(self, handler):
        Parser.__init__(self, handler)
        self.addRule(ListRule())
        self.addRule(ListItemRule())
        self.addRule(TitleRule())
        self.addRule(TableRule())
        self.addRule(TableRowsRule())
        self.addRule(HeadingRule())
        self.addRule(ParagraphRule())

        self.addFilter(r'\<(.+?)\>', 'curly_braces')
        self.addFilter(r'\*(.+?)\*', 'emphasis')
        self.addFilter(r'(http(s){0,1}://[\.a-zA-z0-9/]+)', 'url')
        self.addFilter(r'([\.a-zA-z0-9]+@[\.a-zA-z0-9]+[a-zA-z]+)', 'mail')

if __name__ == '__main__':
    handler = HTMLRenderer()
    parser = BasicTextParser(handler)
    parser.parse(sys.stdin)
