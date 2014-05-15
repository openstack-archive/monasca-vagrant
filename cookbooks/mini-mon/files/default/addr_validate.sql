CREATE DATABASE IF NOT EXISTS `addr_validate` DEFAULT CHARACTER SET latin1;
USE `addr_validate`;

DROP TABLE IF EXISTS `address_blacklist`;
CREATE TABLE `address_blacklist` (
  `name` varchar(100) NOT NULL,
  `type` enum('SMS','EMAIL') NOT NULL,
  `comment` varchar(256) NOT NULL,
  PRIMARY KEY (`name`,`type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `limits`;
CREATE TABLE `limits` (
  `tenant_id` varchar(64) NOT NULL,
  `max_addresses` int(11) DEFAULT NULL,
  `max_outstanding_requests` int(11) DEFAULT NULL,
  PRIMARY KEY (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `requests`;
CREATE TABLE `requests` (
  `id` varchar(36) NOT NULL,
  `address` varchar(128) DEFAULT NULL,
  `type` enum('EMAIL','SMS') DEFAULT NULL,
  `state` enum('in-progress','timed-out','verified') DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `tenant_id` varchar(64) DEFAULT NULL,
  `token` varchar(128) DEFAULT NULL,
  `name` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `schema_migrations`;
CREATE TABLE `schema_migrations` (
  `version` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  UNIQUE KEY `unique_schema_migrations` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
