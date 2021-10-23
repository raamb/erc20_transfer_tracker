ALTER TABLE `agix_balances` 
ADD COLUMN `balance_sub_type` VARCHAR(45) NULL AFTER `balance_type`;

ALTER TABLE `agix_balances` 
ADD COLUMN `balance_type` VARCHAR(45) NULL AFTER `balance_in_cogs`,
DROP INDEX `address_UNIQUE` ,
ADD UNIQUE INDEX `address_balance_type_UNIQUE` (`wallet_address` ASC, `balance_type` ASC, `balance_sub_type` ASC) VISIBLE;

update `agix_balances` set `balance_type` = 'BALANCE', `balance_sub_type` = 'BALANCE';

ALTER TABLE `agix_balances` 
CHANGE COLUMN `balance_in_cogs` `amount` BIGINT NULL DEFAULT NULL ;

ALTER TABLE `agix_transfers` 
CHANGE COLUMN `amount_in_cogs` `amount` BIGINT NULL DEFAULT NULL ;

ALTER TABLE `agix_snapshot` 
CHANGE COLUMN `balance_in_cogs` `amount` BIGINT NULL DEFAULT NULL ;

ALTER TABLE `agix_balances` 
ADD COLUMN `context` varchar(1024) DEFAULT NULL AFTER `block_number`;

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
  `context` varchar(1024) DEFAULT NULL,  
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `address_balance_type_UNIQUE` (`wallet_address`, `balance_type`, 'balance_sub_type')
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


CREATE TABLE `uniswap_v2_tracker` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `contract_address` varchar(45) NOT NULL,
  `pool_name` varchar(45) NOT NULL,
  `block_number` bigint DEFAULT NULL,
  `snapshot_timestamp` timestamp NOT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `address_UNIQUE` (`contract_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

insert into uniswap_v2_tracker (contract_address, pool_name, block_number, snapshot_timestamp, row_created, row_updated)
values ('0x424485f89ea52839fdB30640Eb7DD7E0078E12fb','SDAO-WETH', 12386790, current_timestamp, current_timestamp, current_timestamp);

insert into uniswap_v2_tracker (contract_address, pool_name, block_number, snapshot_timestamp, row_created, row_updated)
values ('0xe45b4a84e0ad24b8617a489d743c52b84b7acebe','AGIX-WETH', 12561147, current_timestamp, current_timestamp, current_timestamp);

insert into uniswap_v2_tracker (contract_address, pool_name, block_number, snapshot_timestamp, row_created, row_updated)
values ('0x3a925503970d40d36d2329e3846e09fcfc9b6acb','SDAO-USDT', 12781399, current_timestamp, current_timestamp, current_timestamp);

insert into uniswap_v2_tracker (contract_address, pool_name, block_number, snapshot_timestamp, row_created, row_updated)
values ('0x4bb0925fa50da9b4c8936869433b48e78ccc5c13','AGIX-USDT', 12564792, current_timestamp, current_timestamp, current_timestamp);


CREATE TABLE `job_runs` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `end_block_number` varchar(45) NOT NULL,
  `context` varchar(1054) DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;