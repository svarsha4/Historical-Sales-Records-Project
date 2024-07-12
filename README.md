
<!-- README.md is generated from README.Rmd. Please edit that file -->

# Data Mart for Historical Sales Records Data

## By: Saul Varshavsky


### Sources

ChatGPT

https://youtu.be/98P9miPwttE?si=s0ShMl_9gAtcVZ8Q 

https://youtu.be/pGjQJmX_IfM?si=AO8-1x2eAVsRZ6fK 

https://youtu.be/btjBNKP49Rk?si=HK_BK3P4tQVq6VMi 

https://youtu.be/ryWCD00nLvQ?si=Pjos3PFJQVIKcow6

https://monkeylearn.com/blog/data-cleaning-techniques/

https://youtu.be/bDhvCp3_lYw?si=6ztk00S_tz41J6Lw

https://youtu.be/GFQaEYEc8_8?si=-KfxjSJIzy6KMW01

https://youtu.be/VWnKUKH4tLg?si=s-Ecjgc0N6luQAvM

https://youtu.be/JYZPdU5F2iM?si=PEIaC6xuwJ3wkHg1


<!-- badges: start -->
<!-- badges: end -->

### Project Description

This project aimed to create a data mart in order to prevent data anomalies and obtain relevant information
from a company's historical records sales data. 


### Process

The following steps have been implemented for this project:

1) Loading the csv file historical_orders.csv (i.e. historical sales records data) into a pandas dataframe
2) Doing any necessary cleaning of the historical sales records data once it was stored in a pandas dataframe, 
which involved the following: removing duplicates, ensuring data consistency, making sure each of the variables/columns
are of appropriate data types, and checking for any missing values
3) Designing an ERD to determine the appropriate design for the data mart; specifically, the ERD expressed the historical sales records data
in Boyce-Codd Normal Form, because Boyce-Codd Normal Form generally helps prevent the main data anomalies and tends to ensure data integrity
4) Creating the data mart using SQLite
5) Loading the clean historical sales records data from the pandas dataframe into the data mart
6) Querying the historical sales records data from the data mart to obtain relevant information


### Requirements to Use the Code

The following commands have been used for installing all the packages used
for this code (installed in Python 3.11.6):

1) pip install pandas
2) pip install tabulate
3) pip install sqlite3

Note, before installing these packages, make sure you perform the following steps in Git to activate your virtual environment
in your project directory:

1) cd path/to/your/project (only needed if the IDE isn't initially set to your project directory)
2) python -m venv venv
3) .\\venv\\Scripts\\activate
