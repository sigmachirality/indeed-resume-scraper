import urllib.request
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from multiprocessing.pool import ThreadPool
import time
import json
import threading
import traceback
from random import randint
from time import sleep
import os

class Thread2(Thread):
	def __init__(self, group=None, target=None, name=None,
				 args=(), kwargs={}, Verbose=None):
		Thread.__init__(self, group, target, name, args, kwargs)
		self._return = None
	def run(self):
		print(type(self._target))
		if self._target is not None:
			self._return = self._target(*self._args,
												**self._kwargs)
	def join(self, *args):
		Thread.join(self, *args)
		return self._return

class CustomEncoder(json.JSONEncoder):
	def default(self, z):
		if isinstance(z, Resume):
			return {"id": z.id, "jobs": z.jobs, "schools": z.schools}
		elif isinstance(z, Job):
			return {"title": z.title, "company": z.company, "location": z.location, "hire_date": z.hire_date}
		elif isinstance(z, School):
			return {"degree": z.degree, "school_name": z.school_name, "grad_date": z.grad_date}
		else:
			return super().default(z)

class Resume(object):

	def __init__ (self, idd, jobs, schools):
		self.id = idd
		self.jobs = jobs
		self.schools = schools

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, 
			sort_keys=True, indent=0)


class Job(object):
	def __init__(self, title, company, location, hire_date):
		self.title = title
		self.company = company
		self.location = location
		self.hire_date = hire_date

class School(object):
	def __init__(self, degree, school_name, grad_date):
		self.degree = degree
		self.school_name = school_name
		self.grad_date = grad_date


def gen_idds(url, driver):

	driver.get(url)
	time.sleep(4) #wait for page to load
	p_element = driver.page_source
	soup = BeautifulSoup(p_element, "lxml")
	links = soup.select(".icl-TextLink.icl-TextLink--primary.rezemp-u-h4")

	idds=[]

	for link in links:
		path = link.get("href")
		#print(path[8:path.find("?")]) 
		idds.append(path[8:path.find("?")]) #8 is to account for "\resume\" at the beginning

	return idds
#print(idds)

def gen_resume(idd, driver):
	URL = '''https://resumes.indeed.com/resume/''' + idd


	driver.get(URL)
	p_element = driver.page_source
	soup = BeautifulSoup(p_element, 'lxml')

	results = soup.find_all('div', attrs={"class":"rezemp-ResumeDisplaySection"})
	#print(results)



	schools = []


	try:
		education = results[1]
		content = education.find(class_="rezemp-ResumeDisplaySection-content")
		for uni in content.children:
			degree = uni.find(class_ = "rezemp-ResumeDisplay-itemTitle").get_text()
			university = uni.find(class_="rezemp-ResumeDisplay-university").contents[0].get_text()
			date = uni.find(class_="rezemp-ResumeDisplay-date").get_text()
			schools.append(School(degree, university, date))
	except:
		pass

	jobs = []


	try:
		work_experience = results[0]
		job_titles = work_experience.find_all(class_="rezemp-u-h4")
		job_descriptions = work_experience.find_all(class_="rezemp-u-h5")
		for i in range(len(job_titles)):
			dates = job_descriptions[i].find_next_sibling().get_text()
			date = dates[:dates.find("to")]
			title = job_titles[i].get_text()
			desc = [p.get_text() for p in job_descriptions[i].find_all("span")][1:]
			company = desc[0]
			location = desc[1]
			jobs.append(Job(title, company, location, date))
	except:
		pass

	return Resume(idd, jobs, schools)



def mine(URL, override=True, rangee=None):
	driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) +  os.sep + "chromedriver.exe")
	driver.implicitly_wait(10)


	if rangee == None:	
		start_index = 0 #700
		target = 10901
	else:
		start_index = rangee[0]
		target = rangee[1]


	#print(start_index, target)

	resumes = []

	fail_ctr = 0
	
	try:

		while 1:
			if (start_index >= target or fail_ctr >= 5):
				break
			
			stri = URL+"&start="+str(start_index)
			idds = gen_idds(URL+"&start="+str(start_index), driver)
			
			if (len(idds) == 0):
				time.sleep(4) #wait a little bit, try again
				fail_ctr += 1
				continue

			fail_ctr = 0

			for idd in idds:
				resumes.append(gen_resume(idd, driver))

			start_index+=50

	except Exception:

		traceback.print_exc()

	finally:
		try:
			driver.close()
		except:
			pass
		return resumes

	# resumes = [gen_resume(idd).toJSON() for idd in idds] 

	


def mine_multi(url, override=True):


	thread_list = []
	names = []
	resumes = []


	pool = ThreadPool(processes=8)

	async_result = pool.apply_async(mine, (url,)) # tuple of args for foo

	#{"rangee": (0, 50)}

	resumes = async_result.get()  # get the return value from your function.


	return resumes


def write_out_json(file_path, resumes):
	print("Writing out data...")
	with open(file_path, "w") as file:
		json.dump(resumes, file, cls = CustomEncoder)
	print("Done!")



def process_query(job, location, path = None):
	file_name = "output_data_" + job + "_" + location + ".json"
	if (path == None):
		path = os.path.dirname(os.path.abspath(__file__)) + os.sep + file_name
	path += os.sep + file_name

	URL = "https://resumes.indeed.com/search?q=" + job + "&l=" + location + "&searchFields="
	resumes = mine_multi(URL)
	write_out_json(path, resumes)



def main():



	t = time.clock();

	#idds = ["f845ad88e3d17704", "1992c61c49a470e1"]

	#URL = "https://resumes.indeed.com/search?l=california&q=software%20engineer&searchFields="

	URL = "https://resumes.indeed.com/search?q=engineer&l=california&searchFields="

	#mine("software_engineers_california", URL, override = False)


	#consolidate_files("lawyer-california", ["resume_outputlawyer-california" + str(i) +".json" for i in range(8)])

	# driver = webdriver.Chrome()
	# driver.implicitly_wait(30)

	# print(gen_idds("https://resumes.indeed.com/search?q=doctor&l=california&searchFields=&start=0", driver))



	resumes = mine_multi(URL)
	write_out_json("resume_output_california_engineers", resumes)



	# print(time.clock() - t)


if __name__ == "___main___":
	main()