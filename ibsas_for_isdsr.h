#ifndef IBSAS_FOR_ISDSR_H
#define IBSAS_FOR_ISDSR_H
#include "ibsas.h"

typedef struct{
	char* id;
	master_pk* mpk;
	master_sk* msk;
	id_secret_key isk;
	int idlen;
	pairing_t pairing;
} nodeinfo;

typedef struct{
	char* sndr;
	char* src;
	char* dest;
	char* msg;
	int rilen;
	int hops;
	int msglength;
	signature sig;
} pktinfo;


#define MAX_MES_LEN 4000

void initialize(pairing_t,master_pk*,master_sk*);
void initializeNodeInfo(char** names,nodeinfo* nodes,char *paramfile,int count);
void initnode(nodeinfo* node,char* name,master_pk* mpk,master_sk* msk,ecparam* param);
void key_derivation_node(nodeinfo* node);
void signing_node(pktinfo* pkt,nodeinfo* node);
int verification_node(pktinfo* pkt,nodeinfo* node);
void generatePacket(pktinfo* pkt,nodeinfo* node);
void destructNode(nodeinfo* node);
void destructPkt(pktinfo* pkt);
void destruction(nodeinfo* nodes,pktinfo* pkt);

#endif
