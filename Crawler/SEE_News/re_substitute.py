# encoding: UTF-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import re

def substitueTest():
	string = '<p>&nbsp; &nbsp; &nbsp;2015年11月19日下午，香港环境保护署高级官员、英国皇家特许化学家、北京大学客座教授雷国强博士（Peter K.K. Louie）在C栋201教室做了两场分别题为&ldquo;Air Pollution, Challenges to Improving Public Health, and Risk Communications&rdquo;，和&ldquo;Controlling Emissions from Marine Vessels in Hong Kong&rdquo;的精彩报告。</p><p style="text-align: center;"><img src="/userfile/2015112001.png" width="550" height="356" alt="" /></p>'

	match = re.search(r'<img[^>]+>', string)
	print match.group()

	str_new = re.sub('/userfile', 'http://see.pkusz.edu.cn/userfile', '<p>&nbsp; &nbsp; &nbsp;2015年11月19日下午，香港环境保护署高级官员、英国皇家特许化学家、北京大学客座教授雷国强博士（Peter K.K. Louie）在C栋201教室做了两场分别题为&ldquo;Air Pollution, Challenges to Improving Public Health, and Risk Communications&rdquo;，和&ldquo;Controlling Emissions from Marine Vessels in Hong Kong&rdquo;的精彩报告。</p><p style="text-align: center;"><img src="/userfile/2015112001.png" width="550" height="356" alt="" /></p>')
	print str_new

if __name__=="__main__":
	substitueTest()