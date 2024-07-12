#Imports
import pandas as pd
from datetime import datetime
from tabulate import tabulate
import sqlite3

#Pandas data frame to be used for extracting the csv file
df = pd.read_csv('D:\\Historical_Sales_Records\\historical_orders.csv')
print(df)  #224 rows in total

#Removes any duplicate rows in this pandas dataframe
df = df.drop_duplicates()
print(df)  #still 224 rows in total which indicates that there aren't any duplicates in the data

#Used filters in Excel to see if there is any data that is inconsistent 
#(e.g. a date in the format ####-##-## would be inconsistent with the format ##/##/#### specified in the order_date column)
#The column order_total has a little data inconsistency, since there are several values with one decimal point, which is not how cost tends
#to be represented. Instead, cost is usually represented with two decimal points (e.g. 349.9 should instead be expressed as 349.90)
df['order_total'] = df['order_total'].apply(lambda x: f"{x:.2f}")

#Checking to see if the row with the value 349.9 (as stated in the example above) gets changed to 349.90
print(df.iloc[106])  #indeed, the value 349.9 now becomes 349.90 in this example

#Now, let's make sure all the variables have the appropriate data types
print(df.dtypes)

#Currently, the variables order_id and postal_code are integer types, but it's best to have them be strings
df['postal_code'] = df['postal_code'].astype(str)
df['order_id'] = df['order_id'].astype(str)
print(df.dtypes)

#The variable order_total should not be an object, but rather a float
df['order_total'] = df['order_total'].astype(float)
print(df.dtypes)

#Finally, let's make sure there isn't any missing data
print(df.isnull())  #appears that there are no missing values at all in this dataframe

#Now that the data has been cleaned, let's use Boyce-Codd Normal Form to construct an ERD pertaining to the dataframe.
#Boyce-Codd Normal Form is generally effective, because it helps prevent the main data anomalies: insertion, update, and deletion

#First, let's determine all the functional dependencies that can be deciphered from the dataframe:
#(first_name, last_name) -> (date_of_birth, phone, email)  *Each person has a unique date of birth, phone, and email
#phone -> (first_name, last_name)   *A given phone number can identify or contact a given person
#email -> (first_name, last_name)  *A given email is also another means to contact a given person
#(street, city, state) -> postal_code  *A street is located in a city, which is located in a state and has a postal code associated with it.
#Because there can be several streets and cities with the same names, it is why together the street, city, and state must be used to determine
#the postal code.
#(street, city, state) -> (first_name, last_name)  *A given address can specifically identify where a given person lives
#product_name -> price  *A given product will have a certain price tag
#Now, using the functional dependencies determined above, we can then create an ERD that reflects these dependencies.
#The ERD is created in the Draw.io file titled historical_sales_records_ERD.


#Setting up sqlite
db_file = 'Historical_Sales_Records_Data_Mart.db'  #The SQL database gets converted into a file
conn = sqlite3.connect(db_file)
curr = conn.cursor()

#Dropping all the tables before creating new ones (to ensure everything is up to date)
tables_to_drop = ['Address_History', 'Contact_Info', 'Customers', 'Products', 'Orders']

for table in tables_to_drop:
    drop_table_query = f"DROP TABLE IF EXISTS {table};"
    curr.execute(drop_table_query)
    conn.commit()

curr.execute("PRAGMA foreign_keys = ON;")


#Now, let's define the actual tables determined from the ERD
address_history_table = """
CREATE TABLE IF NOT EXISTS Address_History (
    address_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    street TEXT, 
    city TEXT, 
    state TEXT, 
    postal_code TEXT, 
    start_date DATE,
    end_date DATE
);
"""
curr.execute(address_history_table)

contact_info_table = """
CREATE TABLE IF NOT EXISTS Contact_Info (
    contact_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    phone TEXT, 
    email TEXT, 
    address_id INTEGER, 
    FOREIGN KEY (address_id) REFERENCES Address_History(address_id)
);
"""
curr.execute(contact_info_table)

customers_table = """
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT, 
    date_of_birth DATE, 
    contact_id INTEGER, 
    FOREIGN KEY (contact_id) REFERENCES Contact_Info(contact_id)
);
"""
curr.execute(customers_table)

products_table = """
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    product_name TEXT, 
    price REAL
);
"""
curr.execute(products_table)

orders_table = """
CREATE TABLE IF NOT EXISTS Orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    order_date DATE, 
    order_status INTEGER, 
    customer_id INTEGER, 
    product_id INTEGER, 
    quantity INTEGER, 
    order_total REAL, 
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id), 
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
"""
curr.execute(orders_table)

conn.commit()

#With the data tables now created, the data from the csv file (which is now a pandas dataframe) can be inserted into the tables

#In order to accomplish this, we first need to specify which columns from the original pandas dataframe should go in which table
#we've defined earlier, as well as any new columns not specified in the original dataframe (e.g. order_status).
#Then, we make sure to convert those columns from the dataframe into SQL format, so that the data can be understood by the sqlite data tables we've
#defined earlier.
df_address_history = pd.DataFrame({
    'street': df['street'], 
    'city': df['city'], 
    'state': df['state'],
    'postal_code': df['postal_code'],
    'start_date': datetime(2015, 1, 1),  #assumption since not enough information is provided
    'end_date': datetime(2024, 1, 1)   #assumption since not enough information is provided
})
df_address_history.to_sql('Address_History', conn, if_exists='append', index=False)
conn.commit() 

