CREATE TABLE `wave_midjourney_stage_result` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `trigger_id` varchar(128) NOT NULL COMMENT 'trigger_id for midjourney api',
  `stage` varchar(512) NOT NULL COMMENT 'request收到请求/start开始生成/generating正在生成/end生成完成',
  `pic_url` text DEFAULT NULL COMMENT '图片地址',
  `msg_id` varchar(1024) DEFAULT NULL COMMENT 'discord msg id',
  `msg_hash` varchar(1024) DEFAULT NULL COMMENT 'discord msg hash',
  `video_url` text DEFAULT NULL COMMENT '视频地址',
  `token` varchar(256) DEFAULT NULL COMMENT '请求验证token',
  `updated_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) ON UPDATE CURRENT_TIMESTAMP(4) COMMENT '更新时间',
  `created_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`trigger_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='midjourney结果保存表';

CREATE TABLE `wave_midjourney_auth_token` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `token` varchar(256) NOT NULL COMMENT 'trigger_id for midjourney api',
  `rate_limit` int(11) NOT NULL COMMENT 'token维度1s限流值',
  `period` int(11) NOT NULL COMMENT '限流周期, 单位s =10代表10秒内最多rate_limit次请求',
  `effective` smallint(4) NOT NULL COMMENT '是否有效1=有效, 0=无效',
  `expired_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) COMMENT '过期时间',
  `updated_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) ON UPDATE CURRENT_TIMESTAMP(4) COMMENT '更新时间',
  `created_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`token`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='鉴权+限流表';

insert into wave_midjourney_auth_token (token, rate_limit, `period`, effective, expired_at) values ('abc', 3, 10, 1, '2024-12-01 00:00:00');

alter table `wave_midjourney_stage_result` add column `token` varchar(256) DEFAULT NULL COMMENT '请求验证token' after `video_url`;