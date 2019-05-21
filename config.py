url = "https://sourceforge.net/directory/language:java/os:linux/"#可以修改（注：最好该分类下的项目数目不要太大，建议该分类下的English分类的数目小于25000，因为英文是最多的）
item_index_head = 'https://sourceforge.net'
dir_name = '/root/SourceForgelinxjava/data/'#改成你的目录
happy_end = "all works are done!\n" \
            "please remember to check whether any pages went into error in file timeanderror" \
            "you can also check the time this project takes in file timeanderror"

mysql_host = ''
mysql_username = ''
mysql_passwords = ''
mysql_database = ''

table_1 = "CREATE TABLE `briefintro` (`id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id of items'," \
          "`name` varchar(50) DEFAULT NULL COMMENT 'name of items'," \
          "`summary` text COMMENT 'summary of items'," \
          "`Categories` tinytext COMMENT 'categories of items'," \
          "`Licenses` tinytext COMMENT 'Licenses of items'," \
          " PRIMARY KEY (`id`)" \
          ") ENGINE=InnoDB AUTO_INCREMENT=9376 DEFAULT CHARSET=utf8mb4 COMMENT='briefintro about java&Linux on SourceForge';"
table_2 = "CREATE TABLE `userratings` (" \
          "`Id` int(11) NOT NULL AUTO_INCREMENT," \
          "`average` varchar(50) DEFAULT NULL," \
          "`num_of_5stars` varchar(50) DEFAULT NULL," \
          "`num_of_4stars` varchar(50) DEFAULT NULL," \
          "`num_of_3stars` varchar(50) DEFAULT NULL," \
          "`num_of_2stars` varchar(50) DEFAULT NULL," \
          "`num_of_1star` varchar(50) DEFAULT NULL," \
          "`Ease` varchar(50) DEFAULT NULL," \
          "`Features` varchar(50) DEFAULT NULL," \
          "`Design` varchar(50) DEFAULT NULL," \
          "`Support` varchar(50) DEFAULT NULL," \
          " PRIMARY KEY (`Id`)) ENGINE=InnoDB AUTO_INCREMENT=9516 DEFAULT CHARSET=utf8mb4;"
table_3 = "CREATE TABLE `userreviews` (" \
          "`id` int(11) DEFAULT NULL," \
          "`nickname` varchar(50) DEFAULT NULL," \
          "`num_of_stars` int(11) DEFAULT NULL," \
          "`date` varchar(50) DEFAULT NULL," \
          "`review_txt` text," \
          "`helpful_cnt` varchar(50) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"