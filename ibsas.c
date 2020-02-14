#include "ibsas.h"

void set_up(){
	element_random(mpk_ibsas.g1);
	element_random(msk_ibsas.a1);
	element_random(msk_ibsas.a2);
	element_pow_zn(mpk_ibsas.g2, mpk_ibsas.g1, msk_ibsas.a1);
	element_pow_zn(mpk_ibsas.g3, mpk_ibsas.g1, msk_ibsas.a2);

}

void H1(char *message,int len,element_t h){
	element_from_hash(h,message,len);
	//element_printf("H1(%s)=%B\n",message,h);
	return;
}

void print_hex(char* arr, int len)
{
    int i;
    for(i = 0; i < len; i++)
        printf("%02x", (unsigned char) arr[i]);
}

void H2(const unsigned char *message,int len,element_t h){
	unsigned char hash[SHA256_DIGEST_LENGTH];
	SHA256( message,len , hash );
	element_from_hash(h,hash,SHA256_DIGEST_LENGTH);

	//element_printf("H2(%s)=%B\n",message,h);
	return;
}

void H3(const unsigned char *message,int len,element_t h){
	unsigned char hash[SHA256_DIGEST_LENGTH];
	mpz_t a; mpz_init(a);
	SHA256( message,len , hash );
	mpz_import(a, SHA256_DIGEST_LENGTH, 1, sizeof(hash[0]), 0, 0, hash);
	element_set_mpz(h,a);

	//element_printf("H3(%s)=%B\n",message,h);
	return;
}

void key_derivation(pairing_t pairing, char* id, int idlen, id_secret_key *isk, master_sk *msk){
	element_t temp1, temp2;
	element_init_G1(temp1, pairing);
	element_init_G1(temp2, pairing);
	H1(id,idlen,temp1);
	H2((unsigned char *)id,idlen,temp2);
	element_pow_zn(isk->sk1, temp1, msk->a1);
	element_pow_zn(isk->sk2, temp2, msk->a2);
	element_clear(temp1);
	element_clear(temp2);
}



//master_sk sakujo wasurenai!!!


void signing(pairing_t pairing, master_pk *mpk, id_secret_key *isk, signature* sig, char *id, char *msg){
	//printf("ibsas signing start msg=%s\n",msg);
	//printSignatures(sig);


	element_t r,x,temp1,temp2,temp4,temp5,temp6,temp7,tsig3;
	element_init_Zr(r,pairing);
	element_init_Zr(x,pairing);
	element_init_G1(tsig3,pairing);
	element_init_G1(temp1,pairing);
	element_init_G1(temp2,pairing);
	element_init_G1(temp4,pairing);
	element_init_G1(temp5,pairing);
	element_init_Zr(temp6,pairing);
	element_init_G1(temp7,pairing);
	//printf("0\n");

	//element_random(r);
	//element_random(x);

	element_set_si(r, 5);
	element_set_si(x, 10);

	element_pow_zn(temp1,mpk->g1,x);
	//printf("1\n");
	element_pow_zn(temp2,mpk->g1,r);
	//printf("2\n");
	element_set(tsig3,sig->sig3);
	element_add(sig->sig3,sig->sig3,temp1);
	element_add(sig->sig2,sig->sig2,temp2);
	element_pow_zn(temp4,tsig3,r);
	element_pow_zn(temp5,sig->sig2,x);
	int idmeslength=strlen(id)+strlen(msg);
	char idm[idmeslength];
	sprintf(idm,"%s%s",id,msg);
	//printf("signing msg %s\n",idm);
	//printf("len=%d\n",idlen+meslen);
	H3((unsigned char*)idm,idmeslength,temp6);
	//element_printf("H3=%B\n",temp6);
	//element_set_mpz(temp6,a);void readECParameter(ecparam* param)
	//element_printf("t6=%B\n",temp6);
	//gmp_printf("a=%Zd\n",a);
	//element_printf("sk1=%B\n",idsk.sk1);
	//element_printf("temp7=%B\n",temp7);
	//element_printf("temp6=%B\n",temp6);
	//element_printf("isk.sk1=%B\n",node->isk.sk1);
	element_pow_zn(temp7,isk->sk1,temp6);
	//printf("3\n");
	element_add(sig->sig1,sig->sig1,temp4);
	element_add(sig->sig1,sig->sig1,temp5);
	element_add(sig->sig1,sig->sig1,isk->sk2);
	element_add(sig->sig1,sig->sig1,temp7);

	element_clear(tsig3);
	element_clear(r);
	element_clear(x);
	element_clear(temp1);
	element_clear(temp2);
	element_clear(temp4);
	element_clear(temp5);
	element_clear(temp6);
	element_clear(temp7);
	return;
}


