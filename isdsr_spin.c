#include "isdsr_spin.h"

void signingPacket(struct packet *pkt, int id,nodeinfo *nodes){
	int i=0;
	char msg[100];
	msg[0]='\0';
	for(i=0;i<=pkt->rilen;i++){
		sprintf(msg,"%s%s",msg,nodes[pkt->ri[i]-1].id);
	}
	pktinfo _pkt;
	_pkt.src=nodes[pkt->src-1].id;
	_pkt.sndr=nodes[pkt->ri[pkt->rilen]-1].id;
	_pkt.dest=nodes[pkt->dest-1].id;
	_pkt.msg=msg;
	//_pkt.src=nodes[pkt->src-1].id;
	//_pkt.sndr=nodes[id-1].id;

	if(strcmp(_pkt.src,_pkt.sndr)!=0){
		element_init_G1(_pkt.sig.sig1,nodes[id-1].pairing);
		element_init_G1(_pkt.sig.sig2,nodes[id-1].pairing);
		element_init_G1(_pkt.sig.sig3,nodes[id-1].pairing);

		element_from_bytes(_pkt.sig.sig1,pkt->sig1);
		element_from_bytes(_pkt.sig.sig2,pkt->sig2);
		element_from_bytes(_pkt.sig.sig3,pkt->sig3);
	}


	generatePacket(&_pkt,&nodes[id-1]);
	element_to_bytes((unsigned char *)pkt->sig1,_pkt.sig.sig1);
	element_to_bytes((unsigned char *)pkt->sig2,_pkt.sig.sig2);
	element_to_bytes((unsigned char *)pkt->sig3,_pkt.sig.sig3);
	destructPkt(&_pkt);


}


int verifyingPacket(struct packet *pkt, int id, nodeinfo *nodes){
	int i=0;
	int ret=0;
	char msg[100];
	msg[0]='\0';
	for(i=0;i<=pkt->rilen;i++){
		sprintf(msg,"%s%s",msg,nodes[pkt->ri[i]-1].id);
	}
	pktinfo _pkt;
	_pkt.msg=msg;
	_pkt.dest=nodes[pkt->dest-1].id;
	_pkt.hops=pkt->hops;
	_pkt.rilen=pkt->rilen;
	_pkt.sndr=nodes[pkt->ri[pkt->hops-1]-1].id;

	element_init_G1(_pkt.sig.sig1,nodes[id-1].pairing);
	element_init_G1(_pkt.sig.sig2,nodes[id-1].pairing);
	element_init_G1(_pkt.sig.sig3,nodes[id-1].pairing);

	element_from_bytes(_pkt.sig.sig1,(unsigned char*)(pkt->sig1));
	element_from_bytes(_pkt.sig.sig2,(unsigned char*)(pkt->sig2));
	element_from_bytes(_pkt.sig.sig3,(unsigned char*)(pkt->sig3));

	ret=verification_node(&_pkt,&nodes[id-1]);
	destructPkt(&_pkt);
	return ret;
}
