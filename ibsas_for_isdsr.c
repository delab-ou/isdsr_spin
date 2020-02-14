#include "ibsas_for_isdsr.h"

#define USER_NUM 3
#define ID_LENGTH 4
#define MAX_USERS 500

void initializeNodeInfo(char** names,nodeinfo* nodes,char *paramfile,int count){
	ecparam param;
	param.filename=paramfile;
	printf("param file is %s\n",param.filename);
	constructMasterKeys(&param);
	set_up();
	int cnt=0;
	for(cnt=0;cnt<count;cnt++){
		initnode((nodes+cnt),names[cnt],&mpk_ibsas,&msk_ibsas,&param);
		key_derivation_node((nodes+cnt));
	}
}

void key_derivation_node(nodeinfo* node){
	key_derivation(node->pairing,node->id, node->idlen,&(node->isk),node->msk);
}
void signing_node(pktinfo* pkt,nodeinfo* node){
	signing(node->pairing, node->mpk, &(node->isk), &(pkt->sig), node->id, pkt->msg);
}

int verification_node(pktinfo* pkt,nodeinfo* node){
	return verification(node->pairing, node->mpk, &(pkt->sig), pkt->msg, pkt->rilen+1, node->idlen);
}
void destructNode(nodeinfo* node){
	int cnt=0;
	for(cnt=0;cnt<USER_NUM;cnt++){
		element_clear((node+cnt)->isk.sk1);
		element_clear((node+cnt)->isk.sk2);
		pairing_clear((node+cnt)->pairing);
	}

}
void destructPkt(pktinfo* pkt){
	//element_printf("sig1=%B\n",pkt->sig.sig1);
	//element_printf("sig2=%B\n",pkt->sig.sig2);
	//element_printf("sig3=%B\n",pkt->sig.sig3);
	//printf("destruct pkt1\n");
	element_clear(pkt->sig.sig1);
		//printf("destruct pkt2\n");
	element_clear(pkt->sig.sig2);
		//printf("destruct pkt3\n");
	element_clear(pkt->sig.sig3);
		//printf("destruct pkt4\n");
}
void destruction(nodeinfo* nodes,pktinfo* pkt){
	destructMasterKeys();
	destructPkt(pkt);
	destructNode(nodes);
}
void initnode(nodeinfo* node,char* name,master_pk* mpk,master_sk* msk,ecparam* param){
	node->msk=msk;
	node->mpk=mpk;
	node->id=name;
	//printf("init node parames\n cnt %d\n param %s\n",param->cnt,param->param);
	pairing_init_set_buf(node->pairing, param->param, param->cnt);
	//printf("%s is generating sk\n",name);
	element_init_G1(node->isk.sk1, node->pairing);
	element_init_G1(node->isk.sk2, node->pairing);

	node->idlen=strlen(node->id);
	//element_printf("isk sk1=%B\n",node->isk.sk1);
	//element_printf("isk sk2=%B\n",node->isk.sk2);
}

