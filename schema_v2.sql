ALTER TABLE `agix_balances` 
ADD COLUMN `balance_type` VARCHAR(45) NULL AFTER `balance_in_cogs`,
DROP INDEX `address_UNIQUE` ,
ADD UNIQUE INDEX `address_balance_type_UNIQUE` (`wallet_address` ASC, `balance_type` ASC) VISIBLE;

ALTER TABLE `agix_balances` 
ADD COLUMN `balance_sub_type` VARCHAR(45) NULL AFTER `balance_type`;

update `agix_balances` set `balance_type` = 'BALANCE', `balance_sub_type` = 'BALANCE';

ALTER TABLE `agix_balances` 
CHANGE COLUMN `balance_in_cogs` `amount` BIGINT NULL DEFAULT NULL ;

ALTER TABLE `agix_transfers` 
CHANGE COLUMN `amount_in_cogs` `amount` BIGINT NULL DEFAULT NULL ;

ALTER TABLE `agix_snapshot` 
CHANGE COLUMN `balance_in_cogs` `amount` BIGINT NULL DEFAULT NULL ;

CREATE TABLE `sdao_transfers` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `from_address` varchar(45) DEFAULT NULL,
  `to_address` varchar(45) DEFAULT NULL,
  `amount` varchar(256) DEFAULT NULL,
  `transaction_hash` varchar(256) DEFAULT NULL,
  `block_number` bigint DEFAULT NULL,
  `logIndex` int DEFAULT NULL,
  `transactionIndex` int DEFAULT NULL,
  `raw_event` varchar(1024) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `unique_transaction` (`from_address`,`to_address`,`transaction_hash`),
  UNIQUE KEY `unique_block` (`from_address`,`to_address`,`block_number`,`logIndex`,`transactionIndex`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sdao_balances` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `wallet_address` varchar(45) NOT NULL,
  `is_contract` BIT(1) DEFAULT 0,
  `amount` varchar(256) DEFAULT NULL,
  `balance_type` varchar(45) NOT NULL,
  `balance_sub_type` VARCHAR(45) NULL,
  `block_number` bigint DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `address_balance_type_UNIQUE` (`wallet_address`, `balance_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `sdao_snapshot` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `wallet_address` varchar(45) NOT NULL,
  `is_contract` BIT(1) DEFAULT 0,
  `amount` bigint DEFAULT NULL,
  `block_number` bigint DEFAULT NULL,
  `snapshot_timestamp` timestamp NOT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `address_UNIQUE` (`wallet_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;