#ifndef ISDSR_SPIN_H
#define ISDSR_SPIN_H
#include <stdio.h>
#include "pan.h"
#include "ibsas_for_isdsr.h"


void signingPacket(struct packet *pkt, int id,nodeinfo *nodes);
int verifyingPacket(struct packet *pkt, int id, nodeinfo *nodes);
void initialize();
#endif
