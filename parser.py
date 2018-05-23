#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Example of recursive descent parser written by hand using plex module as scanner
NOTE: This progam is a language recognizer only.

Stmt_list -> Stmt Stmt_list | ε.
Stmt -> id = Expr | print Expr.
Expr -> ( Expr LogOp Expr ) | BooleanVal.
LogOp -> and | or | not.
BooleanVal -> true | TRUE | t | T | 1 | false | FALSE | f | F | 0 .

FIRST sets
----------
Stmt_list:  ε, id, print
Stmt:    	id, print
Expr:     	(, true, TRUE, t, T, 1, false, FALSE, f, F, 0	
LogOp: 		and, or, not
BooleanVal:	true, TRUE, t, T, 1, false, FALSE, f, F, 0

FOLLOW sets
-----------
Stmt_list:  $
Stmt:   	ε, id, print
Expr:     	ε, id, print, ), and, or, not
LogOp: 		(, true, TRUE, t, T, 1, false, FALSE, f, F, 0
BooleanVal:	ε, id, print, ), and, or, not
  

"""


import plex



class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass



class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		digit = plex.Range("09")
		string = plex.Rep1(letter | digit)
		
		logOp = plex.Str("and", "or", "not")	
		assignOp = plex.Str("=")
		booleanVal = plex.NoCase(plex.Str("true","false","t","f","0","1"))
		
		printCommand = plex.Str("print")
		leftpar = plex.Str("(")	
		rightpar = plex.Str(")")	
		
		space = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(logOp,'LOG_OP_TOKEN'),
			(booleanVal,'BOOLEAN_VAL_TOKEN'),
			(space,plex.IGNORE),
			(assignOp, 'ASSIGN_OP'),
			(printCommand, 'PRINT_COMMAND'),
			(string, 'string'),
			(leftpar, '('),
			(rightpar, ')')
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		# la is the type of token
		# val is the value of the token
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			print("-----")
			print("match exception")
			print(self.la)
			print(self.val)
			print("-----")
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.stmt()
	
			
	def stmt(self):
		""" 
			Stmt -> id = Expr | print Expr. 
			FIRST sets:
			Stmt:    	id, print
		"""
		
		print("val in stmt: " + self.val)
		if self.la=='string' or self.la=='PRINT_COMMAND':
			self.match('string')
			self.expr()
		elif self.la is None:
			print("You have reached the end of the program.")
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in stmt: string or print command expected")
	
	def expr(self):
		"""
			Expr -> ( Expr LogOp Expr ) | BooleanVal.
			FIRST sets:
			Expr:     	(, true, TRUE, t, T, 1, false, FALSE, f, F, 0	
		"""
		print("val in expr: " + self.val)
		if self.la=='BOOLEAN_VAL_TOKEN':
			self.booleanVal()
		elif self.la=='LOG_OP_TOKEN':
			self.logOp()
		elif self.la=='ASSIGN_OP':
			self.assignOp()
		elif self.la=='PRINT_COMMAND':
			self.printCheck()
		elif self.la=='string':
			self.match('string')
			self.stmt()
		elif self.val=='(':
			self.match('(')
			self.expr()
		elif self.val==')':
			self.match(')')
			self.expr()	
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in expr: Valid expression expected")

	
	def booleanVal(self):
		"""
			BooleanVal -> true | TRUE | t | T | 1 | false | FALSE | f | F | 0 .
			FIRST sets:
			BooleanVal:	true, TRUE, t, T, 1, false, FALSE, f, F, 0
		"""
		print("val in bool: " + self.val)
		if self.la=='BOOLEAN_VAL_TOKEN':
			self.match('BOOLEAN_VAL_TOKEN')
			self.expr()
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in booleanVal: Boolean value expected")

	
	def logOp(self):
		"""
			LogOp -> and | or | not.
			FIRST sets:
			LogOp: 		and, or, not
		"""
		print("val in logOp: " + self.val)
		if self.la=='LOG_OP_TOKEN':
			self.match('LOG_OP_TOKEN')
			self.expr()	
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in logOp: Logical Operator (and, or, not) expected")
			
	def assignOp(self):
	
		print("val in assignOp: " + self.val)
		if self.la=='ASSIGN_OP':
			self.match('ASSIGN_OP')
			if self.la=='(' or self.la=='BOOLEAN_VAL_TOKEN' or self.val=='not':
				self.expr()	
			else:
				print(self.la)
				print(self.val)
				raise ParseError("in assignOp: Assignment operator expected")
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in assignOp: Assignment operator expected")
			
			
	def printCheck(self):
	
		print("val in printCheck: " + self.val)
		if self.la=='PRINT_COMMAND':
			self.match('PRINT_COMMAND')
			self.stringCheck()	
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in printCheck: Print Command expected")
			
	def stringCheck(self):
	
		print("val in printCheck: " + self.val)
		if self.la=='string':
			self.match('string')
			self.stmt()	
		else:
			print(self.la)
			print(self.val)
			raise ParseError("in stringCheck: Print Command expected")
		
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("recursive-descent-parsing.txt","r") as fp:

	# parse file
	try:
		parser.parse(fp)
		print("Successful parsing of program")
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
