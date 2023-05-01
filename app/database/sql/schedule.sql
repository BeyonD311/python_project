CREATE TABLE IF NOT EXISTS schedule(
    id bigint not null primary key auto_increment,
    queue_name VARCHAR(60) NOT NULL
    `beginning` DATE NOT NULL,
    `ending` DATE NOT NULL,
    active BOOLEAN DEFAULT false,
    stop_queue VARCHAR(60) DEFAULT NULL,
    period_schedule JSON DEFAULT NULL,
    CONSTRAINT `queue_name_fk` 
    FOREIGN KEY (queue_name) 
    REFERENCES queues(`name`) 
    ON DELETE CASCADE 
    ON UPDATE CASCADE
);