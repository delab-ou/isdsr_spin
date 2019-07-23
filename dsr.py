from pathlib import Path;
import subprocess;

''' class for promela code generation '''
class PromelaGenerator:
    nodes=4;
    around=1;
    def __init__(self,n,a):
        self.nodes=n;
        self.around=a;

    def genHeader(self):
        return "\
#define AROUND "+str(self.around)+"\n\
#define CHAN_BUF 1\n\
#define NODES "+str(self.nodes)+"\n\
typedef packet{byte type,src,dest,next,hops,ri[NODES],rilen};\n\
chan c[NODES] = [CHAN_BUF] of {packet};\n\
c_decl{\n\
\#include \"replace.h\"\n\
\#include \"print_state.h\"\n\
};\n\
";

    def genBroadcast(self):
        ret= "\
inline broadcast(){\n\
\tatomic{\n\
\t\tfor(cnt: 1 .. AROUND){\n\
\t\t\tif\n";
        for x in range(self.nodes):
            ret+="\t\t\t\t::next="+str(x)+";\n"
        ret+="\
\t\t\t\t::next=255;\n\
\t\t\tfi;\n\
\t\t\tif::((next==255) || ((next+1)==id))->skip;\n\
\t\t\t\t::else -> unicast(next);\n\
\t\t\tfi;\n\
\t\t};\n\
\t\tnext=0;\n\
\t};\n\
}";
        return ret;

    def genNODES(self):
        file=Path('./dsr_node_src');
        ret="";
        with file.open() as f:
            ret=f.read();
        return ret;

    def genInit(self):
        ret="\
init{\n\
\tatomic{\n\
\t\trun Src(1,2);\n\
\t\trun Dest(2);\n"
        for x in range(self.nodes-2):
            ret+="\t\trun Node("+str(x+3)+");\n";
        ret+="\t}\n}";
        return ret;


    def genPromelaCode(self):
        file_pml=Path('./dsr_gen.pml');
        ret=self.genHeader()+"\n"+self.genBroadcast()+"\n"+self.genNODES()+"\n"+self.genInit();
        with file_pml.open('w') as f:
            f.write(ret);

'''class for node replacement code generation '''
class ReplacementCodeGenerator:
    nodes=4;

    def __init__(self,n):
        self.nodes=n;

    def genQfunc(self):
        ret3="";
        ret2="";
        ret1="void (*moveq[])(int *perm, Q0 *_now, Q0 *_tmp)={\n"
        for i in range(3,(self.nodes+1)):
            for j in range(3,(self.nodes+1)):
                ret1+="moveQ"+str(i)+"Q"+str(j);
                ret2+=self.genQreplace(i,j);
                ret3+=self.genQreplaceDefinition(i,j)+";\n";
                if not(i==self.nodes and j==self.nodes):
                    ret1+=",";
        ret1+="};"
        return ret1,ret2,ret3;

    def genQreplaceDefinition(self,now=0,tmp=0):
        return "void moveQ"+str(now)+"Q"+str(tmp)+"(int *perm, Q0 *_now, Q0 *_tmp)";

    def genQreplace(self,now=0,tmp=0):
        ret=self.genQreplaceDefinition(now,tmp);
        if (now==tmp):
            return ret+"{}\n";
        #0:type,1:src,2:dest,3:next,4:hops,5:ri[NODES],5+NODES:rilen
        ret+="\
{\n\
  Q"+str(now)+" *_nowQ=(Q"+str(now)+"*)_now;\n\
  Q"+str(tmp)+" *_tmpQ=(Q"+str(tmp)+"*)_tmp;\n\
  _tmpQ->Qlen=_nowQ->Qlen;\n\
  _tmpQ->contents[0].fld0=_nowQ->contents[0].fld0;\n\
  _tmpQ->contents[0].fld1=_nowQ->contents[0].fld1;\n\
  _tmpQ->contents[0].fld2=_nowQ->contents[0].fld2;\n\
  _tmpQ->contents[0].fld3=_nowQ->contents[0].fld3;\n\
  _tmpQ->contents[0].fld4=_nowQ->contents[0].fld4;\n"
        for i in range(5, (5+self.nodes+1)):
            ret+="\
  _tmpQ->contents[0].fld"+str(i)+"=_nowQ->contents[0].fld"+str(i)+";\n"
        ret+=self.genQreplaceCheckPerm("_tmpQ");
        ret+="}\n";
        return ret;

    def genQreplaceCheckPerm(self,v="_tmp"):
        ret="\
  if((3 <= "+v+"->contents[0].fld3) && ("+v+"->contents[0].fld3 <= NODES)){\n\
    "+v+"->contents[0].fld3=perm["+v+"->contents[0].fld3-3];\n\
  }\n"
        for i in range(5,(5+self.nodes)):
            ret+="\
  if((3 <= "+v+"->contents[0].fld"+str(i)+") && ("+v+"->contents[0].fld"+str(i)+" <= NODES)){\n\
    "+v+"->contents[0].fld"+str(i)+"=perm["+v+"->contents[0].fld"+str(i)+"-3];\n\
  }\n";

        return ret;

    def genSrcDestCheckPerm(self):
        cp=self.genQreplaceCheckPerm("_p");
        ret="void moveSrcQ(int *perm, Q1 *_p){\n";
        ret+=cp;
        ret+="}\n";
        ret+="void moveDestQ(int *perm, Q2 *_p){\n";
        ret+=cp;
        ret+="}\n";
        return ret;

    def genReplaceHeader(self):
        return '\
#ifndef REPLACE_H\n\
#define REPLACE_H\n\
#include "pan.h"\n\
#include "print_state.h"\n\
#ifndef NODES\n\
#define NODES '+str(self.nodes)+'\n\
#endif\n';


    def genReplace(self):

        fileS=Path('./replace_src');
        file_code=Path("./replace.c");
        file_header=Path("./replace.h");

        ret='\
#include <stdio.h>\n\
#include <string.h>\n\
#include "replace.h"\n';
        qp,qf,qd=self.genQfunc();
        ret+=qp+"\n";
        ret+=qf+"\n";
        ret+=self.genSrcDestCheckPerm();
        with fileS.open() as f:
            ret+=f.read();
        with file_code.open('w') as f:
            f.write(ret);
        ret=self.genReplaceHeader();
        ret+=qd+"\n";
        ret+="\
void moveQueue(int *perm, Q0* _now, Q0* _tmp);\n\
void moveDestQ(int *perm, Q2 *q);\n\
void moveSrcQ(int *perm, Q1 *q);\n\
int isSameState(char* s1,char *s2, int size);\n\
void moveCorrespondingNode(int *perm, struct packet *_p);\n\
void movePacket(int*perm, struct packet *_now, struct packet *_tmp);\n\
void movePackets(int *perm, P2 *_now, P2 *_tmp);\n\
void moveSrcPackets(int *perm, P0* _tmp);\n\
void moveDestPackets(int *perm, P1* _tmp);\n\
void moveProcess(int *perm, P2 *_now, P2* _tmp);\n\
void moveState(int *perm, struct State *_now,struct State *_tmp,int id,short *pos,short *qos);\n\
void replace(int *perm, struct State *_now, struct State* _tmp,short *pos,short *qos);\n\
int routeLength(struct State *s,short *pos);\n\
#endif"
        with file_header.open('w') as f:
            f.write(ret);
        return ret;

