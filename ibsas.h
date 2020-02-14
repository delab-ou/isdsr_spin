#ifndef IBSAS_H
#define IBSAS_H
#include <pbc/pbc.h>
#include <pbc/pbc_test.h>
#include <stdio.h>
#include <string.h>
#include <openssl/sha.h>

typedef struct{
	char* filename;
	char param[2048];
	size_t cnt;
} ecparam;

typedef struct{
	element_t g1;
	element_t g2;
	element_t g3;
} master_pk;

typedef struct{
	element_t a1;
	element_t a2;
} master_sk;

typedef struct{
	element_t sk1;
	element_t sk2;
} id_secret_key;

typedef struct{
	element_t sig1;
	element_t sig2;
	element_t sig3;
} signature;


#define MAX_MES_LEN 4000

pairing_t pairing_ibsas;
master_pk mpk_ibsas;
master_sk msk_ibsas;
ecparam param;

void H1(char*,int,element_t);
void H2(const unsigned char *message,int len,element_t h);
void H3(const unsigned char *message,int len,element_t h);
void set_up();
void key_derivation(pairing_t pairing, char* id, int idlen, id_secret_key *isk, master_sk *msk);
void signing(pairing_t pairing, master_pk *mpk, id_secret_key *isk, signature* sig, char *id, char *msg);
int verification(pairing_t pairing, master_pk *mpk, signature *sig, char *msg, int cnt, int idlen);

void constructMasterKeys(ecparam *param);
void destructMasterKeys();
void printSignatureElements(signature *sigs);

#endif
