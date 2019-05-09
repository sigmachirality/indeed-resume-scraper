from indeed_scraper import process_query
import os

def main():
	locationString = ''' New York
Los Angeles
Chicago
Brooklyn
Queens
Houston
Manhattan
Phoenix
Philadelphia
San Antonio
Bronx
San Diego
Dallas
San Jose
Austin
Jacksonville
San Francisco
Columbus
Fort Worth
Indianapolis
Charlotte
Seattle
Denver
Washington
Boston
El Paso
Detroit
Nashville
Memphis
Portland
Oklahoma City
Las Vegas
Louisville
Baltimore
Milwaukee
Albuquerque
Tucson
Fresno
Sacramento
Mesa
Kansas City
Atlanta
Staten Island
Long Beach
Omaha
Raleigh
Colorado Springs
Miami
Virginia Beach
'''

	locations = locationString.split("\n")
	locations = [i.strip() for i in locations if i != ""]
	jobs = ["engineer", "lawyer", "doctor", "journalist", "software engineer", "nurse", "consultant", "executive"]


	output_folder = os.path.dirname(os.path.abspath(__file__)) + os.sep + "data"

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	for j in jobs:
		for l in locations[:10]:
			process_query(j, l, output_folder)









main()