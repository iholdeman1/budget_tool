import argparse
import csv
import sys
from collections import OrderedDict
from json import dump

# Constants
MONTHLY_INCOME = 3739.0
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Sale class to neatly contain sale details
class Sale:

	def __init__(self, company, amount, occurrence):
		self.company = company
		self.amount = amount
		self.occurrence = occurrence

# Month class to contain sales objects and a total spent
class Month:

	def __init__(self):
		self.sales = []
		self.total = 0.0

# Category class to contain month objects in that category
class Category:

	def __init__(self):
		self.months = OrderedDict({month : Month() for month in MONTHS})
		self.total = 0.0

# Helper function to print data in json format for debugging purposes
def print_data_as_json(data):
	
	final_result = {}

	for category, obj in data.iteritems():
		final_result[category] = OrderedDict()
		for month in obj.months.keys():
			final_result[category][month] = {}
			final_result[category][month]['Total'] = obj.months[month].total
			final_result[category][month]['Sales'] = [(sale.company, str(sale.amount), sale.occurrence) 
																								 for sale in obj.months[month].sales]
			final_result[category]['Total'] = obj.total

	with open('data.json', 'w') as f:
		dump(final_result, f, indent=2)

# Helper function to convert money strings to floats
def convert_to_float(s):
	return float(s.strip().replace('$', '').replace(',', ''))

# Function to read CSV file for data
def read_data():
	
	first_line_read = False
	categories = OrderedDict()

	with open('budget.csv', 'r') as csv_file:
		reader = csv.reader(csv_file)
		data_categories = []

		for row in reader:
			# Read in category names
			if not first_line_read:
				for item in row:
					if item:
						data_categories.append(item.decode("utf-8-sig").encode("utf-8"))
				
				# Create category objects
				for category in data_categories:
					categories[category] = Category()

				# Set read
				first_line_read = True
			
			# Read in row of data
			else:
				length = len(row)
				index = 0
				count = 0
				while index != length:
					if row[index] in MONTHS:
						category_month = categories[data_categories[count]].months[row[index]]
						amount_as_float = convert_to_float(row[index+2])
						category_month.sales.append(Sale(row[index+1],amount_as_float,row[index+3]))
						category_month.total += amount_as_float
						categories[data_categories[count]].total += amount_as_float

					index += 4
					count += 1

	return categories

# Function to get total amount spent in a specified month
def get_total_of_single_month(data, month):

	return sum([category.months.get(month).total for category in data.values()])

# Function to get the cumulative total of a specified category
def get_total_of_single_category(data, category):

	return data[category].total

# Function to break down average spending for the year and in each month
def get_average_spent_in_each_month(data):

	totals = OrderedDict()
	year_total = 0.0

	for month in MONTHS:
			totals[month] = MONTHLY_INCOME - get_total_of_single_month(data, month)
			year_total += totals[month]

	return totals, year_total/len(MONTHS)

def get_month_breakdown_for_single_category(data, category):

	return OrderedDict({month : obj.total for month, obj in data.get(category).months.iteritems()})

def get_category_breakdown_for_single_month(data, month):

	return OrderedDict({category : obj.months.get(month).total for category, obj in data.iteritems()})

# Intermediary function to handle arg parsing and print statements
def handle_args(args):
	
	# Read data
	data = read_data()

	# Expect month command
	if 'month' in args:
		if args.split:
			breakdown = get_category_breakdown_for_single_month(data, args.month)
			print('Your {} breakdown is as follows:'.format(args.month))
			for category, total in breakdown.iteritems():
				print('${0:-7.2f} spent on {1:5}'.format(total, category))

		total = get_total_of_single_month(data, args.month)
		if total == 0.0:
			print('You either didn\'t spend any money or {} hasn\'t passed yet'.format(args.month))
		else:
			print('You spent ${0:.2f} total in {1:5}'.format(total, args.month))
	
	# Expect category command
	elif 'category' in args:
		if args.category not in data:
			raise Exception('Invalid category: {}'.format(args.category))

		if args.split:
			breakdown = get_month_breakdown_for_single_category(data, args.category)
			for month, total in breakdown.iteritems():
				print('${0:-7.2f} spent in {1:5}'.format(total, month))

		total = get_total_of_single_category(data, args.category)
		print('You spent ${} on {} related expenses this year'.format(total, args.category))
	
	# Expect average command
	elif 'average' in args:
		totals, average = get_average_spent_in_each_month(data)
		for month, total in totals.iteritems():
			print('You saved ${0:-7.2f} in {1:5}'.format(total, month))
		print('\nOn average you saved ${0:.2f} per month this year'.format(average))

# Main
def main():

	parser = argparse.ArgumentParser(description='Runs Ian\'s budget analyzer')
	subparsers = parser.add_subparsers(help='sub-command help')

	month_parser = subparsers.add_parser('month', help='')
	month_parser.add_argument('month', type=str, choices=MONTHS, help='')
	month_parser.add_argument('--split', required=False, action='store_true', help='')

	category_parser = subparsers.add_parser('category', help='')
	category_parser.add_argument('category', type=str, help='')
	category_parser.add_argument('--split', required=False, action='store_true', help='')

	average_parser = subparsers.add_parser('average', help='')
	average_parser.set_defaults(average=True)

	args = parser.parse_args()

	try:
		handle_args(args)
	except Exception as e:
		print('{}'.format(e))
		sys.exit(1)

# Starter
if __name__ == '__main__':
	
	main()
