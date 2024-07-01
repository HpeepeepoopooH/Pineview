import sqlite3
from werkzeug.security import generate_password_hash

# Connect to the database (it will create the database if it doesn't exist)
connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Add sample users
cur.execute('''
    INSERT INTO users (first_name, last_name, email, username, password, account_type)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('Admin', 'User', 'admin@example.com', 'admin', generate_password_hash('superuserpassword'), 'superuser'))

# Add sample products
# Remove the image field from sample products data
products = [
    ('Apple', 'Fruit', 1.5, 100, 'Fresh red apples', '2023-01-01', 'Yes', 'apple.webp'),
    ('Banana', 'Fruit', 0.5, 200, 'Sweet bananas', '2023-01-02', 'Yes', 'banana.jpeg'),
    ('Orange', 'Fruit', 1.0, 120, 'Juicy oranges', '2023-01-07', 'Yes', 'orange.jpeg'),
    ('Strawberry', 'Fruit', 2.0, 60, 'Sweet strawberries', '2023-01-09', 'Yes', 'strawberry.jpeg'),
    ('Grapes', 'Fruit', 3.0, 50, 'Fresh grapes', '2023-01-03', 'Yes', 'grapes.jpeg'),
    ('Broccoli', 'Vegetable', 1.5, 70, 'Fresh broccoli', '2023-01-04', 'No', 'broccoli.webp'),
    ('Carrot', 'Vegetable', 0.8, 150, 'Fresh carrots', '2023-01-05', 'No', 'carrot.jpeg'),
    ('Sweet potato', 'Vegetable', 1.0, 90, 'Fresh spinach', '2023-01-08', 'Yes', 'sweet-potato.jpeg'),
    ('White cabbage', 'Vegetable', 1.2, 100, 'Juicy tomatoes', '2023-01-10', 'Yes', 'white-cabbage.jpeg'),
    ('Walnuts', 'Dried Fruit', 12.0, 25, 'Fresh walnuts', '2023-01-12', 'Yes', 'walnuts.jpg'),
    ('Dates', 'Dried Fruit', 15.0, 40, 'Sweet dates', '2023-01-13', 'Yes', 'dates.jpeg'),
    ('Raisins', 'Dried Fruit', 8.0, 60, 'Delicious raisins', '2023-01-14', 'Yes', 'raisins.png'),
    ('Prunes', 'Dried Fruit', 9.0, 20, 'Healthy prunes', '2023-01-15', 'Yes', 'prunes.jpg'),
    ('Cinnamon', 'Spice', 5.0, 100, 'Aromatic cinnamon', '2023-01-16', 'Yes', 'cinnamon.jpeg'),
    ('Pepper', 'Spice', 4.0, 120, 'Fresh black pepper', '2023-01-17', 'Yes', 'pepper.jpeg'),
    ('Turmeric', 'Spice', 6.0, 80, 'Golden turmeric', '2023-01-18', 'Yes', 'tumeric.jpeg')
]


# Update the insert statement to match the new schema
for product in products:
    cur.execute('''
        INSERT INTO products (name, type, price, quantity, description, date_added, organic, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', product)


# Add a sample newsletter email
cur.execute('''
    INSERT INTO newsletter_emails (email)
    VALUES (?)
''', ('test@example.com',))

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Database initialized and admin user created.")
