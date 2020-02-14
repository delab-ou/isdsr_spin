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
        ret= "\
#define AROUND "+str(self.around)+"\n\
#define CHAN_BUF 1\n\
#define NODES "+str(self.nodes)+"\n\
#define SIG_LEN 128\n\
typedef packet{\n\
  byte type,src,dest,next,hops,ri[NODES],rilen,\n\
  sig1[SIG_LEN],sig2[SIG_LEN],sig3[SIG_LEN]\n\
};\n\
chan c[NODES] = [CHAN_BUF] of {packet};\n\
c_decl{\n\
\#include \"isdsr_spin.h\"\n\
\#include \"replace.h\"\n\
\#include \"print_state.h\"\n\
nodeinfo nodes[NODES];\n\
char *ids[]={\"0001\"";
        for x in range(2,self.nodes+1):
            ret+=",\""+str(x).zfill(4)+"\"";

        ret+="};\n};\n";
        return ret;

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
        file=Path('./isdsr_node_src');
        ret="";
        with file.open() as f:
            ret=f.read();
        return ret;

    def genInit(self):
        ret="\
init{\n\
  c_code{\n\
    initializeNodeInfo((char**)ids,nodes,\"a.param\",NODES);\n\
  };\n\
\tatomic{\n\
\t\trun Src(1,2);\n\
\t\trun Dest(2);\n"
        for x in range(self.nodes-2):
            ret+="\t\trun Node("+str(x+3)+");\n";
        ret+="\t}\n}";
        return ret;


    def genPromelaCode(self):
        file_pml=Path('./isdsr_gen.pml');
        ret=self.genHeader()+"\n"+self.genBroadcast()+"\n"+self.genNODES()+"\n"+self.genInit();
        with file_pml.open('w') as f:
            f.write(ret);

