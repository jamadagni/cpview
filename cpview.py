#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# cpview -- a simple codepoint viewer app
# lists the Unicode codepoints in an input string
#
# Copyright (C) 2014, Shriramana Sharma
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re
import unicodedata

def code ( char, smpLen = 6 ) :
	c = hex(ord(char))[2:]
	if len(c) < 4 : c = c.zfill(4)
	elif 4 < len(c) < smpLen : c = c.zfill(smpLen)
	return c

def joinSurrogates(match) :
	SURROGATE_OFFSET = 0x10000 - ( 0xD800 << 10 ) - 0xDC00
	return chr ( ( ord(match.group(1)) << 10 ) + ord(match.group(2)) + SURROGATE_OFFSET )

def fixSurrogatePresence(s) :
	'''Returns the input UTF-16 string with surrogate pairs replaced by the character they represent'''
	# needed for some buggy versions of PyQt4 which do not replace surrogate pairs from Qt by the unified trans-BMP codepoint
	# ideas from:
	# http://www.unicode.org/faq/utf_bom.html#utf16-4
	# http://stackoverflow.com/a/6928284/1503120
	return re.sub ( '([\uD800-\uDBFF])([\uDC00-\uDFFF])', joinSurrogates, s )

def setComboItem(cb,s) :
	for i in range(cb.count()) :
		if cb.itemText(i) == s : cb.setCurrentIndex(i)

