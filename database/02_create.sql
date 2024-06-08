
-- Таблица roles
INSERT INTO roles (id, name) VALUES
(1, 'user'),
(2, 'admin');


-- Таблица users
INSERT INTO users (email, full_name, username, password, password_reset_token, expiry, role_id) VALUES
('daniel.williams@myorg.com', 'Daniel Williams', 'danielwil', '$2b$12$hjgCihf19pzQZX5oqK2VUub3Rl/gjkebk/K6kfmdldRBMhpA1cJgC', NULL, NOW() + INTERVAL '1 day', 2);

-- Таблица countries
INSERT INTO countries (id, name) VALUES
(1, 'Ukraine'),
(2, 'Germany'),
(3, 'Moldova'),
(4, 'Poland'),
(5, 'Czech Republic'),
(6, 'France'),
(7, 'Spain'),
(8, 'Italy'),
(9, 'United Kingdom'),
(10, 'Turkey'),
(11, 'Netherlands'),
(12, 'Belgium'),
(13, 'Switzerland'),
(14, 'Norway'),
(15, 'Sweden'),
(16, 'Finland'),
(17, 'Denmark'),
(18, 'Ireland'),
(19, 'Greece'),
(20, 'Portugal'),
(21, 'Austria'),
(22, 'Hungary'),
(23, 'Belarus'),
(24, 'Romania'),
(25, 'Bulgaria'),
(26, 'Slovakia'),
(27, 'Croatia'),
(28, 'Bosnia and Herzegovina'),
(29, 'Albania'),
(30, 'Lithuania'),
(31, 'Latvia'),
(32, 'Estonia'),
(33, 'Montenegro'),
(34, 'Luxembourg'),
(35, 'Malta'),
(36, 'Iceland'),
(37, 'United States'),
(38, 'Canada'),
(39, 'Mexico'),
(40, 'China'),
(41, 'India'),
(42, 'Brazil'),
(43, 'South Africa'),
(44, 'Australia'),
(45, 'New Zealand'),
(46, 'Japan'),
(47, 'South Korea'),
(48, 'Indonesia');

-- Таблица employees
UPDATE employees SET
    city = 'None',
    line = 'None',
    postal_code = 'None',
    region = 'None',
    date_of_birth = TO_DATE('2003-05-26', 'YYYY-MM-DD'),
    monday_start = '09:00'::time,
    monday_end = '18:00'::time,
    tuesday_start = '09:00'::time,
    tuesday_end = '18:00'::time,
    wednesday_start = '09:00'::time,
    wednesday_end = '18:00'::time,
    thursday_start = '09:00'::time,
    thursday_end = '18:00'::time,
    friday_start = '09:00'::time,
    friday_end = '18:00'::time,
    saturday_start = NULL,
    saturday_end = NULL,
    sunday_start = NULL,
    sunday_end = NULL,
    mobile_number = 'None',
    profile_file_name = NULL,
    reference = 'None',
    service_start_day = TO_DATE('2021-05-05', 'YYYY-MM-DD'),
    service_end_day = NULL,
    country_id = 4,
    manager_id = NULL
WHERE id = 1;



-- Таблица privilege
INSERT INTO privilege (title, spec_word) VALUES
('Company Year and Creating New', 'year'),
('Departments and Creating New', 'department'),
('Projects and Creating New', 'project'),
('Job Roles and Creating New', 'jobroles'),
('Users and Creating New', 'users');

-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
INSERT INTO role_privileges (role_id, privilege_id)
SELECT r.id AS role_id, p.id AS privilege_id
FROM roles r, privilege p
WHERE r.name = 'admin';

-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