'''class for node replacement code generation '''
class ReplacementCodeGenerator:
    nodes=4;
    siglen=128;
    def __init__(self,n,l=128):
        self.nodes=n;
        self.siglen=l;
    '''
    def genTranslateQtoPkt(self,siglen):
        ret="\
void translateQtoPkt(Q1 *_p,struct packet *pkt){\n";
        ret+="\
  int cnt=0;\n\
  uchar *c=(uchar*)(&(_p->contents));\n\
  uchar *p=(uchar*)(pkt);\n\
  for(cnt=0;cnt<"+str(6+self.nodes+self.siglen*3)+";cnt++){\n\
    p[cnt]=c[cnt];\n\
  }\n\
}\n";
        return ret;

    def genTtranslatePkttoQ(self,siglen):
        ret="\
void translatePkttoQ(Q1 *_p,struct packet *pkt){\n";
        ret+="\
  int cnt=0;\n\
  uchar *c=(uchar*)(&(_p->contents));\n\
  uchar *p=(uchar*)(pkt);\n\
  for(cnt=0;cnt<"+str((6+self.nodes+self.siglen*3))+";cnt++){\n\
    c[cnt]=p[cnt];\n\
  }\n\
}\n";
        return ret;
    '''
    def genTranslateQtoPkt(self,siglen):
        ret="\
void translateQtoPkt(Q1 *_q,struct packet *pkt){\n";
        ret+="\
  pkt->type=_q->contents[0].fld0;\n\
  pkt->src=_q->contents[0].fld1;\n\
  pkt->dest=_q->contents[0].fld2;\n\
  pkt->next=_q->contents[0].fld3;\n\
  pkt->hops=_q->contents[0].fld4;\n";
        for i in range(0,self.nodes):
            ret+="\
  pkt->ri["+str(i)+"]=_q->contents[0].fld"+str((i+5))+";\n";
        ret+="\
  pkt->rilen=_q->contents[0].fld"+str(5+self.nodes)+";\n";
        ret1="";ret2="";ret3="";
        for i in range(0,self.siglen):
            ret1+="\
  pkt->sig1["+str(i)+"]=_q->contents[0].fld"+str(i+6+self.nodes)+";\n";
            ret2+="\
  pkt->sig2["+str(i)+"]=_q->contents[0].fld"+str(i+6+self.nodes+self.siglen)+";\n";
            ret3+="\
  pkt->sig3["+str(i)+"]=_q->contents[0].fld"+str(i+6+self.nodes+self.siglen*2)+";\n";
        ret+=ret1+ret2+ret3+"}\n";
        return ret;

    def genTtranslatePkttoQ(self,siglen):
        ret="\
void translatePkttoQ(Q1 *_q,struct packet *pkt){\n";
        ret+="\
  _q->contents[0].fld0=pkt->type;\n\
  _q->contents[0].fld1=pkt->src;\n\
  _q->contents[0].fld2=pkt->dest;\n\
  _q->contents[0].fld3=pkt->next;\n\
  _q->contents[0].fld4=pkt->hops;\n";
        for i in range(0,self.nodes):
            ret+="\
  _q->contents[0].fld"+str((i+5))+"=pkt->ri["+str(i)+"];\n";
        ret+="\
  _q->contents[0].fld"+str(5+self.nodes)+"=pkt->rilen;\n";
        ret1="";ret2="";ret3="";
        for i in range(0,self.siglen):
            ret1+="\
  _q->contents[0].fld"+str(i+6+self.nodes)+"=pkt->sig1["+str(i)+"];\n";
            ret2+="\
  _q->contents[0].fld"+str(i+6+self.nodes+self.siglen)+"=pkt->sig2["+str(i)+"];\n";
            ret3+="\
  _q->contents[0].fld"+str(i+6+self.nodes+self.siglen*2)+"=pkt->sig3["+str(i)+"];\n";
        ret+=ret1+ret2+ret3+"}\n";
        return ret;

    def genReplaceHeader(self):
        return '\
#ifndef REPLACE_H\n\
#define REPLACE_H\n\
#include "pan.h"\n\
#include "print_state.h"\n\
#include "ibsas_for_isdsr.h"\n\
#include "isdsr_spin.h"\n\
#ifndef NODES\n\
#define NODES '+str(self.nodes)+'\n\
#endif\n';


    def genReplace(self):

        fileS=Path('./isdsr_replace_src');
        file_code=Path("./replace.c");
        file_header=Path("./replace.h");

        ret='\
#include <stdio.h>\n\
#include <string.h>\n\
#include "replace.h"\n\
int count=0;\n';
        ret+=self.genTranslateQtoPkt(self.siglen);
        ret+=self.genTtranslatePkttoQ(self.siglen);
        with fileS.open() as f:
            ret+=f.read();
        with file_code.open('w') as f:
            f.write(ret);
        ret=self.genReplaceHeader();
        ret+="\
void translateQtoPkt(Q1 *_p,struct packet *pkt);\n\
void translatePkttoQ(Q1 *_p,struct packet *pkt);\n\
void signingReplacementPacket(struct packet *pkt, nodeinfo *nodes);\n\
void moveQueue(int *perm, Q1* _now, Q1* _tmp,nodeinfo *nodes);\n\
void moveDestQ(int *perm, Q2 *q,nodeinfo *nodes);\n\
void moveSrcQ(int *perm, Q1 *q,nodeinfo *nodes);\n\
int isSameState(char* s1,char *s2, int size);\n\
void moveCorrespondingNode(int *perm, struct packet *_p);\n\
void movePacket(int *perm, struct packet *_now, struct packet *_tmp,  nodeinfo *nodes);\n\
void movePackets(int *perm, P2 *_now, P2 *_tmp,  nodeinfo *nodes);\n\
void moveSrcPackets(int *perm, P0* _tmp, nodeinfo *nodes);\n\
void moveDestPackets(int *perm, P1* _tmp, nodeinfo *nodes);\n\
void moveProcess(int *perm, P2 *_now, P2* _tmp,  nodeinfo *nodes);\n\
void moveState(int *perm, struct State *_now,struct State *_tmp,int id,short *pos,short *qos, nodeinfo *nodes);\n\
void replace(int *perm, struct State *_now, struct State* _tmp,short *pos,short *qos, nodeinfo *nodes);\n\
int routeLength(struct State *s,short *pos);\n\
#endif"
        with file_header.open('w') as f:
            f.write(ret);
        return ret;

