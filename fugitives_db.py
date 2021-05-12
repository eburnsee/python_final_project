import psycopg2
import getpass
import csv
from csv import reader

def create_fug_tables():
	"""Creates tables in the database for data to be loaded into"""
	conn=psycopg2.connect(connstring)
	cur=conn.cursor()
	sql1 = """DROP TABLE IF EXISTS fugitives, agencies, haircolors, eyecolors, sexes, races;
				CREATE TABLE agencies (
				agid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
				agencyname VARCHAR(500) NOT NULL
				);
				CREATE TABLE haircolors (
				haid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
				haircolor VARCHAR(500) NOT NULL
				);
				CREATE TABLE eyecolors (
				eid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
				eyecolor VARCHAR(500) NOT NULL
				);
				CREATE TABLE sexes (
				sid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
				sex VARCHAR(500) NOT NULL
				);
				CREATE TABLE races (
				rid INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
				race VARCHAR(500) NOT NULL
				);
				CREATE TABLE fugitives (
				ncic BIGINT PRIMARY KEY,
				lastname VARCHAR(500) NOT NULL,
				firstname VARCHAR(500) NOT NULL,
				middlename VARCHAR(500),
				agid INT REFERENCES agencies (agid) ON DELETE CASCADE,
				url VARCHAR(500) NOT NULL,
				allegation1 VARCHAR(5000),
				allegation2 VARCHAR(5000),
				allegation3 VARCHAR(5000),
				alias1 VARCHAR(500),
				alias2 VARCHAR(500),
				alias3 VARCHAR(500),
				yob INT,
				haid INT REFERENCES haircolors (haid) ON DELETE CASCADE, 
				eid INT REFERENCES eyecolors (eid) ON DELETE CASCADE,
				height INT,
				weight INT,
				sid INT REFERENCES sexes (sid) ON DELETE CASCADE,
				rid INT REFERENCES races (rid) ON DELETE CASCADE,
				note1 VARCHAR(5000),
				note2 VARCHAR(5000),
				note3 VARCHAR(5000)
				);"""
	cur.execute(sql1)
	conn.commit()
	cur.close()
	conn.close()
	print("Tables initialized.\n")
	
def import_fug_csv():
	"""Creates stored procedure for loading data into tables after reading from csv"""
	conn=psycopg2.connect(connstring)
	cur=conn.cursor()
	sql2="""DROP PROCEDURE IF EXISTS addfug;
				CREATE PROCEDURE addfug(
					nc BIGINT,
					ln VARCHAR(500),
					fn VARCHAR(500),
					mn VARCHAR(500),
					wb VARCHAR(500),
					url VARCHAR(500),
					a1 VARCHAR(5000),
					a2 VARCHAR(5000),
					a3 VARCHAR(5000),
					al1 VARCHAR(500),
					al2 VARCHAR(500),
					al3 VARCHAR(500),
					yob INT,
					hc VARCHAR(500),
					ec VARCHAR(500),
					he INT,
					we INT,
					sx VARCHAR(500),
					rc VARCHAR(500),
					n1 VARCHAR(5000),
					n2 VARCHAR(5000),
					n3 VARCHAR(5000)
				)
				AS $$
				DECLARE agidout INT;
				DECLARE haidout INT;
				DECLARE eidout INT;
				DECLARE sidout INT;
				DECLARE ridout INT;

				BEGIN
				IF (SELECT COUNT(*) FROM agencies WHERE agencyname=wb)=1 THEN
						SELECT agid INTO agidout FROM agencies WHERE agencyname=wb; 
					ELSE
						INSERT INTO agencies(agencyname) VALUES (wb);
						SELECT LASTVAL() INTO agidout;
					END IF;

				IF (SELECT COUNT(*) FROM haircolors WHERE haircolor=hc)=1 THEN
						SELECT haid INTO haidout FROM haircolors WHERE haircolor=hc; 
					ELSE
						INSERT INTO haircolors(haircolor) VALUES (hc);
						SELECT LASTVAL() INTO haidout;
					END IF;

				IF (SELECT COUNT(*) FROM eyecolors WHERE eyecolor=ec)=1 THEN
						SELECT eid INTO eidout FROM eyecolors WHERE eyecolor=ec; 
					ELSE
						INSERT INTO eyecolors(eyecolor) VALUES (ec);
						SELECT LASTVAL() INTO eidout;
					END IF;

				IF (SELECT COUNT(*) FROM sexes WHERE sex=sx)=1 THEN
						SELECT sid INTO sidout FROM sexes WHERE sex=sx; 
					ELSE
						INSERT INTO sexes(sex) VALUES (sx);
						SELECT LASTVAL() INTO sidout;
					END IF;

				IF (SELECT COUNT(*) FROM races WHERE race=rc)=1 THEN
						SELECT rid INTO ridout FROM races WHERE race=rc; 
					ELSE
						INSERT INTO races(race) VALUES (rc);
						SELECT LASTVAL() INTO ridout;
					END IF;
				INSERT INTO fugitives
				(ncic, lastname, firstname, middlename, agid, url, allegation1, allegation2, allegation3, alias1, alias2, alias3, yob, haid, eid, height, weight, sid, rid, note1, note2, note3) 
				VALUES 
				(nc, ln, fn, mn, agidout, url, a1, a2, a3, al1, al2, al3, yob, haidout, eidout, he, we, sidout, ridout, n1, n2, n3);
				END; $$
				language plpgsql;"""
	cur.execute(sql2)
	with open('fugitives_file.csv', 'r', encoding="utf8") as fugitives:
		csv_reader = reader(fugitives)
		header=next(csv_reader)
		ncic_list=[]
		for row in csv_reader:
			ncic=row[0]
			if ncic not in ncic_list:
				ncic_list.append(ncic)
			elif ncic in ncic_list:
				continue
			l_name=row[1]
			f_name=row[2]
			m_name=row[3]
			if m_name=='null':
				m_name=None
			agency = row[4]
			url = row[5]
			all_1=row[6]
			all_2=row[7]
			all_3=row[8]
			ali_1=row[9]
			ali_2=row[10]
			ali_3=row[11]
			yob=row[12]
			if yob == 'null':
				continue
			hair=row[13]
			if hair == 'null':
				continue
			eye=row[14]
			if eye == 'null':
				continue
			height=row[15]
			if (height == 'null') or (height == "' \"") or (height == "0' 0\""):
				continue
			if height == "6' \"":
				height = "6"
			weight=row[16]
			if weight == 'null':
				continue
			sex=row[17]
			if sex == 'null':
				continue
			race=row[18]
			if race == "null":
				continue
			note_1=row[19]
			note_2=row[20]
			note_3=row[21]
			print("Read: " + f_name +" "+ l_name + " " + ncic)	
			cur.execute('CALL addfug(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (ncic, l_name, f_name, m_name, agency, url, all_1, all_2, all_3, ali_1, ali_2, ali_3, yob, hair, eye, height, weight, sex, race, note_1, note_2, note_3));
	conn.commit()
	cur.close()
	conn.close()

def main():
	'''Menu for user to choose the options create and fill the tables'''
	while True:
		print("Choose what you would like to do:")
		print("Enter 1 to initialize the table.")
		print("Enter 2 to import csv.")
		print("Enter 3 to quit.")
		choice=input("Enter choice:")
		if choice=="1":
			create_fug_tables()
		elif choice=="2":
			import_fug_csv()
		elif choice=="3":
			break;

# Gets password that won't show in the terminal
password = getpass.getpass("Please enter your password: ")
# string for establishing connection to the database in PostreSQL
connstring="host=localhost dbname=testdb user=postgres password=" + password
main()