int verification(pairing_t pairing, master_pk *mpk, signature *sig, char *msg, int cnt, int idlen){
	element_t temp1,temp2,temp3,temp4,temp5,temp6,temp7,temp8,temp9,temp10;
	//printf("0\n");
	element_init_GT(temp1,pairing);
	element_init_GT(temp2,pairing);
	element_init_G1(temp3,pairing);
	element_init_G1(temp4,pairing);
	element_init_G1(temp5,pairing);
	element_init_Zr(temp6,pairing);
	element_init_G1(temp7,pairing);
	element_init_G1(temp8,pairing);
	element_init_GT(temp9,pairing);
	element_init_GT(temp10,pairing);
	//printf("1\n");
	element_pairing(temp1,sig->sig1,mpk->g1);
	element_pairing(temp2,sig->sig2,sig->sig3);
	//element_printf("temp1=%B\n",temp1);
	int i=0,l,ret=1;
	//int sndrlen=strlen(pkt->sndr);
	//int msglength=strlen(pkt->msg);
	//int idmsglength=sndrlen+strlen(pkt->msg);
	char mes[MAX_MES_LEN],mes2[MAX_MES_LEN],mes3[MAX_MES_LEN];
	char tmpid[idlen+1];
	element_set0(temp3);
	element_set0(temp8);
	mes[0]='\0';
//	sprintf(mes,"");
	do{
		int j=0;
		for(j=0;j<idlen;j++){
			tmpid[j]=msg[((i*4)+j)];
		}
		tmpid[idlen]='\0';
		H2((unsigned char*)tmpid,idlen,temp4);
		element_add(temp3,temp3,temp4);
		H1(tmpid,idlen,temp5);
		//printf("verify user=%s\n",tmpid);
		sprintf(mes3,"%s%s",mes,tmpid);

		//printf("verify mes3=%s\n",mes3);
		sprintf(mes2,"%s%s",tmpid,mes3);
		sprintf(mes,"%s",mes3);
		//printf("verify mes2=%s\n",mes2);
		l=strlen(mes2);
		//printf("l=%d\n",l);
		H3((unsigned char*)mes2,l,temp6);
		//element_printf("H3=%B\n",temp6);
		element_pow_zn(temp7,temp5,temp6);
		element_add(temp8,temp8,temp7);
		i++;
	}while(i<cnt);


	element_pairing(temp9,temp3,mpk->g3);
	element_pairing(temp10,temp8,mpk->g2);
	element_mul(temp2,temp2,temp9);
	element_mul(temp2,temp2,temp10);

	if (!element_cmp(temp1, temp2)) {
		ret= 1;
    } else {
      element_invert(temp1, temp1);
      if (!element_cmp(temp1, temp2)) {
      	ret= 1;
      } else {
      	ret= 0;
      }
    }



	element_clear(temp1);
	element_clear(temp2);
	element_clear(temp3);
	element_clear(temp4);
	element_clear(temp5);
	element_clear(temp6);
	element_clear(temp7);
	element_clear(temp8);
	element_clear(temp9);
	element_clear(temp10);
	return ret;
}

void constructMasterKeys(ecparam *param){
	FILE *fp;
  fp=fopen(param->filename,"r");
  param->cnt= fread(param->param, 1, 2048, fp);

	pairing_init_set_buf(pairing_ibsas, param->param, param->cnt);
	element_init_G1(mpk_ibsas.g1, pairing_ibsas);
	element_init_G1(mpk_ibsas.g2, pairing_ibsas);
	element_init_G1(mpk_ibsas.g3, pairing_ibsas);
	element_init_Zr(msk_ibsas.a1, pairing_ibsas);
	element_init_Zr(msk_ibsas.a2, pairing_ibsas);
}

void destructMasterKeys(){
	element_clear(mpk_ibsas.g1);
	element_clear(mpk_ibsas.g2);
	element_clear(mpk_ibsas.g3);
	element_clear(msk_ibsas.a1);
	element_clear(msk_ibsas.a2);
	pairing_clear(pairing_ibsas);
}

void printSignatureElements(signature *sigs){

	element_printf("sig1=%B\n",sigs->sig1);
	element_printf("sig2=%B\n",sigs->sig2);
	element_printf("sig3=%B\n",sigs->sig3);
}
