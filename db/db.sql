CREATE TABLE `challenges` (
  `id` int(255) NOT NULL,
  `CHname` varchar(255) NOT NULL,
  `CHpoint` int(255) NOT NULL,
  `CHhint` varchar(255) NOT NULL,
  `CHlink` varchar(255) DEFAULT NULL,
  `CHfile` varchar(255) DEFAULT NULL,
  `CHcategory` varchar(255) NOT NULL,
  `CHstatus` varchar(255) NOT NULL DEFAULT 'OFF',
  `adminName` varchar(255) NOT NULL,
  `CHlevel` varchar(255) DEFAULT NULL,
  `CHtimestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
ALTER TABLE challenges MODIFY adminName VARCHAR(255) COLLATE utf8mb4_general_ci;

CREATE TABLE `COMPEINFO` (
  `compe_id` int(11) NOT NULL,
  `time_start` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `time_end` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`compe_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `solvedchallenges` (
  `id` int(11) NOT NULL,
  `userId` int(11) NOT NULL,
  `CHid` int(255) NOT NULL,
  `team_id` int(11) DEFAULT NULL,
  `Time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `userId` (`userId`),
  KEY `CHid` (`CHid`),
  KEY `solvedchallenges_team_fk` (`team_id`),
  CONSTRAINT `fk_solvedchallenges_challenges` FOREIGN KEY (`CHid`) REFERENCES `challenges` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_solvedchallenges_team` FOREIGN KEY (`team_id`) REFERENCES `Team` (`Teamid`) ON DELETE SET NULL,
  CONSTRAINT `fk_solvedchallenges_users` FOREIGN KEY (`userId`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `Team` (
  `Teamid` int(11) NOT NULL,
  `leader_id` int(11) DEFAULT NULL,
  `TeamName` varchar(255) NOT NULL,
  PRIMARY KEY (`Teamid`),
  KEY `Team_ibfk_1` (`leader_id`),
  CONSTRAINT `Team_ibfk_1` FOREIGN KEY (`leader_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `UserName` varchar(255) NOT NULL,
  `team_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `team_id` (`team_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `Team` (`Teamid`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;