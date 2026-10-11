USE customer_data;

CREATE TABLE IF NOT EXISTS customers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  classification VARCHAR(20) NOT NULL
);

INSERT INTO customers (first_name, last_name, email, classification) VALUES
  ('Sample', 'Customer-A', 'sample-a@example.invalid', 'SYNTHETIC'),
  ('Sample', 'Customer-B', 'sample-b@example.invalid', 'SYNTHETIC'),
  ('Sample', 'Customer-C', 'sample-c@example.invalid', 'SYNTHETIC');

