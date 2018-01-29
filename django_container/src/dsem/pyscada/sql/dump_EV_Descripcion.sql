-- MySQL dump 10.11
--
-- Host: localhost    Database: dsem
-- ------------------------------------------------------
-- Server version	5.0.51a-3ubuntu5.4

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
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2009-02-08  4:30:41
