CREATE TABLE `wave_midjourney_stage_result` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `trigger_id` varchar(128) NOT NULL COMMENT 'trigger_id for midjourney api',
  `stage` varchar(512) NOT NULL COMMENT 'generating/pic_completed/upscale/upscale_completed/video/video_completed',
  `pic_url` text DEFAULT NULL COMMENT '图片地址',
  `msg_id` varchar(1024) DEFAULT NULL COMMENT 'discord msg id',
  `msg_hash` varchar(1024) DEFAULT NULL COMMENT 'discord msg hash',
  `video_url` text DEFAULT NULL COMMENT '视频地址',
  `updated_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) ON UPDATE CURRENT_TIMESTAMP(4) COMMENT '更新时间',
  `created_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`trigger_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='midjourney结果保存表';

CREATE TABLE `wave_midjourney_auth_token` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '自增主键',
  `token` varchar(256) NOT NULL COMMENT 'trigger_id for midjourney api',
  `rate_limit` int(11) NOT NULL COMMENT 'token维度1s限流值',
  `effective` smallint(4) NOT NULL COMMENT '是否有效1=有效, 0=无效',
  `expired_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) COMMENT '过期时间',
  `updated_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) ON UPDATE CURRENT_TIMESTAMP(4) COMMENT '更新时间',
  `created_at` timestamp(4) NOT NULL DEFAULT CURRENT_TIMESTAMP(4) COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY (`token`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT='鉴权+限流表';

insert into wave_midjourney_auth_token (token, rate_limit, effective, expired_at) values ('abc', 3, 1, '2024-12-01 00:00:00');