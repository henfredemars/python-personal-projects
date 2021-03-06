python-personal-projects
========================

A collection of small applications written for exploration or personal need

I have written much more, but most of my work is restricted by licensing restrictions and cannot
	be posted here (and is not written in Python)

See my work on frank-recruiter-system-dev for work in deployment

Later, I will need to move the unit tests and add more documentation if others actually find this useful

Contents by Folder:

PyTxtFormat: A GUI application that I use regularly to message close friends and relatives overseas
	while keeping the number of text messages (and thus cost) down for the longer letters that
	I desire to write. It reforms text to consume less space while remaining human-readable according
	to translations (substitutions) that you provide while eliminating wasteful spaces

PyHash: Simple utility script to check a directory for changes

ChatBot: A terminal application that provides a simple implementation of a learning chat bot. It is far
	from perfect, but provided an occasional evening of amusement

"ChatterBox" (so-called): A GUI chat client and server sample

DeathSwitch: Toy dead-man's switch once used to send out emails if user hasn't logged in after a period.

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

LogoutDaemon: Tool to log out session after idle time expires. This program was written for use
	on a system where I could not set the usual timeout environment variable and the
	limit on number of logins was low, resulting in the inability to login when
	accessing the server from an unreliable connection

Small8ASM: A simple assembler for the Small8 instruction set architecture. The ISR is easily
	determined by examining the script, but it is intended to minimize the number of components

SubsetCopy: Interactive CLI script that performs a useful but often lacking filesystem operation:
	subset copy--meaning--copy a subset of files in a directory tree into a new directory
	tree. Very useful for choosing a subset of files to fit on a portable device with
	much less storage.

PathRename: Simple utility script that I used to correct invalid file names in my music collection

PySudokuSolver: Simple benchmark script that I once used to guage the performance of PyPy

PyMultiplicationScript: A simple script I once used to help my brother practice his multiplication

All GUI applications use tkinter and the Python 3 standard library, and the code is released under the
	permissive MIT license in the hopes it might be useful to someone else
