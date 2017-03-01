-- phpMyAdmin SQL Dump
-- version 4.1.14
-- http://www.phpmyadmin.net
--
-- Host: 127.0.0.1
-- Generation Time: 2015-12-08 04:53:58
-- 服务器版本： 5.6.17
-- PHP Version: 5.5.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `opensns`
--

-- --------------------------------------------------------

--
-- 表的结构 `news_category`
--

CREATE TABLE IF NOT EXISTS `news_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(20) NOT NULL,
  `pid` int(11) NOT NULL,
  `can_post` tinyint(4) NOT NULL COMMENT '前台可投稿',
  `need_audit` tinyint(4) NOT NULL COMMENT '前台投稿是否需要审核',
  `sort` tinyint(4) NOT NULL,
  `status` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='资讯分类' AUTO_INCREMENT=10 ;

--
-- 转存表中的数据 `news_category`
--

INSERT INTO `news_category` (`id`, `title`, `pid`, `can_post`, `need_audit`, `sort`, `status`) VALUES
(1, '南燕要闻', 0, 0, 0, 1, 1),
(2, '信工', 0, 0, 0, 2, 1),
(3, '汇丰', 0, 1, 1, 3, 1),
(4, '化生', 0, 1, 1, 4, 1),
(5, '环能', 0, 1, 1, 5, 1),
(6, '城规', 0, 1, 1, 6, 1),
(7, '新材料', 0, 1, 1, 7, 1),
(8, '人文', 0, 1, 1, 8, 1),
(9, '国法', 0, 1, 1, 9, 1);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
