# isdsr_spin
Development Environment
MacOS Mojave 10.14.4
SPIN 6.4.9
Python 3.7.3
gcc 4.2.1

Execution
0:
put all files in the same directory
dsr.py uses *_src files to generate C files.

1:
Run Script
python3 dsr.py

2:
6 files are generated by dsr.py
dsr_gen.pml
pan_symm.c
replace.h
replace.c
print_state.h
print_state.c

3:
SPIN also generates 6 files 
pan.b pan.c pan.h pan.m pan.p pan.t

4:
Compile
gcc -DNOREDUCE pan_symm.c replace.c state_print.c

5:
Run
./a.out -E

In dsr.py, there are 5 classes.
PromelaGenerator: generates a Promela source file dsr_gen.pml
ReplacementCodeGenerator: generates replace.h and replace.c
PrintState: generates pint_state.h and print_state.c
InsertingStatementGenerator: generates pan_symm.c
CodeGeneration: a method genPromelaCsource() is a triger of code generation

A constructor of CodeGeneration takes 2 arguments nodes and around.
Args:
nodes: is the number of nodes in a network
around: is the number of neighbor nodes at most when a node broadcasts a packet.

Parameters when we conduct experiments for ISSRE2019 are
nodes=N, around=1.
N is the number of nodes from 4 to 9.
