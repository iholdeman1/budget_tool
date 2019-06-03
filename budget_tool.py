import argparse
import csv
import sys
from collections import OrderedDict

def read_data():
	
	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	data = OrderedDict()
	headers = True

	with open('test.csv', 'r') as csv_file:
		reader = csv.reader(csv_file)
		data_headers = []

		for row in reader:
			if headers:
				for item in row:
					if item:
						item = item.decode("utf-8-sig").encode("utf-8")
						data[item] = {}
						for month in months:
							data[item][month] = {}
				headers = False
				data_headers = data.keys()
			
			else:
				count = 0
				sub_count = 1
				listy_list = []
				for item in row:
					
					listy_list.append(item)

					if sub_count % 4 == 0:
						if listy_list[0]:
							month = data[data_headers[count]].get(listy_list[0], {})
							company = month.get(listy_list[1], [])
							company.append([listy_list[2], listy_list[3]])
							month[listy_list[1]] = company
							data[data_headers[count]][listy_list[0]].update(month)

						count += 1
						sub_count = 0
						listy_list = []

					sub_count += 1

	return data

def get_total_per_month(data):

	def convert_to_float(s):
		return float(s.strip().replace('$', '').replace(',', ''))

	months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
	monthly_data = OrderedDict()
	for month in months:
		monthly_data[month] = {}

	for month in months:
		total = 0.0
		for key, val in data.iteritems():
			if val.get(month):
				month_data = val.get(month)
				total += sum([convert_to_float(transactions[0]) for company in month_data for transactions in month_data.get(company)])
				
		monthly_data[month] = total

	return monthly_data

def main():

	parser = argparse.ArgumentParser(description='Runs Ian\'s budget analyzer')
	subparsers = parser.add_subparsers(help='sub-command help')

	month_parser = subparsers.add_parser('month', help='')
	month_parser.set_defaults(func=foo)

	category_parser = subparsers.add_parser('category', help='')
	category_parser.set_defaults(func=foo)

	data = read_data()

	# monthly_stuff = get_total_per_month(data)
	
	# monthly_income = 3739.0
	# total_net = []

	# for key, val in monthly_stuff.iteritems():
	# 	if val != 0.0:
	# 		net = monthly_income-val
	# 		total_net.append(net)
	# 		print('You spent ${} in {}. Your net profit was {} after taxes.'.format(val, key, net))

	# total_of_net = sum(total_net)
	# length = len(total_net)

	# print('On average, you bring home ${} per month!'.format(total_of_net/length))

if __name__ == '__main__':
	
	main()