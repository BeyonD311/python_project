INSERT INTO public.status_users (id, "name",color,code,behavior,alter_name,life_time) VALUES
	 (1,'Предварительная обработка','danger','precall','call','Входящий звонок',NULL),
	 (2,'Ожидание ответа абонента','danger','callwaiting','busy',NULL,NULL),
	 (3,'Обратный вызов','danger','callback','busy',NULL,NULL),
	 (4,'Разговор с абонентом','danger','externalcall','busy','Занят',NULL),
	 (5,'Разговор между операторами','danger','internalcall','busy','Занят',NULL),
	 (6,'Разговор по задаче','danger','taskcall','busy','Занят',NULL),
	 (7,'Поствызывная обработка','danger','aftercall','aftercall',NULL,NULL),
	 (8,'Прочие разговоры','danger','othercall','busy',NULL,NULL),
	 (9,'Перерыв','warning','break','break','Перерыв',NULL),
	 (10,'Готов','success','ready','ready','Доступен',NULL),
	 (11,'Ручной режим коллцентра',NULL,'manualcallcenter','call',NULL,NULL),
	 (12,'Обратный вызов из текстовой задачи',NULL,'taskcallback','call',NULL,NULL),
	 (13,'Обработка текстовой задачи',NULL,'taskprocessing','call',NULL,NULL),
	 (14,'Недоступен','disabled','unavailable','offline','Оффлайн',NULL),
	 (15,'Нерабочее время','disabled','offline','offline','Оффлайн',NULL),
	 (16,'Уволен','disabled','dismiss','dismiss','Уволен',NULL),
	 (17,'Завершение разговора',NULL,'hangup','hangup',NULL,NULL),
	 (18,'Авторизация в системе',NULL,'auth','auth',NULL,NULL),
	 (19,'Перерыв на обед','warning','break_lunch','break','Обед','01:00:00'),
	 (20,'Перерыв на туалет','warning','break_toilet','break','Туалет','00:20:00'),
	 (21,'Перерыв на обучение','warning','break_training','break','Обучение','00:45:00');