-- MySQL dump 10.13  Distrib 8.0.42, for Win64 (x86_64)
--
-- Host: localhost    Database: bom
-- ------------------------------------------------------
-- Server version	8.0.42

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ingredient_inventory`
--

DROP TABLE IF EXISTS `ingredient_inventory`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredient_inventory` (
  `ingredient_id` varchar(10) NOT NULL,
  `ingredient_name` varchar(255) DEFAULT NULL,
  `quantity` float DEFAULT NULL,
  `unit` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`ingredient_id`),
  CONSTRAINT `ingredient_inventory_ibfk_1` FOREIGN KEY (`ingredient_id`) REFERENCES `ingredients` (`ingredient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredient_inventory`
--

LOCK TABLES `ingredient_inventory` WRITE;
/*!40000 ALTER TABLE `ingredient_inventory` DISABLE KEYS */;
INSERT INTO `ingredient_inventory` VALUES ('I001','Almonds',1000,'kg'),('I002','Anardana powder',1000,'kg'),('I003','Apple',1000,'kg'),('I004','Baby corn',1000,'kg'),('I005','Baby potato',1000,'kg'),('I006','Baking powder',1000,'kg'),('I007','Banana',1000,'kg'),('I008','Bay leaf',1000,'kg'),('I009','Beans',1000,'kg'),('I010','Beetroot',1000,'kg'),('I011','Besan',1000,'kg'),('I012','Bhindi',1000,'kg'),('I013','Black chana',1000,'kg'),('I014','Black pepper',1000,'kg'),('I015','Black-eyed peas',1000,'kg'),('I016','Boondi',1000,'kg'),('I017','Bread',1000,'kg'),('I018','Bread crumbs',1000,'kg'),('I019','Brinjal',1000,'kg'),('I020','Broken wheat',1000,'kg'),('I021','Brown rice',1000,'kg'),('I022','Bulgar wheat',1000,'kg'),('I023','Butter',1000,'kg'),('I024','Cabbage',1000,'kg'),('I025','Capsicum',1000,'kg'),('I026','Cardamom',1000,'kg'),('I027','Carrot',1000,'kg'),('I028','Cashew nuts',1000,'kg'),('I029','Cashew paste',1000,'kg'),('I030','Cauliflower',1000,'kg'),('I031','Chaat masala',1000,'kg'),('I032','Chana dal',1000,'kg'),('I033','Chana masala',1000,'kg'),('I034','Chana sprouts',1000,'kg'),('I035','Chenna',1000,'kg'),('I036','Chicken',1000,'kg'),('I037','Chickpeas',1000,'kg'),('I038','Cinnamon',1000,'kg'),('I039','Cloves',1000,'kg'),('I040','Coconut',1000,'kg'),('I041','Coconut milk',1000,'L'),('I042','Coffee powder',1000,'kg'),('I043','Coriander leaves',1000,'kg'),('I044','Coriander powder',1000,'kg'),('I045','Coriander seeds',1000,'kg'),('I046','Corn',1000,'kg'),('I047','Corn cob',1000,'kg'),('I048','Corn flakes',1000,'kg'),('I049','Cornflour',1000,'kg'),('I050','Crab meat',1000,'kg'),('I051','Cream',1000,'kg'),('I052','Cucumber',1000,'kg'),('I053','Cumin powder',1000,'kg'),('I054','Cumin seeds',1000,'kg'),('I055','Curd',1000000,'ml'),('I056','Curry leaves',1000000,'ml'),('I057','Custard powder',1000,'kg'),('I058','Dabeli masala',1000,'kg'),('I059','Dalia',1000,'kg'),('I060','Doodhi',1000,'kg'),('I061','Dried green peas',1000,'kg'),('I062','Dried white peas',1000,'kg'),('I063','Drumstick',1000,'kg'),('I064','Dry red chili',1000,'kg'),('I065','Egg',1000,'kg'),('I066','Eggplant',1000,'kg'),('I067','Eno',1000,'kg'),('I068','Fennel seeds',1000,'kg'),('I069','Fenugreek leaves',1000,'kg'),('I070','Fruit jam',1000,'kg'),('I071','Garam masala',1000,'kg'),('I072','Garlic',1000,'kg'),('I073','Gavar',1000,'kg'),('I074','Gawar',1000,'kg'),('I075','Ghee',1000,'kg'),('I076','Ginger',1000,'kg'),('I077','Green beans',1000,'kg'),('I078','Green black-eyed peas',1000,'kg'),('I079','Green chili',1000,'kg'),('I080','Green chutney',1000,'kg'),('I081','Green curry paste',1000,'kg'),('I082','Green moong dal',1000,'kg'),('I083','Green moong sprouts',1000,'kg'),('I084','Green peas',1000,'kg'),('I085','Hakka noodles',1000,'kg'),('I086','Honey',1000,'kg'),('I087','Ice',1000,'kg'),('I088','Idli',1000,'kg'),('I089','Karela',1000,'kg'),('I090','Khoya',1000,'kg'),('I091','Kiwi',1000,'kg'),('I092','Lauki',1000,'kg'),('I093','Lemon',1000,'kg'),('I094','Lemon juice',1000,'L'),('I095','Lettuce',1000,'kg'),('I096','Macaroni',1000,'kg'),('I097','Maggi masala',1000,'kg'),('I098','Maggi noodles',1000,'kg'),('I099','Maida',1000,'kg'),('I100','Mango juice',1000,'L'),('I101','Masoor dal',1000,'kg'),('I102','Matki',1000,'kg'),('I103','Matki sprouts',1000,'kg'),('I104','Mayonnaise',1000,'kg'),('I105','Methi leaves',1000,'kg'),('I106','Milk',1000,'L'),('I107','Minced chicken',1000,'kg'),('I108','Mint chutney',1000,'kg'),('I109','Mint leaves',1000,'kg'),('I110','Moong dal',1000,'kg'),('I111','Mushroom',1000,'kg'),('I112','Mustard oil',1000,'L'),('I113','Mustard seeds',1000,'kg'),('I114','Navy beans',1000,'kg'),('I115','Oil',1000,'L'),('I116','Onion',1000,'kg'),('I117','Orange juice',1000,'L'),('I118','Paneer',1000,'kg'),('I119','Papad',1000,'kg'),('I120','Papadi',1000,'kg'),('I121','Papaya',1000,'kg'),('I122','Papdi',1000,'kg'),('I123','Parsley',1000,'kg'),('I124','Pasta',1000,'kg'),('I125','Pav',1000,'kg'),('I126','Pav bhaji masala',1000,'kg'),('I127','Peanut paste',1000,'kg'),('I128','Peanuts',1000,'kg'),('I129','Pickle',1000,'kg'),('I130','Pickled vegetables',1000,'kg'),('I131','Pineapple',1000,'kg'),('I132','Pineapple juice',1000,'L'),('I133','Poha',1000,'kg'),('I134','Pomegranate seeds',1000,'kg'),('I135','Potato',1000,'kg'),('I136','Puffed rice',1000,'kg'),('I137','Radish',1000,'kg'),('I138','Raisins',1000,'kg'),('I139','Rajma',1000,'kg'),('I140','Red cabbage',1000,'kg'),('I141','Red chili powder',1000,'kg'),('I142','Red curry paste',1000,'kg'),('I143','Rice',1000,'kg'),('I144','Rice flour',1000,'kg'),('I145','Ridge gourd',1000,'kg'),('I146','Sabudana',1000,'kg'),('I147','Saffron',1000,'kg'),('I148','Salt',1000,'kg'),('I149','Sambar masala',1000,'kg'),('I150','Samosa',1000,'kg'),('I151','Schezwan sauce',1000,'kg'),('I152','Semolina',1000,'kg'),('I153','Sev',1000,'kg'),('I154','Snake gourd',1000,'kg'),('I155','Soya chunks',1000,'kg'),('I156','Soya granules',1000,'kg'),('I157','Soya sauce',1000,'kg'),('I158','Spinach',1000,'kg'),('I159','Split green moong dal',1000,'kg'),('I160','Spring onion',1000,'kg'),('I161','Sugar',1000,'kg'),('I162','Tamarind',1000,'kg'),('I163','Tamarind chutney',1000,'kg'),('I164','Tamarind paste',1000,'kg'),('I165','Tea leaves',1000,'kg'),('I166','Tendli',1000,'kg'),('I167','Tomato',1000,'kg'),('I168','Toor dal',1000,'kg'),('I169','Tulsi leaves',1000,'kg'),('I170','Turmeric',1000,'kg'),('I171','Urad dal',1000,'kg'),('I172','Vada',1000,'kg'),('I173','Vermicelli',1000,'kg'),('I174','Vinegar',1000,'L'),('I175','Water',1000,'L'),('I176','Watermelon',1000,'kg'),('I177','Wheat flakes',1000,'kg'),('I178','Wheat flour',1000,'kg'),('I179','Whole masoor dal',1000,'kg'),('I180','Yellow moong dal',1000,'kg'),('I181','Yogurt',1000,'kg');
/*!40000 ALTER TABLE `ingredient_inventory` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-16  7:58:39