void generatePacket(pktinfo* pkt,nodeinfo* node){
	pkt->sndr=node->id;
	if(strcmp(pkt->src,node->id)==0){
		//printf("start from src:%s\n",node->id);
		element_init_G1(pkt->sig.sig1,node->pairing);
		element_init_G1(pkt->sig.sig2,node->pairing);
		element_init_G1(pkt->sig.sig3,node->pairing);
		element_set1(pkt->sig.sig1);
		element_set1(pkt->sig.sig2);
		element_set1(pkt->sig.sig3);
	}

	signing_node(pkt,node);

}
/*

int main(int argc, char **argv) {
	//pairing_t pairing;
	char message[MAX_MES_LEN];
	struct timeval start,setup,keyder,sign,veri;
	char* users[MAX_USERS]={
		"0001","0002","1003","1004","1005","1006","1007","1008","1009","1010","1011","1012","1013","1014","1015","1016","1017","1018","1019","1020",
"1021","1022","1023","1024","1025","1026","1027","1028","1029","1030","1031","1032","1033","1034","1035","1036","1037","1038","1039","1040",
"1041","1042","1043","1044","1045","1046","1047","1048","1049","1050","1051","1052","1053","1054","1055","1056","1057","1058","1059","1060",
"1061","1062","1063","1064","1065","1066","1067","1068","1069","1070","1071","1072","1073","1074","1075","1076","1077","1078","1079","1080",
"1081","1082","1083","1084","1085","1086","1087","1088","1089","1090","1091","1092","1093","1094","1095","1096","1097","1098","1099","1100",
"1101","1102","1103","1104","1105","1106","1107","1108","1109","1110","1111","1112","1113","1114","1115","1116","1117","1118","1119","1120",
"1121","1122","1123","1124","1125","1126","1127","1128","1129","1130","1131","1132","1133","1134","1135","1136","1137","1138","1139","1140",
"1141","1142","1143","1144","1145","1146","1147","1148","1149","1150","1151","1152","1153","1154","1155","1156","1157","1158","1159","1160",
"1161","1162","1163","1164","1165","1166","1167","1168","1169","1170","1171","1172","1173","1174","1175","1176","1177","1178","1179","1180",
"1181","1182","1183","1184","1185","1186","1187","1188","1189","1190","1191","1192","1193","1194","1195","1196","1197","1198","1199","1200",
"1201","1202","1203","1204","1205","1206","1207","1208","1209","1210","1211","1212","1213","1214","1215","1216","1217","1218","1219","1220",
"1221","1222","1223","1224","1225","1226","1227","1228","1229","1230","1231","1232","1233","1234","1235","1236","1237","1238","1239","1240",
"1241","1242","1243","1244","1245","1246","1247","1248","1249","1250","1251","1252","1253","1254","1255","1256","1257","1258","1259","1260",
"1261","1262","1263","1264","1265","1266","1267","1268","1269","1270","1271","1272","1273","1274","1275","1276","1277","1278","1279","1280",
"1281","1282","1283","1284","1285","1286","1287","1288","1289","1290","1291","1292","1293","1294","1295","1296","1297","1298","1299","1300",
"1301","1302","1303","1304","1305","1306","1307","1308","1309","1310","1311","1312","1313","1314","1315","1316","1317","1318","1319","1320",
"1321","1322","1323","1324","1325","1326","1327","1328","1329","1330","1331","1332","1333","1334","1335","1336","1337","1338","1339","1340",
"1341","1342","1343","1344","1345","1346","1347","1348","1349","1350","1351","1352","1353","1354","1355","1356","1357","1358","1359","1360",
"1361","1362","1363","1364","1365","1366","1367","1368","1369","1370","1371","1372","1373","1374","1375","1376","1377","1378","1379","1380",
"1381","1382","1383","1384","1385","1386","1387","1388","1389","1390","1391","1392","1393","1394","1395","1396","1397","1398","1399","1400",
"1401","1402","1403","1404","1405","1406","1407","1408","1409","1410","1411","1412","1413","1414","1415","1416","1417","1418","1419","1420",
"1421","1422","1423","1424","1425","1426","1427","1428","1429","1430","1431","1432","1433","1434","1435","1436","1437","1438","1439","1440",
"1441","1442","1443","1444","1445","1446","1447","1448","1449","1450","1451","1452","1453","1454","1455","1456","1457","1458","1459","1460",
"1461","1462","1463","1464","1465","1466","1467","1468","1469","1470","1471","1472","1473","1474","1475","1476","1477","1478","1479","1480",
"1481","1482","1483","1484","1485","1486","1487","1488","1489","1490","1491","1492","1493","1494","1495","1496","1497","1498","1499","1500",
	};

	nodeinfo nodes[USER_NUM];

	//char *user_id[U->msk,node->id,node->idlen,&(node->isk),*(node->pairing)SER_NUM]={"Kenta Muranaka"};
	//master_pk mpk;
	//master_sk msk;
	ecparam param;
	if(argc!=2){
		printf("read param a.param\n");
	param.filename="a.param";
	}
	else{
		printf("read param %s\n",argv[1]);
	param.filename=argv[1];
	}

	// construction(pairing,&mpk,&msk,(char**)users,nodes,&param,0);
	initializeNodeInfo((char**)users,nodes,"a.param",USER_NUM);
	//element_printf("mpk g1=%B\n",mpk.g1);
	//element_printf("mpk g2=%B\n",mpk.g2);
	//element_printf("mpk g3=%B\n",mpk.g3);
	//element_printf("msk a1=%B\n",msk.a1);
	//element_printf("msk a2=%B\n",msk.a2);

	pktinfo pkt;
	pkt.src=nodes[0].id;
	//pkt.msg=nodes[0].id;
	pkt.msg="";
	pkt.hops=0;
	double ptime=0;
	int times=0;
	for(times=0;times<USER_NUM-1;times++){
		//printf("gen msg %s\n",pkt.msg);
		sprintf(message,"%s%s",pkt.msg,nodes[times].id);
		pkt.msg=message;
		pkt.hops++;
		gettimeofday(&start, NULL);
		generatePacket(&pkt,&nodes[times]);
		gettimeofday(&sign, NULL);
		ptime=start.tv_sec-sign.tv_sec+(start.tv_usec-sign.tv_usec)*1.0E-6;
		printf("sign=%.3f\n",ptime);

	}
	gettimeofday(&start,NULL);
	int result=verification_node(&pkt,&nodes[USER_NUM-1]);
	gettimeofday(&veri,NULL);
	ptime=start.tv_sec-veri.tv_sec+(start.tv_usec-veri.tv_usec)*1.0E-6;
	printf("veri=%.3f\n",ptime);
	if(result){
		printf("success verification\n");
	}else{
		printf("NG\n");
	}
	//destruction(pairing, &mpk, &msk,nodes,&pkt);
	destruction(nodes,&pkt);

	int i=0;
	int t=1000;
	char cid[4];
	int id=2;
	for(i=0;i<4;i++){
		cid[i]='0'+(id/t);
		id=id%t;
		t=t/10;
	}
	printf("it is %s\n",cid);
}
*/
