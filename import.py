import os
import csv
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# connection details
engine = create_engine('postgres://hbsswfbyxtdtuz:ce19cc966a963c9f0c06014e99936251f9f949c175397ca77eb9a1a6df8298b9@ec2-54-247-177-254.eu-west-1.compute.amazonaws.com:5432/df9pvk9bfdb4r1')
db = scoped_session(sessionmaker(bind=engine))

def main():
    # open csv and transfer rows to database
    with open('books_small500.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader) # skip first row with column names

        for isbn, title, author, year in reader:
            timestamp = datetime.datetime.now()
            db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", 
                        {"isbn": isbn, "title": title, "author": author, "year": year})
            print(f"Added book: {title}, {isbn}, {author}, {year}")
        db.commit()

if __name__ == "__main__":
    main()