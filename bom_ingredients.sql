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
-- Table structure for table `ingredients`
--

DROP TABLE IF EXISTS `ingredients`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ingredients` (
  `ingredient_id` varchar(4) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Meal_Category` enum('Veg','Non-Veg','Jain') NOT NULL,
  PRIMARY KEY (`ingredient_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ingredients`
--

LOCK TABLES `ingredients` WRITE;
/*!40000 ALTER TABLE `ingredients` DISABLE KEYS */;
INSERT INTO `ingredients` VALUES ('I001','Almonds','Veg'),('I002','Anardana powder','Veg'),('I003','Apple','Veg'),('I004','Baby corn','Veg'),('I005','Baby potato','Veg'),('I006','Baking powder','Veg'),('I007','Banana','Veg'),('I008','Bay leaf','Veg'),('I009','Beans','Veg'),('I010','Beetroot','Veg'),('I011','Besan','Veg'),('I012','Bhindi','Veg'),('I013','Black chana','Veg'),('I014','Black pepper','Veg'),('I015','Black-eyed peas','Veg'),('I016','Boondi','Veg'),('I017','Bread','Veg'),('I018','Bread crumbs','Veg'),('I019','Brinjal','Veg'),('I020','Broken wheat','Veg'),('I021','Brown rice','Veg'),('I022','Bulgar wheat','Veg'),('I023','Butter','Veg'),('I024','Cabbage','Veg'),('I025','Capsicum','Veg'),('I026','Cardamom','Veg'),('I027','Carrot','Veg'),('I028','Cashew nuts','Veg'),('I029','Cashew paste','Veg'),('I030','Cauliflower','Veg'),('I031','Chaat masala','Veg'),('I032','Chana dal','Veg'),('I033','Chana masala','Veg'),('I034','Chana sprouts','Veg'),('I035','Chenna','Veg'),('I036','Chicken','Non-Veg'),('I037','Chickpeas','Veg'),('I038','Cinnamon','Veg'),('I039','Cloves','Veg'),('I040','Coconut','Veg'),('I041','Coconut milk','Veg'),('I042','Coffee powder','Veg'),('I043','Coriander leaves','Veg'),('I044','Coriander powder','Veg'),('I045','Coriander seeds','Veg'),('I046','Corn','Veg'),('I047','Corn cob','Veg'),('I048','Corn flakes','Veg'),('I049','Cornflour','Veg'),('I050','Crab meat','Non-Veg'),('I051','Cream','Veg'),('I052','Cucumber','Veg'),('I053','Cumin powder','Veg'),('I054','Cumin seeds','Veg'),('I055','Curd','Veg'),('I056','Curry leaves','Veg'),('I057','Custard powder','Veg'),('I058','Dabeli masala','Veg'),('I059','Dalia','Veg'),('I060','Doodhi','Veg'),('I061','Dried green peas','Veg'),('I062','Dried white peas','Veg'),('I063','Drumstick','Veg'),('I064','Dry red chili','Veg'),('I065','Egg','Non-Veg'),('I066','Eggplant','Non-Veg'),('I067','Eno','Veg'),('I068','Fennel seeds','Veg'),('I069','Fenugreek leaves','Veg'),('I070','Fruit jam','Veg'),('I071','Garam masala','Veg'),('I072','Garlic','Veg'),('I073','Gavar','Veg'),('I074','Gawar','Veg'),('I075','Ghee','Veg'),('I076','Ginger','Veg'),('I077','Green beans','Veg'),('I078','Green black-eyed peas','Veg'),('I079','Green chili','Veg'),('I080','Green chutney','Veg'),('I081','Green curry paste','Veg'),('I082','Green moong dal','Veg'),('I083','Green moong sprouts','Veg'),('I084','Green peas','Veg'),('I085','Hakka noodles','Veg'),('I086','Honey','Veg'),('I087','Ice','Veg'),('I088','Idli','Veg'),('I089','Karela','Veg'),('I090','Khoya','Veg'),('I091','Kiwi','Veg'),('I092','Lauki','Veg'),('I093','Lemon','Veg'),('I094','Lemon juice','Veg'),('I095','Lettuce','Veg'),('I096','Macaroni','Veg'),('I097','Maggi masala','Veg'),('I098','Maggi noodles','Veg'),('I099','Maida','Veg'),('I100','Mango juice','Veg'),('I101','Masoor dal','Veg'),('I102','Matki','Veg'),('I103','Matki sprouts','Veg'),('I104','Mayonnaise','Veg'),('I105','Methi leaves','Veg'),('I106','Milk','Veg'),('I107','Minced chicken','Non-Veg'),('I108','Mint chutney','Veg'),('I109','Mint leaves','Veg'),('I110','Moong dal','Veg'),('I111','Mushroom','Veg'),('I112','Mustard oil','Veg'),('I113','Mustard seeds','Veg'),('I114','Navy beans','Veg'),('I115','Oil','Veg'),('I116','Onion','Veg'),('I117','Orange juice','Veg'),('I118','Paneer','Veg'),('I119','Papad','Veg'),('I120','Papadi','Veg'),('I121','Papaya','Veg'),('I122','Papdi','Veg'),('I123','Parsley','Veg'),('I124','Pasta','Veg'),('I125','Pav','Veg'),('I126','Pav bhaji masala','Veg'),('I127','Peanut paste','Veg'),('I128','Peanuts','Veg'),('I129','Pickle','Veg'),('I130','Pickled vegetables','Veg'),('I131','Pineapple','Veg'),('I132','Pineapple juice','Veg'),('I133','Poha','Veg'),('I134','Pomegranate seeds','Veg'),('I135','Potato','Veg'),('I136','Puffed rice','Veg'),('I137','Radish','Veg'),('I138','Raisins','Veg'),('I139','Rajma','Veg'),('I140','Red cabbage','Veg'),('I141','Red chili powder','Veg'),('I142','Red curry paste','Veg'),('I143','Rice','Veg'),('I144','Rice flour','Veg'),('I145','Ridge gourd','Veg'),('I146','Sabudana','Veg'),('I147','Saffron','Veg'),('I148','Salt','Veg'),('I149','Sambar masala','Veg'),('I150','Samosa','Veg'),('I151','Schezwan sauce','Veg'),('I152','Semolina','Veg'),('I153','Sev','Veg'),('I154','Snake gourd','Veg'),('I155','Soya chunks','Veg'),('I156','Soya granules','Veg'),('I157','Soya sauce','Veg'),('I158','Spinach','Veg'),('I159','Split green moong dal','Veg'),('I160','Spring onion','Veg'),('I161','Sugar','Veg'),('I162','Tamarind','Veg'),('I163','Tamarind chutney','Veg'),('I164','Tamarind paste','Veg'),('I165','Tea leaves','Veg'),('I166','Tendli','Veg'),('I167','Tomato','Veg'),('I168','Toor dal','Veg'),('I169','Tulsi leaves','Veg'),('I170','Turmeric','Veg'),('I171','Urad dal','Veg'),('I172','Vada','Veg'),('I173','Vermicelli','Veg'),('I174','Vinegar','Veg'),('I175','Water','Veg'),('I176','Watermelon','Veg'),('I177','Wheat flakes','Veg'),('I178','Wheat flour','Veg'),('I179','Whole masoor dal','Veg'),('I180','Yellow moong dal','Veg'),('I181','Yogurt','Veg'),('I182','Hot Garlic Paste','Veg'),('I183','Malvani Masala','Veg'),('I184','Kofta Mix','Veg'),('I185','Spring Roll Sheets','Veg'),('I186','Biryani Masala','Veg'),('I187','Khichdi Mix','Veg'),('I188','Shevgyachi Sheng','Veg'),('I200','Fenugreek seeds','Veg'),('I201','Tomato puree','Veg'),('I202','Red chili flakes','Veg'),('I203','Mixed herbs','Veg'),('I204','Brownie Base','Veg'),('I205','Vanilla Ice Cream','Veg'),('I206','Murmura','Veg'),('I207','Sev','Veg'),('I208','Sweet Chutney','Veg'),('I209','Pehadi Masala','Veg'),('I210','Fried Chicken Wing','Non-Veg'),('I211','Cooked Fried Rice Base','Veg'),('I212','Onion Chopped','Veg'),('I213','Tomato Chopped','Veg'),('I214','Mixed Salad Cubes','Veg'),('I215','Farsan Mix','Veg');
/*!40000 ALTER TABLE `ingredients` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-16  7:58:38
