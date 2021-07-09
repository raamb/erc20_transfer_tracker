CREATE TABLE `agix_transfers` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `from_address` varchar(45) DEFAULT NULL,
  `to_address` varchar(45) DEFAULT NULL,
  `amount_in_cogs` bigint DEFAULT NULL,
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

CREATE TABLE `agix_balances` (
  `row_id` int NOT NULL AUTO_INCREMENT,
  `wallet_address` varchar(45) NOT NULL,
  `is_contract` BIT(1) DEFAULT 0,
  `balance_in_cogs` bigint DEFAULT NULL,
  `block_number` bigint DEFAULT NULL,
  `row_created` timestamp NULL DEFAULT NULL,
  `row_updated` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`row_id`),
  UNIQUE KEY `address_UNIQUE` (`wallet_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;