df_contact_info = pd.DataFrame({
    'phone': df['phone'], 
    'email': df['email'], 
    'address_id': range(1, len(df_address_history)+1)  #Assuming the id foreign key goes from 1 to the index of the last row, since there is not enough information provided
})
df_contact_info.to_sql('Contact_Info', conn, if_exists='append', index=False)
conn.commit()

df_customers = pd.DataFrame({
    'first_name': df['first_name'], 
    'last_name': df['last_name'], 
    'date_of_birth': df['date_of_birth'], 
    'contact_id': range(1, len(df_contact_info)+1)
})
df_customers.to_sql('Customers', conn, if_exists='append', index=False)
conn.commit()

df_products = pd.DataFrame({
    'product_name': df['product_name'], 
    'price': df['price']
})
df_products.to_sql('Products', conn, if_exists='append', index=False)
conn.commit()

df_orders = pd.DataFrame({
    'order_date': df['order_date'], 
    'order_status': True,    #assumption since not enough information is provided
    'customer_id': range(1, len(df_customers)+1), 
    'product_id': range(1, len(df_products)+1), 
    'quantity': df['quantity'], 
    'order_total': df['order_total']
})
df_orders.to_sql('Orders', conn, if_exists='append', index=False)
conn.commit()

#Verifies to make sure the appropriate data was inserted into each of the tables
def display_table_data(query, table_name):
    curr.execute(query)
    rows = curr.fetchall()
    col_names = [desc[0] for desc in curr.description]
    print(f"\nData from {table_name} table:")
    if rows:
        print(tabulate(rows, headers=col_names, tablefmt='grid'))
    else:
        print("No data found.")

queries = {
    "Address_History": "SELECT * FROM Address_History;",
    "Contact_Info": "SELECT * FROM Contact_Info;",
    "Customers": "SELECT * FROM Customers;",
    "Products": "SELECT * FROM Products;",
    "Orders": "SELECT * FROM Orders;"
}

for table_name, query in queries.items():
    display_table_data(query, table_name)

#With the data now inserted from the pandas dataframe into their appropriate tables using sqlite, we can now 
#gather important insight from the data.

#1) Total numbers of orders shipped to a specific state in a given year

#A query needs to be designed to retireve the relevant information from the data
query1 = """
SELECT COUNT(o.order_id) AS total_orders, ah.state, o.order_date
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
JOIN Contact_Info ci ON c.contact_id = ci.contact_id
JOIN Address_History ah ON ci.address_id = ah.address_id
GROUP BY ah.state, o.order_date;
"""

curr.execute(query1)
conn.commit()
rows = curr.fetchall()
#Even though only data pertaining to the Orders and Address_History tables is displayed, the Customers and Contact_Info
#tables must be joined in order to connect the Orders and Address_History tables together.
#In other words, the Orders and Address_History tables are connected to each other through the Customers and
#Contact_Info tables.

df_query1 = pd.read_sql_query(query1, conn)
print(df_query1)

#2) Retrieval of all customers' current addresses

query2 = """
SELECT c.first_name, c.last_name, ah.street, ah.city, ah.state, ah.postal_code
FROM Customers c
JOIN Contact_Info ci ON c.contact_id = ci.contact_id
JOIN Address_History ah ON ci.address_id = ah.address_id;
"""
curr.execute(query2)
conn.commit()
rows = curr.fetchall()
df_query2 = pd.read_sql_query(query2, conn)
print(df_query2)

#3) Display of all orders and their order statuses

query3 = """
SELECT c.first_name, c.last_name, p.product_name, o.order_date, o.order_status
FROM Orders o
JOIN Products p ON o.product_id = p.product_id
JOIN Customers c ON o.customer_id = c.customer_id;
"""
curr.execute(query3)
conn.commit()
rows = curr.fetchall()
df_query3 = pd.read_sql_query(query3, conn)
print(df_query3)

#4) Identifying customers who did not place orders in certain years

query4 = """
SELECT c.first_name, c.last_name
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
WHERE order_status = 0;
"""
curr.execute(query4)
conn.commit()
rows = curr.fetchall()
df_query4 = pd.read_sql_query(query4, conn)
print(df_query4)
#Nothing actually gets returned, because order_status is 1 (True) by default.

#5) Quarterly sales at the customer level

query5 = """
SELECT c.first_name, c.last_name, SUM(o.order_total) AS sales
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
GROUP BY c.first_name, c.last_name;
"""
#This assumes that the quarterly sales specifically pertains to the sales associated with orders from this csv file

curr.execute(query5)
conn.commit()
rows = curr.fetchall()
df_query5 = pd.read_sql_query(query5, conn)
print(df_query5)

#6) Quarterly sales at the product level

query6 = """
SELECT p.product_name, SUM(o.order_total) AS sales
FROM Orders o
JOIN Products p ON o.product_id = p.product_id
GROUP BY p.product_name;
"""
curr.execute(query6)
conn.commit()
rows = curr.fetchall()
df_query6 = pd.read_sql_query(query6, conn)
print(df_query6)

#Make sure to close the connection to the SQL database after using it
curr.close()
conn.close()
