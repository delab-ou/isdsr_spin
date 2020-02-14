# isdsr_spin

Development Environment

MacOS Mojave 10.14.4

SPIN 6.4.9

Python 3.7.3

gcc 4.2.1


Execution for dsr and isdsr
0:
put all files in the same directory
DSR: dsr.py uses *_src files to generate C files.
ISDSR: isdsr.py uses isdsr_*_src files to generate C files.

1:
Run Script
DSR: python3 dsr.py
ISDSR: python3 isdsr.py

2:
5 files are generated by both dsr.py and isdsr.py
pan_symm.c
replace.h,replace.c
print_state.h,print_state.c

dsr.py and isdsr.py also generate dsr_gen.pml and isdsr_gen.pml, respectively.


3:
SPIN also generates 6 files 
pan.b pan.c pan.h pan.m pan.p pan.t


4:
Compile
DSR: gcc -DNOREDUCE pan_symm.c replace.c state_print.c
ISDSR gcc -DNOREDUCE -lgmp -lpbc -lssl -lcrypto pan_sysm.c replace.c state_print.c ibsas.c isdsr_spin.c ibsas_for_isdsr.c

5:
Run
./a.out -E


In dsr.py and isdsr.py, there are 5 classes.

PromelaGenerator: generates a Promela source file dsr_gen.pml

ReplacementCodeGenerator: generates replace.h and replace.c

PrintState: generates pint_state.h and print_state.c

InsertingStatementGenerator: generates pan_symm.c

CodeGeneration: a method genPromelaCsource() is a triger of code generation


A constructor of CodeGeneration takes 2 arguments nodes and around.

Args:

nodes: is the number of nodes in a network

around: is the number of neighbor nodes at most when a node broadcasts a packet.

Parameters when we conduct experiments for ISSRE2019 and APDCM2020 are

nodes=N, around=1.
N is the number of nodes from 4 to 9.
