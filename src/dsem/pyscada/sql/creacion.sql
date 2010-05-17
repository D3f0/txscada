-- -*- coding: utf8 -*-
-- Creacion de la DB

DROP DATABASE IF EXISTS `dsem`;
-- DROP USER IF EXISTS dsem;
CREATE DATABASE `dsem`;
GRANT ALL ON dsem.* TO `dsem`@`locahost` IDENTIFIED BY 'passmenot';

USE dsem;


-- MySQL dump 10.11
--
-- Host: localhost    Database: dsem
-- ------------------------------------------------------
-- Server version	5.0.75-0ubuntu10

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `AI`
--

DROP TABLE IF EXISTS `AI`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `AI` (
  `id` int(11) NOT NULL auto_increment,
  `uc_id` int(11) default NULL,
  `nro_port` int(11) default NULL,
  `valor` smallint(6) default NULL,
  PRIMARY KEY  (`id`),
  KEY `uc_id` (`uc_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `AI`
--

LOCK TABLES `AI` WRITE;
/*!40000 ALTER TABLE `AI` DISABLE KEYS */;
/*!40000 ALTER TABLE `AI` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CO`
--

DROP TABLE IF EXISTS `CO`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `CO` (
  `id_CO` int(11) NOT NULL auto_increment,
  `ip_address` varchar(15) NOT NULL,
  `hab` tinyint(1) NOT NULL,
  `t_out` float NOT NULL,
  `max_retry` smallint(6) NOT NULL,
  `poll_delay` float NOT NULL,
  `nombre_co` varchar(40) default NULL,
  PRIMARY KEY  (`id_CO`),
  UNIQUE KEY `ip_address` (`ip_address`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `CO`
--

LOCK TABLES `CO` WRITE;
/*!40000 ALTER TABLE `CO` DISABLE KEYS */;
/*!40000 ALTER TABLE `CO` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Calle`
--

DROP TABLE IF EXISTS `Calle`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `Calle` (
  `id` int(11) NOT NULL default '0',
  `nombre` varchar(40) default NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `Calle`
--

LOCK TABLES `Calle` WRITE;
/*!40000 ALTER TABLE `Calle` DISABLE KEYS */;
INSERT INTO `Calle` VALUES (177,'12 DE OCTUBRE'),(351,'13 DE JULIO'),(40,'25 DE MAYO'),(49,'26 DE NOVIEMBRE'),(113,'28 DE JULIO'),(146,'9 DE JULIO'),(228,'A. JENKINS'),(308,'A.MATHEWS'),(272,'A.P. BEL'),(265,'A.P. BELL'),(188,'A.P.BELL'),(288,'ALBERDI'),(77,'ALCAZABA'),(249,'ALDERETE'),(26,'AMEGHINO'),(30,'ARTIGAS'),(252,'AV. DE LOS TRABAJ'),(93,'AV. RAWSON'),(127,'AV.CENTENARIO'),(292,'AV.FONTANA'),(330,'AVDA. EVA PERON'),(353,'AVELLANEDA'),(220,'AVENIDA'),(319,'AZOPARDO'),(174,'BAHIA SIN FONDO'),(126,'BEGHIN'),(179,'BELGRANO'),(305,'BERWYN'),(290,'BRASIL'),(37,'BROWN'),(114,'BS. AS.'),(111,'BUENOS AIRES'),(75,'BURMEISTER'),(354,'C. GARDEL'),(375,'C.ARGENTINA'),(244,'C.CHIQUICHANO'),(363,'C.GRAL.BELGRANO'),(315,'C.NAHUELPAN'),(142,'C.NAMUNCURA'),(261,'CABOT'),(78,'CAC. NAHUELQUIR'),(340,'CACIQUE NAHUELPAN'),(236,'CADFAN HUGHES'),(99,'CALDERON'),(56,'CAMARONES'),(169,'CAMBRIN'),(162,'CANGALLO'),(189,'CAP.MURGA'),(280,'CARRASCO'),(358,'CATAMARCA'),(294,'CEBALLOS'),(46,'CERRO CENTINELA'),(338,'CHACO'),(253,'CIPOLLETTI'),(175,'CNEL. PALACIOS'),(302,'COLOMBIA'),(341,'COLON'),(184,'COMAHUE'),(224,'CONDARCO'),(320,'CONESA'),(39,'CORCOVADO'),(107,'CORRIENTES'),(301,'COSTA RICA'),(42,'CRUZ DEL SUR'),(117,'CUBA'),(322,'D.LL. JONES'),(47,'DALEOSO'),(51,'DOLAVON'),(254,'DON BOSCO'),(248,'E. HANN'),(310,'E.ROBERTS'),(90,'ECUADOR'),(29,'EDISON'),(202,'EL CARMEN'),(57,'EL MAITEN'),(102,'ELSGOOD'),(109,'ENTRE RIOS'),(65,'EPUYEN'),(43,'EPUYEN (N)'),(307,'ESPAÃ‘A'),(62,'ESQUEL'),(159,'F. VIEJO'),(200,'F.L.BELTRAN'),(150,'F.SAN JOSE'),(334,'FELDMAN'),(295,'FTE. SAN JOSE'),(235,'FUCHS'),(211,'G. MAYO'),(52,'GAIMAN'),(148,'GALES'),(227,'GALINA'),(66,'GAN GAN'),(44,'GASTRE (N)'),(240,'GDOR. TELLO'),(53,'GDOR.COSTA'),(72,'GUEMES'),(135,'H. BEGHIN'),(119,'H. JONES'),(219,'H. YRIGOYEN'),(101,'H.L. JONES'),(73,'H.L.JONES'),(327,'HERNANDEZ'),(287,'HONDURAS'),(344,'INGENIEROS'),(277,'INMIGRANTES'),(259,'ITALIA'),(76,'J. DE LA PIEDRA'),(345,'J. EVANS'),(279,'J. HERNANDEZ'),(156,'J. JONES'),(232,'J. KATTERFIELD'),(281,'J. MUZIO'),(210,'J. SOSA'),(79,'J.A. ROCA'),(136,'J.A.ROCA'),(213,'J.M. DE ROSAS'),(180,'J.M.DE ROSAS'),(347,'JOSE BERRETA'),(231,'JOSIAH WILLIAMS'),(312,'JUAN EVANS'),(96,'JUAN XXIII'),(367,'JUJUY'),(230,'L.N. ALEM'),(241,'L.N.ALEM'),(38,'LAGO PUELO'),(229,'LAMADRID'),(350,'LAS HERAS'),(89,'LAURA VICUÂ¥A'),(255,'LEWIS JONES'),(242,'LEZANA'),(118,'LIBERTAD'),(24,'LOPEZ Y PLANES'),(54,'LOS ALTARES'),(291,'LOS ANDES'),(173,'LOS MARTIRES'),(226,'LOVE PARRY'),(282,'M. CUTILLO'),(283,'M. FIERRO'),(178,'M. HUMPHREYS'),(88,'M. RODRIGUEZ'),(321,'M.FIERRO'),(157,'MAESTROS PUNTANOS'),(343,'MAGALLANES'),(34,'MAIPU'),(190,'MALACARA'),(87,'MALASPINA'),(55,'MAMEL'),(25,'MARCONI'),(185,'MERMOZ'),(106,'MEXICO'),(31,'MICHAEL D.JONES'),(316,'MISIONES'),(192,'MITRE'),(284,'MORENO'),(116,'MORETEAU'),(85,'MORGAN'),(176,'MORIAH'),(74,'MOSCONI'),(250,'MOYANO'),(33,'MUSTERS'),(298,'NICARAGUA'),(82,'O\'HIGGINS'),(374,'O.SMITH'),(100,'ONETO'),(161,'OWEN'),(129,'P. JUNTA'),(133,'P. MORENO'),(71,'P.DALEOSO'),(28,'P.MORENO'),(137,'PARAGUAY'),(50,'PASO DE INDIOS'),(166,'PATAGONIA'),(140,'PECORARO'),(86,'PEDRO DERBES'),(191,'PELLEGRINI'),(332,'PENINSULA VALDES'),(289,'PERU'),(170,'PIEDRABUENA'),(155,'PIETROBELLI'),(203,'PORTUGAL'),(369,'POSADAS'),(198,'R.DE ESCALADA'),(112,'RAMON Y CAJAL'),(61,'RAWSON'),(58,'RIO NEGRO'),(45,'RIO PICO'),(181,'RIVADAVIA'),(36,'RONDEAU'),(234,'ROSALES'),(164,'RUCA-HUE'),(149,'RUTA NACIONAL NÂ°2'),(377,'RUTA NACIONAL NÂ°3'),(336,'S. ALLENDE'),(104,'S. DE ALCAZABA'),(361,'S. ORTEGA'),(128,'S. ORTIZ'),(368,'SAAVEDRA'),(238,'SAENZ PEÂ¥A'),(365,'SALTA'),(311,'SAN DAVID'),(297,'SAN LUIS'),(41,'SAN MARTIN'),(108,'SANTA FE'),(314,'SARMIENTO'),(125,'SAYHUEQUE'),(251,'SGO. DEL ESTERO'),(201,'SGTO. CABRAL'),(80,'SOBERANIA NACIONA'),(23,'SOLER'),(216,'T. DEL FUEGO'),(171,'T.DEL FUEGO'),(48,'TECKA'),(342,'TEHUELCHES'),(335,'TELLO'),(67,'TELSEN'),(225,'THOMAS'),(158,'THOMAS DAVIES'),(59,'TREVELIN'),(207,'TTE. GARCIA'),(359,'TUCUMAN'),(326,'TUPUNG.'),(317,'TUPUNGATO'),(285,'URQUIZA'),(110,'URUGUAY'),(239,'V. MIMOSA'),(165,'V. VESTA'),(163,'VENUS'),(143,'VESPUCIO'),(68,'VIEDMA'),(84,'VILLARINO'),(154,'VILLEGAS'),(313,'W. DAVIES'),(328,'WINTER'),(194,'ZAPIOLA');
/*!40000 ALTER TABLE `Calle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DI`
--

DROP TABLE IF EXISTS `DI`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `DI` (
  `id` int(11) NOT NULL auto_increment,
  `uc_id` int(11) default NULL,
  `nro_port` int(11) default NULL,
  `valor` smallint(6) default NULL,
  PRIMARY KEY  (`id`),
  KEY `uc_id` (`uc_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `DI`
--

LOCK TABLES `DI` WRITE;
/*!40000 ALTER TABLE `DI` DISABLE KEYS */;
/*!40000 ALTER TABLE `DI` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EV`
--

DROP TABLE IF EXISTS `EV`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `EV` (
  `id` int(11) NOT NULL auto_increment,
  `uc_id` int(11) default NULL,
  `tipo` smallint(6) default NULL,
  `prio` smallint(6) default NULL,
  `codigo` smallint(6) default NULL,
  `nro_port` smallint(6) NOT NULL,
  `nro_bit` smallint(6) NOT NULL,
  `estado_bit` smallint(6) NOT NULL,
  `ts_bit` datetime NOT NULL,
  `ts_bit_ms` int(11) NOT NULL,
  `atendido` varchar(1) default 'n',
  `ts_a` datetime default NULL,
  `ts_r` datetime default NULL,
  PRIMARY KEY  (`id`),
  KEY `uc_id` (`uc_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5604 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `EV`
--

LOCK TABLES `EV` WRITE;
/*!40000 ALTER TABLE `EV` DISABLE KEYS */;
/*!40000 ALTER TABLE `EV` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EV_Descripcion`
--

DROP TABLE IF EXISTS `EV_Descripcion`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `EV_Descripcion` (
  `id` int(11) NOT NULL auto_increment,
  `tipo` smallint(6) NOT NULL,
  `codigo` smallint(6) NOT NULL,
  `descripcion` varchar(50) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `codigo_tipo_unico` (`tipo`,`codigo`)
) ENGINE=MyISAM AUTO_INCREMENT=8 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `EV_Descripcion`
--

LOCK TABLES `EV_Descripcion` WRITE;
/*!40000 ALTER TABLE `EV_Descripcion` DISABLE KEYS */;
INSERT INTO `EV_Descripcion` VALUES (1,2,8,'Falta de Comunicación con el CC'),(2,2,2,'Estado escritura diferida EEPROM'),(3,2,3,'Evento Provocado desde el CC (Dummy)'),(4,1,9,'Corto Circuito en lámpara. Movi:'),(5,1,2,'Circuito Abierto en DOS lámparas. Movi:'),(6,1,1,'Circuito Abierto en UNA lámpara. Movi:'),(7,0,0,'Evento de Campo Puerto');
/*!40000 ALTER TABLE `EV_Descripcion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Esquina`
--

DROP TABLE IF EXISTS `Esquina`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `Esquina` (
  `id` int(11) NOT NULL auto_increment,
  `uc_id` int(11) default NULL,
  `x` float default NULL,
  `y` float default NULL,
  PRIMARY KEY  (`id`),
  KEY `uc_id` (`uc_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `Esquina`
--

LOCK TABLES `Esquina` WRITE;
/*!40000 ALTER TABLE `Esquina` DISABLE KEYS */;
/*!40000 ALTER TABLE `Esquina` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Esquina_Calles`
--

DROP TABLE IF EXISTS `Esquina_Calles`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `Esquina_Calles` (
  `id` int(11) NOT NULL auto_increment,
  `esquina_id` int(11) default NULL,
  `calle_id` int(11) default NULL,
  `angulo` smallint(6) default NULL,
  `tipo_calle` smallint(6) default NULL,
  `sentido` varchar(2) default NULL,
  PRIMARY KEY  (`id`),
  KEY `calle_id` (`calle_id`),
  KEY `esquina_id` (`esquina_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `Esquina_Calles`
--

LOCK TABLES `Esquina_Calles` WRITE;
/*!40000 ALTER TABLE `Esquina_Calles` DISABLE KEYS */;
/*!40000 ALTER TABLE `Esquina_Calles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `SV`
--

DROP TABLE IF EXISTS `SV`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `SV` (
  `id` int(11) NOT NULL auto_increment,
  `uc_id` int(11) default NULL,
  `nro_sv` int(11) default NULL,
  `valor` smallint(6) default NULL,
  PRIMARY KEY  (`id`),
  KEY `uc_id` (`uc_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `SV`
--

LOCK TABLES `SV` WRITE;
/*!40000 ALTER TABLE `SV` DISABLE KEYS */;
/*!40000 ALTER TABLE `SV` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Semaforo`
--

DROP TABLE IF EXISTS `Semaforo`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `Semaforo` (
  `id` int(11) NOT NULL auto_increment,
  `uc_id` int(11) default NULL,
  `Esquina_Calles_id` int(11) default NULL,
  `ti_mov` smallint(6) default NULL,
  `subti_mov` smallint(6) default NULL,
  `n_mov` smallint(6) default NULL,
  `x` int(11) default NULL,
  `y` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `uc_id` (`uc_id`),
  KEY `Esquina_Calles_id` (`Esquina_Calles_id`)
) ENGINE=MyISAM AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `Semaforo`
--

LOCK TABLES `Semaforo` WRITE;
/*!40000 ALTER TABLE `Semaforo` DISABLE KEYS */;
/*!40000 ALTER TABLE `Semaforo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `UC`
--

DROP TABLE IF EXISTS `UC`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `UC` (
  `id` int(11) NOT NULL auto_increment,
  `co_id` int(11) NOT NULL,
  `id_UC` int(11) NOT NULL,
  `zona` smallint(6) default NULL,
  `can_movi` smallint(6) default NULL,
  `nombre_uc` varchar(40) default NULL,
  `hab` tinyint(1) default NULL,
  PRIMARY KEY  (`id`,`co_id`,`id_UC`),
  KEY `co_id` (`co_id`)
) ENGINE=MyISAM AUTO_INCREMENT=5 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Dumping data for table `UC`
--

LOCK TABLES `UC` WRITE;
/*!40000 ALTER TABLE `UC` DISABLE KEYS */;
/*!40000 ALTER TABLE `UC` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-04-15 10:23:17