''' class for printing state variables '''
class PrintState:
    nodes=4;
    siglen=128;
    def __init__(self,nodes,siglen=128):
        self.nodes=nodes;
        self.siglen=siglen;

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
}\n';
        return ret;

    def genPrintPacketWithSig(self):
        ret='\
void printPacketWithSig(struct packet* pkt){\n\
  printf("type:%d,src:%d,dest:%d,next:%d,hops:%d,ri:[%d';
        for i in range(self.nodes-1):
            ret+=',%d';
        ret+='],%d,\\n",\n\
          pkt->type,pkt->src,pkt->dest,pkt->next,pkt->hops,pkt->ri[0]';
        for i in range(1,self.nodes):
            ret+=',pkt->ri['+str(i)+']';
        ret+=',pkt->rilen);\n';
        ret+="\
  if(pkt->sig1[0]==0){\n\
    printf(\"sig1={0}, sig2={0}, sig3={0}\\n\");\n\
    return;\n\
  }\n";
        ret+="\
  uchar *s1=(pkt->sig1);\n\
  uchar *s2=(pkt->sig2);\n\
  uchar *s3=(pkt->sig3);\n";
        ret1='sig1=('
        ret2='sig2=('
        ret3='sig3=('
        for i in range(self.siglen):
            if (i%16)==0 :
                ret1+="\\n\\\n    ";
                ret2+="\\n\\\n    ";
                ret3+="\\n\\\n    ";
            ret1+="%u,";
            ret2+="%u,";
            ret3+="%u,";
        ret1+=")\\n\"";
        ret2+=")\\n\"";
        ret3+=")\\n\"";

        for i in range(self.siglen):
            if (i%16)==0 :
                ret1+="\n   ";
                ret2+="\n   ";
                ret3+="\n   ";
            ret1+=",s1["+str(i)+"]";
            ret2+=",s2["+str(i)+"]";
            ret3+=",s3["+str(i)+"]";

        ret1+="\n";
        ret2+="\n";
        ret3+="\n";
        ret1="\
  printf(\""+ret1+"  );\n";
        ret2="\
  printf(\""+ret2+"  );\n";
        ret3="\
  printf(\""+ret3+"  );\n";
        return ret+ret1+ret2+ret3+"}\n";

    def genPrintQueue(self):
        ret="\
void printQueue(struct State *s, short *qos,int id){\n\
  Q1 *q=((Q1 *)(((unsigned char *)s)+(int)qos[id-1]));\n\
  uchar *c=(uchar*)(&(q->contents));\n\
  printf(\"Q%d:Qlen=%d,_t=%d\\n\",id,q->Qlen,q->_t);\n";
        ret+="\
  printf(\"(%d,%d,%d,%d,%d,ri[%d";
        for i in range(1,self.nodes):
            ret+=",%d";
        ret+="],%d)\\n\"\n    ";
        for i in range(6+self.nodes):
            ret+=",c["+str(i)+"]";
        ret+=");\n";
        return ret+"\n}\n";

    def genPrintHeader(self):
        return '\
#ifndef STATE_PRINT_H\n\
#define STATE_PRINT_H\n\
#include "pan.h"\n\
#include "replace.h"\n';

    def genPrintCode(self):
        fileS=Path('./isdsr_print_src');
        file_code=Path('./print_state.c');
        file_header=Path('./print_state.h');


        ret='#include <stdio.h>\n\
#include <string.h>\n\
#include "replace.h"\n\
#include "print_state.h"\n';
        ret+=self.genPrintQueue();
        ret+=self.genPrintPacket();
        ret+=self.genPrintPacketWithSig();
        with fileS.open() as f:
            ret+=f.read();
        with file_code.open('w') as f:
            f.write(ret);

        ret=self.genPrintHeader();
        ret+='\
void printPacket(struct packet*);\n\
void printPacketWithSig(struct packet *pkt);\n\
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
        ret+="replace(permutation,&now,&tmp_state,proc_offset,q_offset,nodes);\n";
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
        subprocess.check_output(['spin1024','-a','isdsr_gen.pml'])
        rcg.genReplace();
        isg.genInsertingCode();
        ps.genPrintCode();
        suffix="n"+str(self.nodes)+"a"+str(self.around);
        #subprocess.check_output(['gcc','-DNOREDUCE','-o','po-'+suffix,'pan.c','replace_automated.c','print_automated.c'])
        #subprocess.check_output(['gcc','-DNOREDUCE','-o','pa-'+suffix,'pan_automated.c','replace_automated.c','print_automated.c'])


nodes=8;
around=1;
cg=CodeGeneration(nodes,around);
cg.genPromelaCsource();
