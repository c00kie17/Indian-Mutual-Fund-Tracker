from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
from tqdm import tqdm
from time import sleep
import platform
from datetime import datetime,timedelta
import sys 
import os


def getdata(link,name):
	data = []
	options = Options()
	options.add_argument("--headless") 
	options.add_argument('--no-sandbox') 
	linkdriver = webdriver.Chrome(chrome_options=options, executable_path=chromefile)
	linkdriver.get(link)
	data.append(name)
	try:
		monthValBox = WebDriverWait(linkdriver, 20).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/span/div/div[3]/div/div[1]/div/div[1]/form/div[1]/div[1]/label/input")))
	except TimeoutException:
		return data	
	finally:
		monthValBox.clear()
		monthValBox.send_keys(monthlyAmount)

	try:
		startDateBox = WebDriverWait(linkdriver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@ng-model="sip_start_date"]')))
	except TimeoutException:
		return data		
	finally:	
		startDateBox.clear()
		startDateBox.send_keys(str(startDate))

	try:
		endDateBox = WebDriverWait(linkdriver, 20).until(EC.visibility_of_element_located((By.XPATH, '//*[@ng-model="sip_end_date"]')))
	except TimeoutException:
		return data		
	finally:	
		endDateBox.clear()
		endDateBox.send_keys(str(endDate))

	try:
		calcBox = WebDriverWait(linkdriver, 20).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[1]/div/span/div/div[3]/div/div[1]/div/div[1]/form/div[1]/div[4]/button')))
	except TimeoutException:
		return data		
	finally:	
		calcBox.click()

	values = linkdriver.find_elements_by_class_name("fund-details");
	for index in range(len(values)-8,len(values)):
			data.append(values[index].text)	
	linkdriver.close()				
	return data	


def start():
	
	options = Options()
	options.add_argument("--headless") 
	options.add_argument('--no-sandbox') 

	driver = webdriver.Chrome(chrome_options=options, executable_path=chromefile)
	driver.set_window_size(1120, 550)
	driver.get("https://coin.zerodha.com/funds")
	sleep(2)
	funds = driver.find_elements_by_class_name("cursor-pointer");
	if(len(funds) == 0):
		print("no links found error")
		driver.close()
		start()
	sortedFunds = []	
	if(keyword == ""):
		sortedFunds = funds
	else:
		for fund in funds:
			if keyword.upper() in fund.text.upper(): 
				sortedFunds.append(fund)			
	pbar = tqdm(total=len(sortedFunds))
	for fund in sortedFunds:
		data = getdata(fund.get_attribute("href"),fund.text)
		writer.writerow(data)
		pbar.update(1)
	pbar.close()
	driver.close()	

def getMonthlyAmount():
	print("enter monthly amount: ")
	monthlyAmount = str(input())
	if(not monthlyAmount.isdigit()):
		print("invalid number")
		getMonthlyAmount()
	else:	
		if(int(monthlyAmount) > 1000000000):
			print("amount too high")
			getMonthlyAmount()
	return monthlyAmount		
	
def getStartDate():
	print("enter SIP start date in format MM/DD/YYYY")
	startDate = input()
	try:
		today = datetime.now()
		date = datetime.strptime(str(startDate), '%m/%d/%Y')
	except ValueError:
		print("date format wrong")
		getStartDate()
	else:
		if(date > (today-timedelta(days=1))):
			print("start date needs to be one day behind current day")
			getStartDate()	
	return startDate

def getEndDate():
	print("enter SIP end date in format MM/DD/YYYY")
	endDate = input()
	try:
		today = datetime.now()
		date = datetime.strptime(str(endDate), '%m/%d/%Y')
		if(date > today):
			print("end date cannot be greater that current day")
			getEndDate()
	except ValueError:
		print("date format wrong")
		getEndDate()
	return endDate	

def getKeyword():
	print("enter a keyword, if you want data on all MF leave blank")
	keyword = input()
	if(any(char.isdigit() for char in keyword)):
		print("no number in keyword")
		getKeyword()
	return keyword	

def getFilename():
	print("enter filename")
	fname = input()
	if(fname == ""):
		print("filename cannot be blank")
		getFilename()
	return fname	

if __name__ == '__main__':
	if(platform.system() == "Darwin"):
		chromefile =  os.path.join(sys._MEIPASS, "chromedrivermac")
	elif(platform.system() == "Windows"):	
		chromefile =  os.path.join(sys._MEIPASS, "chromedriverwin.exe")
	else:
		chromefile =  os.path.join(sys._MEIPASS, "chromedriverlinux")	

	monthlyAmount = getMonthlyAmount()
	startDate = getStartDate()
	endDate = getEndDate()
	keyword = getKeyword()
	fname = getFilename()
	
	csvfilePath = os.path.join(os.path.dirname(sys.argv[0]), fname+'.csv')
	file = open(csvfilePath, 'w+')
	writer = csv.writer(file)
	writer.writerow(["Name","Total invested","Current valuation","Net profit","Absolute profit","Total installments","Internal rate of return","SIP start date","SIP end date"])

	print("Press Ctrl+C to exit program")
	start()



