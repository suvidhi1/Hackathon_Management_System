DELIMITER //

CREATE TRIGGER before_insert_hackathons
BEFORE INSERT ON Hackathons
FOR EACH ROW
BEGIN
    IF NEW.end_date < NEW.start_date THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End date cannot be earlier than start date.';
    END IF;
    IF NEW.end_date < CURDATE() THEN
        SET NEW.status = 'Closed';
    ELSE
        SET NEW.status = 'Open';
    END IF;
END;
//

CREATE TRIGGER before_update_hackathons
BEFORE UPDATE ON Hackathons
FOR EACH ROW
BEGIN
    IF NEW.end_date < NEW.start_date THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'End date cannot be earlier than start date.';
    END IF;
    IF NEW.end_date < CURDATE() THEN
        SET NEW.status = 'Closed';
    ELSE
        SET NEW.status = 'Open';
    END IF;
END;
//
DELIMITER ;
