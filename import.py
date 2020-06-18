import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL= "postgres://bjwxmuebywiexo:cbb7614809a4bba5aa0a32b18dbef509fed6732c10ca07a2b81dc2dac043d721@ec2-54-211-210-149.compute-1.amazonaws.com:5432/d2n3ohvdkibnt3"
engine = create_engine("postgres://bjwxmuebywiexo:cbb7614809a4bba5aa0a32b18dbef509fed6732c10ca07a2b81dc2dac043d721@ec2-54-211-210-149.compute-1.amazonaws.com:5432/d2n3ohvdkibnt3")
db = scoped_session(sessionmaker(bind=engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
        db.commit()
if __name__ == "__main__":
    main()
