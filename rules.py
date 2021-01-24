#!/usr/bin/env python
# -*- coding:utf-8 -*-

class Rule:
    """
    所有规则的基类
    """
    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block)
        handler.end(self.type)
        return True

class HeadingRule(Rule):
    """
    标题只包含一行，不超过70个字符且不以冒号结尾
    """
    type = 'heading'
    def condition(self, block):
        return not '\n' in block and len(block) <= 70 and not block[-1] == ':'

class TitleRule(HeadingRule):
    """
    题目是文档中的第一个文本块，前提条件是它属于标题
    """
    type = 'title'
    first = True

    def condition(self, block):
        if not self.first: return False
        self.first = False
        return HeadingRule.condition(self, block)

class ListItemRule(Rule):
    """
    列表项是以连字符打头的段落。在设置格式的过程中，将把连字符删除
    """
    type = 'listitem'
    def condition(self, block):
        #print(block,block[0])
        return block[0] == '-'
    def action(self, block, handler):
        handler.start(self.type)
        handler.feed(block[1:].strip())
        handler.end(self.type)
        return True

class ListRule(ListItemRule):
    """
    列表以紧跟在非列表项文本块后面的列表项打头，以相连的最后一个列表项结束
    """
    type = 'list'
    inside = False
    def condition(self, block):
        return True
    def action(self, block, handler):
        if not self.inside and ListItemRule.condition(self, block):
            handler.start(self.type)
            self.inside = True
        elif self.inside and not ListItemRule.condition(self, block):
            handler.end(self.type)
            self.inside = False
        return False

class TableRowsRule(Rule):
    """
    表格项是以连竖线打头并使用竖线将字符分隔成多列的段落。在设置格式的过程中，将把竖线删除
    """
    type = 'tablerows'
    sub_type = 'tableh'
    def condition(self, block):
        return block[0] == '|'
    def action(self, block, handler):
        handler.start(self.type)
        block = block[1:].strip()
        for column in block.split('|'):
            handler.start(self.sub_type)
            handler.feed(column)
            handler.end(self.sub_type)
        self.sub_type = 'tabled'
        handler.end(self.type)
        return True

class TableRule(TableRowsRule):
    """
    表格以紧跟在非表格项文本块后面的表格项打头，以相连的最后一个表格项结束
    """
    type = 'table'
    inside = False
    def condition(self, block):
        return True
    def action(self, block, handler):
        if not self.inside and TableRowsRule.condition(self, block):
            handler.start(self.type)
            self.inside = True
        elif self.inside and not TableRowsRule.condition(self, block):
            handler.end(self.type)
            self.inside = False
        return False

class ParagraphRule(Rule):
    """
    段落是不符合其他规则的文本块
    """
    type = 'paragraph'
    def condition(self, block):
        return True

