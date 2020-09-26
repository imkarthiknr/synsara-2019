-- phpMyAdmin SQL Dump
-- version 4.1.14
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: Aug 17, 2019 at 03:41 PM
-- Server version: 5.6.17
-- PHP Version: 5.5.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `synsara`
--

-- --------------------------------------------------------

--
-- Table structure for table `userdetail`
--

CREATE TABLE IF NOT EXISTS `userdetail` (
  `id` int(30) NOT NULL AUTO_INCREMENT,
  `master_id` int(10) NOT NULL,
  `event_name` varchar(80) DEFAULT NULL,
  `abstract` varchar(80) DEFAULT NULL,
  `comments` blob,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `usermaster`
--

CREATE TABLE IF NOT EXISTS `usermaster` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `reg_no` varchar(20) NOT NULL,
  `name` varchar(80) NOT NULL,
  `college` varchar(80) NOT NULL,
  `degree` varchar(40) NOT NULL,
  `yr` varchar(10) NOT NULL,
  `mobile` int(12) NOT NULL,
  `email` varchar(120) NOT NULL,
  `pswrd` varchar(40) NOT NULL,
  `comments` blob NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `reg_no` (`reg_no`),
  UNIQUE KEY `mobile` (`mobile`,`email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
