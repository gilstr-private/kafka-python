create schema sandbox collate utf8mb4_general_ci;

create or replace table transaction
(
    ID        int auto_increment
        primary key,
    timestamp timestamp      null,
    type      varchar(32)    null,
    amount    decimal(10, 2) null
);

-- 1. Create the user, if not already existing,
--    allowing connections from any host:
CREATE USER IF NOT EXISTS 'app_user'@'%'
  IDENTIFIED BY '123123';

-- 2. Grant read/write privileges on ALL databases and tables:
GRANT SELECT, INSERT, UPDATE, DELETE
  ON *.*
  TO 'app_user'@'%';

-- 3. (Optional) If you also want the user to create/drop tables:
-- GRANT CREATE, DROP ON *.* TO 'app_user'@'%';

-- 4. Apply changes
FLUSH PRIVILEGES;