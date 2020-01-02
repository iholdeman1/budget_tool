import argparse
import csv
import sys
from collections import OrderedDict

MONTHLY_INCOME = 3739.0
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Function to read CSV file for data
def read_data():
	
	data = OrderedDict()
	headers = True

	with open('budget.csv', 'r') as csv_file:
		reader = csv.reader(csv_file)
		data_headers = []

		for row in reader:
			if headers:
				for item in row:
					if item:
						item = item.decode("utf-8-sig").encode("utf-8")
						data[item] = {}
						for month in MONTHS:
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

# Function to return a dictionary containing amount spent in each month
def get_total_per_month(data): # TODO: fix months that haven't happened yet!

	def convert_to_float(s):
		return float(s.strip().replace('$', '').replace(',', ''))

	monthly_data = OrderedDict()
	for month in MONTHS:
		monthly_data[month] = {}

	for month in MONTHS:
		total = 0.0
		for key, val in data.iteritems():
			if val.get(month):
				month_data = val.get(month)
				total += sum([convert_to_float(transactions[0]) for company in month_data for transactions in month_data.get(company)])
				
		monthly_data[month] = total

	return monthly_data

# Function to get total amount spent in a specified month
def get_total_of_single_month(data, args):

	if args.month not in MONTHS:
		raise Exception('Invalid month: {}'.format(args.month)) # TODO: Make choices list in argparse
	
	total = get_total_per_month(data)

	if total[args.month] != 0.0:
		print('You spent ${} in {}'.format(total[args.month], args.month))
	else:
		print('{} hasn\'t passed yet!'.format(args.month))

# Function to get the cumulative total of a specified category
def get_total_of_single_category(data, args):

	def convert_to_float(s):
		return float(s.strip().replace('$', '').replace(',', ''))

	if args.category not in data:
		raise Exception('Invalid category: {}'.format(args.category)) # TODO: Make choices list in argparse

	sub_data = data.get(args.category)
	total = 0.0

	for month_data in sub_data.values():
		for company in month_data:
			for transaction in month_data[company]:
				total += convert_to_float(transaction[0])

	print('You spent ${} on {} related expenses this year'.format(total, args.category))

# Function to break down average spending in each month
def get_average_spent_in_each_month(data, args):

	year_total = 0.0
	month_count = 0

	total = get_total_per_month(data)

	for month in MONTHS:
		if total[month] != 0.0:
			net_saving = MONTHLY_INCOME - total[month]
			print('You saved ${} in {}'.format(net_saving, month))
			year_total += net_saving
			month_count += 1

	print('\nOn average you saved ${} per month this year!'.format(year_total/month_count))

# Main
def main():

	parser = argparse.ArgumentParser(description='Runs Ian\'s budget analyzer')
	subparsers = parser.add_subparsers(help='sub-command help')

	month_parser = subparsers.add_parser('month', help='')
	month_parser.add_argument('month', type=str, help='')
	month_parser.set_defaults(func=get_total_of_single_month)

	category_parser = subparsers.add_parser('category', help='')
	category_parser.add_argument('category', type=str, help='')
	category_parser.set_defaults(func=get_total_of_single_category)

	average_parser = subparsers.add_parser('average', help='')
	average_parser.set_defaults(func=get_average_spent_in_each_month)

	data = read_data()

	args = parser.parse_args()
	
	try:
		args.func(data, args)
	except Exception as e:
		print('{}'.format(e))
		sys.exit(1)

# Starter
if __name__ == '__main__':
	
	main()
