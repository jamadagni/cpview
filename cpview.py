#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# cpview -- a simple codepoint viewer app
# lists the Unicode codepoints in an input string
#
# Copyright (C) 2014, Shriramana Sharma <samjnaa at gmail.com>
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

# Contributors:
# Andrew Cunningham <acunningham at slv.vic.gov.au>: code for NCR forms and preserve ASCII

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
	if cb.currentText() == s : return
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
		
		self.outputTable = QTableView()
		w = self.outputTextBox = QPlainTextEdit()
		w.setReadOnly(True)
		self.stringSettingsTab = QWidget()
		
		w = self.tabWidget = QTabWidget()
		w.addTab ( self.outputTable, "As a &table" )
		w.addTab ( self.outputTextBox, "As a st&ring" )
		w.addTab ( self.stringSettingsTab, "String &format" )
		
		# contents of string settings tab
		
		w = self.hexCaseComboBox = QComboBox()
		w.addItem("ABCDEF")
		w.addItem("abcdef")
		
		w = self.hexCaseLabel = QLabel("&Hex digits case")
		w.setBuddy(self.hexCaseComboBox)
		
		self.preserveASCIICheckBox = QCheckBox()

		w = self.preserveASCIILabel = QLabel("Preser&ve ASCII")
		w.setBuddy(self.preserveASCIICheckBox)
		
		w = self.presetComboBox = QComboBox()
		w.addItem("Simple")
		w.addItem("Python")
		w.addItem("HexNCR")
		w.addItem("DecNCR")
		w.addItem("Custom")
		
		w = self.presetLabel = QLabel("<b>&Presets</b>")
		w.setBuddy(self.presetComboBox)
		
		w = self.numSystemComboBox = QComboBox()
		w.addItem("Hex")
		w.addItem("Dec")
		
		w = self.numSystemLabel = QLabel("&Number system")
		w.setBuddy(self.numSystemComboBox)
		
		w = self.bmpPrefixComboBox = QComboBox()
		w.addItem("U+")
		w.addItem("\\u")
		w.addItem("&#x")
		w.addItem("&#")
		w.setEditable(True)
		
		w = self.bmpPrefixLabel = QLabel("&BMP Prefix")
		w.setBuddy(self.bmpPrefixComboBox)
		
		w = self.smpPrefixComboBox = QComboBox()
		w.addItem("U+")
		w.addItem("\\U")
		w.addItem("&#x")
		w.addItem("&#")
		w.setEditable(True)
		
		w = self.smpPrefixLabel = QLabel("&SMP Prefix")
		w.setBuddy(self.smpPrefixComboBox)
		
		w = self.suffixComboBox = QComboBox()
		w.addItem("(none)")
		w.addItem(";")
		w.setEditable(True)
		
		w = self.suffixLabel = QLabel("Suffi&x")
		w.setBuddy(self.suffixComboBox)
		
		w = self.delimeterComboBox = QComboBox()
		w.addItem("(space)")
		w.addItem("(none)")
		w.addItem(",")
		w.setEditable(True)
		
		w = self.delimeterLabel = QLabel("&Delimeter")
		w.setBuddy(self.delimeterComboBox)
		
		w = self.smpCodeLengthComboBox = QComboBox()
		w.addItem("6")
		w.addItem("8")
		
		w = self.smpCodeLengthLabel = QLabel("SMP Hex &Length")
		w.setBuddy(self.smpCodeLengthComboBox)
		
		l = self.stringSettingsGrid = QGridLayout()
		l.setColumnMinimumWidth ( 2, 20 ) # empty separator
		grid = ( ( self.hexCaseLabel  , self.hexCaseComboBox  , None, self.preserveASCIILabel, self.preserveASCIICheckBox ),
		         ( self.presetLabel   , self.presetComboBox   , None, None                   , None                       ),
		         ( self.numSystemLabel, self.numSystemComboBox, None, self.bmpPrefixLabel    , self.bmpPrefixComboBox     ),
		         ( self.delimeterLabel, self.delimeterComboBox, None, self.smpPrefixLabel    , self.smpPrefixComboBox     ),
		         ( self.suffixLabel   , self.suffixComboBox   , None, self.smpCodeLengthLabel, self.smpCodeLengthComboBox ) )
		for r in range(5):
			for c in range(5):
				if grid[r][c] is not None: l.addWidget ( grid[r][c], r, c )
		self.stringSettingsTab.setLayout(l)
		
		l = self.mainLayout = QVBoxLayout()
		l.addWidget(self.inputLabel)
		l.addWidget(self.inputTextBox)
		l.addWidget(self.analyseButton)
		l.addWidget(self.tabWidget)
		self.setLayout(l)
		
		self.analyseButton.clicked.connect(self.analyseText)
		self.presetComboBox.currentIndexChanged[str].connect(self.presetChanged)
		
		for cbn in "bmpPrefix", "smpPrefix", "smpCodeLength", "suffix", "delimeter" :
			self.__dict__[cbn + "ComboBox"].currentIndexChanged[int].connect(
				lambda : setComboItem(self.presetComboBox,"Custom"))
			# above, we use [int] with currentIndexChanged only for minor optimization of avoiding two signals esp with str signature
		self.preserveASCIICheckBox.toggled.connect (
			lambda checked : setComboItem(self.delimeterComboBox,"(none)") if checked else None )
		self.delimeterComboBox.currentIndexChanged[str].connect (
			lambda delimeter : None if delimeter in ("","(none)") else self.preserveASCIICheckBox.setChecked(False) )
		
	def analyseText(self) :
		
		capitalizeHex = self.hexCaseComboBox.currentText() == "ABCDEF"
		preserveASCII = self.preserveASCIICheckBox.isChecked()
		numSystemDecimal = self.numSystemComboBox.currentText() == "Dec"
		bmpPrefix = self.bmpPrefixComboBox.currentText()
		smpPrefix = self.smpPrefixComboBox.currentText()
		smpCodeLength = int(self.smpCodeLengthComboBox.currentText())
		
		suffix = self.suffixComboBox.currentText()
		if suffix == "(none)" : suffix = ""

		delimeter = self.delimeterComboBox.currentText()
		if delimeter == "(none)" : delimeter = ""
		elif delimeter == "(space)" : delimeter = " "
		
		text = fixSurrogatePresence(self.inputTextBox.toPlainText())
		out = ""
		for char in text :
			if preserveASCII and 0x0019 < ord(char) < 0x007f :
				out += char
			else :
				if not preserveASCII and out != "" : out += delimeter
				out += smpPrefix if ord(char) > 0xffff else bmpPrefix
				if numSystemDecimal :
					c = str(ord(char))
				else :
					c = code(char,smpCodeLength)
					if capitalizeHex : c = c.upper()
				out += c
				out += suffix
		self.outputTextBox.setPlainText(out)
		
		tableModel = QStandardItemModel ( len(text), 2 )
		tableModel.setHeaderData ( 0, Qt.Horizontal, "Codepoint" )
		tableModel.setHeaderData ( 1, Qt.Horizontal, "Character name" )
		for i in range(len(text)) :
			tableModel.setItem ( i, 0, QStandardItem ( "U+" + code(text[i]).upper() ) )
			tableModel.setItem ( i, 1, QStandardItem ( unicodedata.name ( text[i], "UNKNOWN" ) ) )
		self.outputTable.setModel(tableModel)
		self.outputTable.horizontalHeader().setStretchLastSection(True)
	
	presetTargets =         ( "numSystem", "bmpPrefix", "smpPrefix", "smpCodeLength", "suffix", "delimeter" )
	presetMap = { "Simple": (       "Hex",        "U+",        "U+",             "6", "(none)",   "(space)" ),
	              "Python": (       "Hex",       "\\u",       "\\U",             "8", "(none)",    "(none)" ),
	              "HexNCR": (       "Hex",       "&#x",       "&#x",             "6",      ";",    "(none)" ),
	              "DecNCR": (       "Dec",        "&#",        "&#",             "6",      ";",    "(none)" ) }
	
	def presetChanged ( self, newPresetName ) :
		if newPresetName == "Custom" : return
		currPreset = MainWindow.presetMap[newPresetName]
		for i in range(len(currPreset)) :
			setComboItem ( self.__dict__ [ MainWindow.presetTargets[i] + "ComboBox" ], currPreset[i] )
		setComboItem ( self.presetComboBox, newPresetName ) # needed since above actions may reset this to Custom
	
app = QApplication([])
mainWindow = MainWindow()
mainWindow.show()
app.exec_()

# Sample text for testing :
# राम ராம രാമ ರಾಮ రామ rāma 𑀭𑀸𑀫
