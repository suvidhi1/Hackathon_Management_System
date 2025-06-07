CREATE TABLE Hackathons (
    hackathon_id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('Open', 'Closed') DEFAULT 'Open'
);