''' class for printing state variables '''
class PrintState:
    nodes=4;

    def __init__(self,nodes):
        self.nodes=nodes;

    def genPrintQDefinition(self,id):
        return 'void pq'+str(id)+'(Q0* q0,int id)';

    def genPrintQueueCode(self,id):
        ret=self.genPrintQDefinition(id)+'{\n';
        ret+='\
  Q'+str(id)+' *q= (Q'+str(id)+'*) q0;\n';
        ret+='\
  printf("Q%d:Qlen=%d,_t=%d\\n",id,q->Qlen,q->_t);\n\
  printf("(%d,%d,%d,%d,%d,ri[%d'
        for i in range(self.nodes-1):
            ret+=',%d'
        ret+='],%d)\\n",\n\
  q->contents[0].fld0,\n\
  q->contents[0].fld1,\n\
  q->contents[0].fld2,\n\
  q->contents[0].fld3,\n\
  q->contents[0].fld4,\n';
        for i in range(5,self.nodes+5):
            ret+='\
  q->contents[0].fld'+str(i)+',\n'
        ret+='\
  q->contents[0].fld'+str(self.nodes+5)+'\n\
  );\n\
}\n';
        return ret;

    def genPrintPacket(self):
        ret='\
void printPacket(struct packet* pkt){\n\
  printf("type:%d,src:%d,dest:%d,next:%d,hops:%d,ri:[%d';
        for i in range(self.nodes-1):
            ret+=',%d';
        ret+='],%d,\\n",\n\
          pkt->type,pkt->src,pkt->dest,pkt->next,pkt->hops,pkt->ri[0]';
        for i in range(1,self.nodes):
            ret+=',pkt->ri['+str(i)+']';
        ret+=',pkt->rilen);\n\
}';
        return ret;
    def genPrintQueue(self):
        ret1="";
        ret2="";
        ret3="void (*pq[])(Q0 *q,int id)={";
        for i in range(1,self.nodes+1):
            ret1+=self.genPrintQDefinition(i)+';\n';
            ret2+=self.genPrintQueueCode(i);
            ret3+='pq'+str(i);
            if not(i==self.nodes):
                ret3+=',';
        ret3+='};\n';
        return ret1,ret2,ret3;

    def genPrintHeader(self):
        return '\
    #ifndef STATE_PRINT_H\n\
    #define STATE_PRINT_H\n\
    #include "pan.h"\n\
    #include "replace.h"\n';

    def genPrintCode(self):
        fileS=Path('./print_src');
        file_code=Path('./print_state.c');
        file_header=Path('./print_state.h');

        qd,qc,qf=self.genPrintQueue();

        ret='#include <stdio.h>\n\
#include <string.h>\n\
#include "replace.h"\n\
#include "print_state.h"\n';
        ret+=qf;
        ret+=qc;
        ret+=self.genPrintPacket();
        with fileS.open() as f:
            ret+=f.read();
        with file_code.open('w') as f:
            f.write(ret);

        ret=self.genPrintHeader();
        ret+=qd;
        ret+='\
void printQueue(struct State*,short*,int);\n\
void printAllQueue(struct State*,short*);\n\
void printProcessP0(struct P0*);\n\
void printProcessP1(struct P1*);\n\
void printProcessP2(struct P2*);\n\
void printProcesses(struct State*, short*);\n\
void printState(struct State* ,short*, short*);\n\
void printDifferences(char*,char*,int);\n';
        ret+='#endif\n';
        with file_header.open('w') as f:
            f.write(ret);

