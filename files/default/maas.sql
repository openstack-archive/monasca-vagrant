CREATE DATABASE IF NOT EXISTS `maas` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `maas`;

SET foreign_key_checks = 0;

DROP TABLE IF EXISTS `access`;
CREATE TABLE `access` (
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `access_type` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`tenant_id`,`access_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `alarm`;
CREATE TABLE `alarm` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `expression` mediumtext COLLATE utf8mb4_unicode_ci,
  `state` enum('UNDETERMINED','OK','ALARM') COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `alarm_action`;
CREATE TABLE `alarm_action` (
  `alarm_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`alarm_id`,`action_id`),
  CONSTRAINT `alarm_action` FOREIGN KEY (`alarm_id`) REFERENCES `alarm` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `audit_api_call_count`;
CREATE TABLE `audit_api_call_count` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `count` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB AUTO_INCREMENT=107928 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `audit_billing`;
CREATE TABLE `audit_billing` (
  `audit_period_beginning` datetime NOT NULL,
  `audit_period_ending` datetime NOT NULL,
  PRIMARY KEY (`audit_period_beginning`,`audit_period_ending`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `audit_metric_post_definitions`;
CREATE TABLE `audit_metric_post_definitions` (
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `hash` varchar(191) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`tenant_id`,`hash`,`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `audit_notifications`;
CREATE TABLE `audit_notifications` (
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('EMAIL','SMS') COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`tenant_id`,`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `endpoint`;
CREATE TABLE `endpoint` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `uri` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tenant_id` (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `endpoint_meta`;
CREATE TABLE `endpoint_meta` (
  `endpoint_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` varchar(300) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`endpoint_id`,`name`),
  CONSTRAINT `endpoint_meta` FOREIGN KEY (`endpoint_id`) REFERENCES `endpoint` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `metering_settings`;
CREATE TABLE `metering_settings` (
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `value` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`tenant_id`,`setting`,`value`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `notification_limit`;
CREATE TABLE `notification_limit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` enum('EMAIL','SMS') COLLATE utf8mb4_unicode_ci NOT NULL,
  `total` int(11) NOT NULL,
  `limit` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `notification_method`;
CREATE TABLE `notification_method` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(250) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` enum('EMAIL','SMS') COLLATE utf8mb4_unicode_ci NOT NULL,
  `address` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `notification_time_limit`;
CREATE TABLE `notification_time_limit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tenant_id` varchar(36) NOT NULL,
  `notifications_per_minute` float NOT NULL,
  `notifications_per_hour` float NOT NULL,
  `notifications_per_day` float NOT NULL,
  `last_updated` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `schema_migrations`;
CREATE TABLE `schema_migrations` (
  `version` varchar(255) NOT NULL,
  UNIQUE KEY `unique_schema_migrations` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `sub_alarm`;
CREATE TABLE `sub_alarm` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `alarm_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `function` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `namespace` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `operator` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `threshold` double NOT NULL,
  `period` int(11) NOT NULL,
  `periods` int(11) NOT NULL,
  `state` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_sub_alarm` (`alarm_id`),
  CONSTRAINT `fk_sub_alarm` FOREIGN KEY (`alarm_id`) REFERENCES `alarm` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `sub_alarm_dimension`;
CREATE TABLE `sub_alarm_dimension` (
  `sub_alarm_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dimension_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `value` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`sub_alarm_id`,`dimension_name`),
  CONSTRAINT `fk_sub_alarm_dimension` FOREIGN KEY (`sub_alarm_id`) REFERENCES `sub_alarm` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `subscription`;
CREATE TABLE `subscription` (
  `id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `tenant_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `endpoint_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `namespace` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `deleted_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `subscription_endpoint` (`endpoint_id`),
  KEY `tenant_id` (`tenant_id`),
  KEY `namespace` (`namespace`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `subscription_endpoint` FOREIGN KEY (`endpoint_id`) REFERENCES `endpoint` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `subscription_dimension`;
CREATE TABLE `subscription_dimension` (
  `subscription_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `dimension_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `value` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`subscription_id`,`dimension_name`),
  CONSTRAINT `subscription_dimension` FOREIGN KEY (`subscription_id`) REFERENCES `subscription` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `subscription_meta`;
CREATE TABLE `subscription_meta` (
  `subscription_id` varchar(36) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
  `value` varchar(300) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`subscription_id`,`name`),
  CONSTRAINT `subscription_meta` FOREIGN KEY (`subscription_id`) REFERENCES `subscription` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET foreign_key_checks = 1;
