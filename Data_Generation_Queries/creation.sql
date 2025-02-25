CREATE TABLE `rectureai`.`db_client` (
  `clientId` INT NOT NULL AUTO_INCREMENT,
  `clientName` VARCHAR(45) NOT NULL,
  `clientLicenseKey` VARCHAR(45) NOT NULL,
  `responseAPI` VARCHAR(45) NOT NULL,
  `lectureRouteUrl` VARCHAR(45) NOT NULL,
  `lectureRouteUrlServer` VARCHAR(45) NOT NULL,
  `clientSecertKey` VARCHAR(45) NOT NULL,
  `isActive` INT NOT NULL DEFAULT 0,
  `createdOn` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`clientId`),
  UNIQUE INDEX `clientLicenseKey_UNIQUE` (`clientLicenseKey` ASC) VISIBLE);

  CREATE TABLE `rectureai`.`tbl_packages` (
  `packageId` INT NOT NULL AUTO_INCREMENT,
  `packageTitle` VARCHAR(45) NOT NULL,
  `packageDescription` VARCHAR(45) NULL,
  `packageprice` DECIMAL NOT NULL,
  `packagetypeId` INT NOT NULL,
  PRIMARY KEY (`packageId`));

  CREATE TABLE `rectureai`.`tbl_pacakgetypes` (
  `typeId` INT NOT NULL AUTO_INCREMENT,
  `typedescription` VARCHAR(45) NULL,
  PRIMARY KEY (`typeId`));


CREATE TABLE `rectureai`.`tbl_relation_client_package` (
  `relationId` INT NOT NULL AUTO_INCREMENT,
  `clientId` INT NOT NULL,
  `packageId` INT NOT NULL,
  `total_lectures` INT NOT NULL,
  `remaining_lecture` INT NOT NULL,
  `activation_date` VARCHAR(45) NOT NULL,
  `isactive` INT NOT NULL,
  `createOn` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`relationId`));

  ALTER TABLE `rectureai`.`db_client` 
RENAME TO  `rectureai`.`tbl_client` ;


INSERT INTO `rectureai`.`tbl_client` (`clientName`, `clientLicenseKey`, `responseAPI`, `lectureRouteUrl`, `lectureRouteUrlServer`, `clientSecertKey`, `isActive`, `createdOn`) VALUES ('Air University', 'SU01-ZCVB-9876', 'https://api/Rest/', 'https://api/Rest/', 'https://api/Rest/', '03334337976', '1', '\"now\"');
INSERT INTO `rectureai`.`tbl_client` (`clientName`, `clientLicenseKey`, `responseAPI`, `lectureRouteUrl`, `lectureRouteUrlServer`, `clientSecertKey`, `isActive`, `createdOn`) VALUES ('Bahria University', 'BU01-ZCVB-9876', 'https://api/Rest/', 'https://api/Rest/', 'https://api/Rest/', '03028988075', '0', '\"yesterday\"');

INSERT INTO `rectureai`.`tbl_pacakgetypes` (`typedescription`) VALUES ('Basic');
INSERT INTO `rectureai`.`tbl_pacakgetypes` (`typedescription`) VALUES ('Standard');
INSERT INTO `rectureai`.`tbl_pacakgetypes` (`typedescription`) VALUES ('Premium');


INSERT INTO `rectureai`.`tbl_packages` (`packageTitle`, `packageDescription`, `packageprice`, `packagetypeId`) VALUES ('Default', 'local server', '50', '1');
INSERT INTO `rectureai`.`tbl_packages` (`packageTitle`, `packageDescription`, `packageprice`, `packagetypeId`) VALUES ('Custom', 'custom server', '50', '1');
INSERT INTO `rectureai`.`tbl_packages` (`packageTitle`, `packageDescription`, `packageprice`, `packagetypeId`) VALUES ('Executive', '3rd party api', '100', '1');

INSERT INTO `rectureai`.`tbl_relation_client_package` (`clientId`, `packageId`, `total_lectures`, `remaining_lecture`, `activation_date`, `isactive`, `createOn`) VALUES ('1', '1', '50', '50', '\"now\"', '1', '\"now\"');
INSERT INTO `rectureai`.`tbl_relation_client_package` (`clientId`, `packageId`, `total_lectures`, `remaining_lecture`, `activation_date`, `isactive`, `createOn`) VALUES ('1', '2', '50', '40', '\"now\"', '1', '\"now\"');
INSERT INTO `rectureai`.`tbl_relation_client_package` (`clientId`, `packageId`, `total_lectures`, `remaining_lecture`, `activation_date`, `isactive`, `createOn`) VALUES ('1', '3', '100', '0', '\"now\"', '0', '\"now\"');