class MainWindow(QWidget) :
	
	def __init__(self) :
		
		QWidget.__init__(self)
		
		self.setObjectName("mainWindow")
		self.setWindowTitle("cpview -- simple codepoint viewer")
		
		self.inputTextBox = QPlainTextEdit()
		
		w = self.inputLabel = QLabel("&Input text")
		w.setBuddy(self.inputTextBox)
		
		self.analyseButton = QPushButton("&Analyse")
		
		w = self.tabWidget = QTabWidget()
		self.tableTab = QTableView()
		self.stringTab = QWidget()
		w.addTab ( self.tableTab, "As a &table" )
		w.addTab ( self.stringTab, "As a st&ring" )
		
		# contents of string tab
		
		w = self.outputTextBox = QPlainTextEdit()
		w.setReadOnly(True)
		
		w = self.outputLabel = QLabel("&Codepoints")
		w.setBuddy(self.outputTextBox)
		
		w = self.presetComboBox = QComboBox()
		w.addItem("Simple")
		w.addItem("Python")
		w.addItem("Custom")
		
		w = self.presetLabel = QLabel("<b>&Presets</b>")
		w.setBuddy(self.presetComboBox)
		
		w = self.hexCaseComboBox = QComboBox()
		w.addItem("ABCDEF")
		w.addItem("abcdef")
		
		w = self.hexCaseLabel = QLabel("&Hex digits case")
		w.setBuddy(self.hexCaseComboBox)
		
		w = self.bmpPrefixComboBox = QComboBox()
		w.addItem("U+")
		w.addItem("\\u")
		w.setEditable(True)
		
		w = self.bmpPrefixLabel = QLabel("&BMP Prefix")
		w.setBuddy(self.bmpPrefixComboBox)
		
		w = self.smpPrefixComboBox = QComboBox()
		w.addItem("U+")
		w.addItem("\\U")
		w.setEditable(True)
		
		w = self.smpPrefixLabel = QLabel("&SMP Prefix")
		w.setBuddy(self.smpPrefixComboBox)
		
		w = self.smpCodeLengthComboBox = QComboBox()
		w.addItem("6")
		w.addItem("8")
		
		w = self.smpCodeLengthLabel = QLabel("SMP Hex &Length")
		w.setBuddy(self.smpCodeLengthComboBox)
		
		w = self.delimeterComboBox = QComboBox()
		w.addItem("(space)")
		w.addItem("(none)")
		w.addItem(",")
		w.setEditable(True)
		
		w = self.delimeterLabel = QLabel("&Delimeter")
		w.setBuddy(self.delimeterComboBox)
		
		l = self.presetGrid = QGridLayout()
		l.addWidget ( self.presetLabel, 0, 0 )
		l.addWidget ( self.presetComboBox, 0, 1 )
		l.addWidget ( self.hexCaseLabel, 0, 3 )
		l.addWidget ( self.hexCaseComboBox, 0, 4 )
		l.addWidget ( self.bmpPrefixLabel, 1, 0 )
		l.addWidget ( self.bmpPrefixComboBox, 1, 1 )
		l.addWidget ( self.delimeterLabel, 1, 3 )
		l.addWidget ( self.delimeterComboBox, 1, 4 )
		l.addWidget ( self.smpPrefixLabel, 2, 0 )
		l.addWidget ( self.smpPrefixComboBox, 2, 1 )
		l.addWidget ( self.smpCodeLengthLabel, 2, 3 )
		l.addWidget ( self.smpCodeLengthComboBox, 2, 4 )
		l.setColumnMinimumWidth ( 2, 20 )
		
		w = self.presetGroupBox = QGroupBox("String output config")
		w.setLayout(l)
		
		l = self.stringTabLayout = QVBoxLayout()
		l.addWidget(self.outputLabel)
		l.addWidget(self.outputTextBox)
		l.addWidget(self.presetGroupBox)
		self.stringTab.setLayout(l)
		
		l = self.mainLayout = QVBoxLayout()
		l.addWidget(self.inputLabel)
		l.addWidget(self.inputTextBox)
		l.addWidget(self.analyseButton)
		l.addWidget(self.tabWidget)
		self.setLayout(l)
		
		self.analyseButton.clicked.connect(self.analyseText)
		self.presetComboBox.currentIndexChanged[str].connect(self.presetChanged)
		
		for cbn in "bmpPrefix", "smpPrefix", "smpCodeLength", "delimeter":
			self.__dict__[cbn + "ComboBox"].currentIndexChanged.connect(lambda: setComboItem(self.presetComboBox,"Custom"))
		
	def analyseText(self) :
		
		bmpPrefix = self.bmpPrefixComboBox.currentText()
		smpPrefix = self.smpPrefixComboBox.currentText()
		smpCodeLength = int(self.smpCodeLengthComboBox.currentText())
		capitalHex = self.hexCaseComboBox.currentText() == "ABCDEF"
		
		delimeter = self.delimeterComboBox.currentText()
		if delimeter == "(none)" : delimeter = ""
		elif delimeter == "(space)" : delimeter = " "
		
		text = fixSurrogatePresence(self.inputTextBox.toPlainText())
		out = ""
		for char in text :
			if out != "" : out += delimeter
			out += smpPrefix if ord(char) > 0xffff else bmpPrefix
			c = code(char,smpCodeLength)
			out += c.upper() if capitalHex else c
		self.outputTextBox.setPlainText(out)
		
		tableModel = QStandardItemModel ( len(text), 2 )
		tableModel.setHeaderData ( 0, Qt.Horizontal, "Codepoint" )
		tableModel.setHeaderData ( 1, Qt.Horizontal, "Character name" )
		for i in range(len(text)) :
			tableModel.setItem ( i, 0, QStandardItem ( "U+" + code(text[i]).upper() ) )
			tableModel.setItem ( i, 1, QStandardItem ( unicodedata.name ( text[i], "UNKNOWN" ) ) )
		self.tableTab.setModel(tableModel)
		self.tableTab.horizontalHeader().setStretchLastSection(True)
	
	presetMap = { "Simple": { "bmpPrefix": "U+",
	                          "smpPrefix": "U+",
	                          "delimeter": "(space)",
	                          "smpCodeLength": "6" },
	              "Python": { "bmpPrefix": "\\u",
	                          "smpPrefix": "\\U",
	                          "delimeter": "(none)",
	                          "smpCodeLength": "8" } }
	
	def presetChanged ( self, newPresetName ) :
		if newPresetName == "Custom" : return
		for k,v in MainWindow.presetMap[newPresetName].items() : setComboItem ( self.__dict__ [ k + "ComboBox" ], v )
		setComboItem ( self.presetComboBox, newPresetName ) # needed since above actions may reset this to Custom
	
app = QApplication([])
mainWindow = MainWindow()
mainWindow.show()
app.exec_()

# Sample text for testing: राम ராம രാമ ರಾಮ రామ rāma 𑀭𑀸𑀫