''' class for inserting statements into pan.c '''
class InsertingStatementGenerator:
    nodes=4;
    def __init__(self,nodes):
        self.nodes=nodes;
    def avoidTheSame(self,a,i):
        ret="";
        if (i>=2):
            ret+="("+a[0]+"!="+a[i-1]+")"
            for l in range(1,i-1):
                ret+="&&("+a[l]+"!="+a[i-1]+")";
        return ret;

    def constraint(self,a,v,i):
        c=self.avoidTheSame(a,i);
        return "("+a[i]+"<="+str(v)+")"+("&&" if c!="" else "")+c;

    def avoidTheSameNode(self,a):
        ret="("+a[0]+"!=3)";
        for l in range(4,self.nodes+1):
            ret+="||("+a[l-3]+"!="+str(l)+")"
        return "("+ret+")";

    def createReplaceCode(self):
        loops=["l"+str(i+1) for i in range(2,self.nodes)];

        ret='\
    struct State tmp_state;\n\
    static int rl=0;\n\
    int rltmp=routeLength(&now,proc_offset);\n\
    if(rl<rltmp){\n\
        rl=rltmp;\n\
        printf("rl=%d\\n",rl);\n\
    }\n\
    if(rl=='+str(self.nodes-1)+'){\n\
    memcpy(&tmp_state,&now,now._vsz);\n\
    int found=0;\n\
    ';
        ret+="int "+loops[0]+"=0";
        for i in range(1,self.nodes-2):
            ret+=","+loops[i]+"=0"
        ret+=";\n";
        ret+="int permutation["+str(self.nodes-2)+"];\n";

        for i in range(nodes-2):
            it1="for ("+loops[i]+" = 3;";
            it2="&&(found==0);"+loops[i]+"++){\n";
            ret+=it1+self.constraint(loops,self.nodes,i)+it2;
            ret+="permutation["+str(i)+"]="+loops[i]+";\n"
        ret+="if("+self.avoidTheSame(loops,self.nodes-2)+"&&"+self.avoidTheSameNode(loops)+"){\n"
        ret+="replace(permutation,&now,&tmp_state,proc_offset,q_offset);\n";
        ret+="int tmp_n=compress(((char*)&tmp_state),tmp_state._vsz);\n";
        ret+="s_hash((uchar *)v,tmp_n);\n";
        ret+="tmp=H_tab[j1_spin];\n";
        ret+="if(tmp){\n";
        ret+="int tmp_m=memcmp(((char *)&(tmp->state)) ,v,tmp_n);\n";
        ret+="if(!tmp_m){\n";
        ret+="vin=(char*)&tmp_state;\n";
        ret+="found=1;\n"
        ret+="}\n"
        ret+="}\n"
        ret+="}\n"
        ret+="}\n";
        for i in range(self.nodes-2):
            ret+="}\n";
        return ret;

    def genInsertingCode(self):
        filePAN=Path('./pan.c');
        filePAN2=Path('./pan_symm.c');
        hstore=0;
        compress=0;
        with filePAN2.open('w') as of:
            with filePAN.open() as f:
                line=f.readline();
                while line:
                    if "h_store(char *vin, int nin)" in line:
                        hstore=1;
                    if "n = compress(vin, nin);" in line and hstore==1:
                        compress+=1;
                        of.write(self.createReplaceCode());
                    of.write(line);
                    line=f.readline();

''' class for executing all processes '''
class CodeGeneration:
    nodes=4;
    around=1;
    def __init__(self,nodes,around):
        self.nodes=nodes;
        self.around=around;
    def genPromelaCsource(self):
        pg=PromelaGenerator(self.nodes,self.around);
        rcg=ReplacementCodeGenerator(self.nodes);
        ps=PrintState(self.nodes);
        isg=InsertingStatementGenerator(self.nodes);
        pg.genPromelaCode();
        subprocess.check_output(['spin','-a','dsr_gen.pml'])
        rcg.genReplace();
        isg.genInsertingCode();
        ps.genPrintCode();
        suffix="n"+str(self.nodes)+"a"+str(self.around);
        #subprocess.check_output(['gcc','-DNOREDUCE','-o','po-'+suffix,'pan.c','replace_automated.c','print_automated.c'])
        #subprocess.check_output(['gcc','-DNOREDUCE','-o','pa-'+suffix,'pan_automated.c','replace_automated.c','print_automated.c'])


nodes=10;
around=1;
cg=CodeGeneration(nodes,around);
cg.genPromelaCsource();
