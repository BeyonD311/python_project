CREATE procedure AddStatusHistory(in time_a INT, uuid_user TEXT, user_c TEXT, source TEXT, destination TEXT, code TEXT, call_time TIME)
BEGIN
	declare input_time TIMESTAMP DEFAULT NULL;
	declare delta_time INT DEFAULT 0;
	declare prev_time TIMESTAMP DEFAULT NULL;
	SET @input_time = from_unixtime(time_a);
	select TIMESTAMPDIFF(SECOND, temp.start_at, temp.end_at) as delta_time , temp.start_at as prev_time
	into @delta_time, @prev_time
	from ( select psh.time_at start_at, @input_time end_at 
			from ps_status_history psh  
			where psh.uuid  = uuid_user ORDER BY psh.time_at DESC limit 1
		) temp;
	update ps_status_history set delta_time = @delta_time where uuid  = uuid_user and time_at = @prev_time;
	INSERT INTO asterisk.ps_status_history (time_at, uuid, src, dst, status_code, call_time, delta_time, user_inner_phone) VALUES 
	(@input_time,uuid_user,source,destination,code,call_time, NULL, user_c);
END

