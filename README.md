python-personal-projects
========================

A collection of small applications written for exploration or personal need

Later, I will need to move the unit tests here and add more documentation if others actually find this useful

Contents by Folder:

PyTxtFormat: A GUI application that I use regularly to message close friends and relatives overseas
	while keeping the number of text messages (and thus cost) down for the longer letters that
	I desire to write. It reforms text to consume less space while remaining human-readable according
	to translations (substitutions) that you provide while eliminating wasteful spaces

ChatBot: A terminal application that provides a simple implementation of a learning chat bot. It is far
	from perfect, but provided an occasional evening of amusement

Get2It: A GUI application for individual project management. I wrote this for the many times when I was
	interrupted while working, repeatedly, eventually forgetting to complete some of the tasks. 
	My solution is to create a stack-based representation of my workflow so that, if I need to
	run off to another part of the code to make changes, I will not forget to return to earlier
	work that remains unfinished. I use this application often when I work

Kitty: A rather ugly compiler and stack-based virtual machine for a simple, procedural dynamic language.
	Here, I learned that having a tool to manage your grammar is far more portable than parsing
	it yourself, and having a well-defined lexer is a worthwhile endeavor

	It should be easy to add a tracing JIT with the PyPy toolchain, and it was originally the end goal
	of this work.

Small8ASM: A simple assembler for the Small8 instruction set architecture. Documentation for the
	supported instructions is provided in the comments

PathRename: Simple utility script that I used to correct invalid file names in my music collection

PySudokuSolver: Simple benchmark script that I once used to guage the performance of PyPy

PyMultiplicationScript: A simple script I once used to help my brother practice his multiplication

All GUI applications use tkinter and the Python 3 standard library, and the code is released under the
	permissive MIT license in the hopes it might be useful to someone else
