import argparse
import csv
import sys
from collections import OrderedDict
from json import dump


###########################################################
# TODO
# Bring average back
###########################################################

# Constants
MONTHLY_INCOME = 3739.0
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
CATEGORIES = [
'Home and Utilities', 
'Transportation', 
'Groceries', 
'Personal and Family Care', 
'Health', 
'Insurance', 
'Restaurants and Dining', 
'Shopping and Entertainment', 
'Travel', 
'Cash, Checks, and Misc', 
'Giving', 
'Education', 
'Finance', 
'Uncategorized'
]

# Helper function to print data in json format for debugging purposes
def print_data_as_json(data):

	with open('data.json', 'w') as f:
		dump(data, f, indent=2)

# Helper function to convert money strings to floats
def convert_to_float(s):

	return float(s.strip().replace('$', '').replace(',', ''))

# Helper function to create default dictionary
def create_default_dictionary():

	data = OrderedDict()

	for month in MONTHS:
		data[month] = OrderedDict()
		data[month]['Total'] = 0.0
		data[month]['Categories'] = OrderedDict()
		data[month]['Category Totals'] = OrderedDict()

		for category in CATEGORIES:
			data[month]['Category Totals'][category] = 0.0

			data[month]['Categories'][category] = OrderedDict()
			data[month]['Categories'][category]['Company Totals'] = OrderedDict()
			data[month]['Categories'][category]['Expense Totals'] = OrderedDict()
			data[month]['Categories'][category]['Transactions'] = []

	return data

# Function to read CSV file for data
def read_data():
	
	first_line_read = False

	data = create_default_dictionary()

	with open('budget.csv', 'r') as csv_file:
		reader = csv.reader(csv_file)

		headers = [item.decode("utf-8-sig").encode("utf-8") for item in next(reader) if item != '']

		if headers != CATEGORIES:
			raise Exception('Invalid category in CSV file!')
				
		for row in reader:
			length = len(row)
			index = 0
			count = 0
			while index != length:
				if row[index] in data:
					# row[index] == month
					# row[index+1] == company
					# row[index+2] == amount spent
					# row[index+3] == expense type
					# CATEGORIES[count] == category

					# Set the fields in the month class
					amount_as_float = convert_to_float(row[index+2])
					data[row[index]]['Total'] += amount_as_float
					data[row[index]]['Category Totals'][CATEGORIES[count]] += amount_as_float

					# Set the fields in the month's category class
					month_category = data[row[index]]['Categories'].get(CATEGORIES[count])
					month_category['Company Totals'][row[index+1]] = month_category['Company Totals'].get(row[index+1],0.0) + amount_as_float
					month_category['Expense Totals'][row[index+3]] = month_category['Expense Totals'].get(row[index+3],0.0) + amount_as_float
					month_category.get('Transactions').append([row[index+1],amount_as_float,row[index+3]])
					

				# Each category should only contain at most 4 columns per row, so we increment by 4
				# Count is just a nice way to increment through our categories list -- this assumes the CSV is accurate with our headers
				index += 4
				count += 1

	return data

# Function to get total amount spent in a specified month
def get_total_of_single_month(data, month):

	return data[month].get('Total')

# Function to get the cumulative total of a specified category
def get_total_of_single_category(data, category):

	return sum([month_data['Category Totals'].get(category) for month_data in data.values()])

# Function to get the company specifics of a specified month and category combo
def get_details_for_category_in_month(data, category, month):

	return (data[month]['Categories'].get(category).get('Company Totals'), 
					data[month]['Categories'].get(category).get('Expense Totals'))

# Function to break down average spending for the year and in each month
# def get_average_spent_in_each_month(data):

# 	totals = OrderedDict()
# 	year_total = 0.0

# 	for month in MONTHS:
# 			totals[month] = MONTHLY_INCOME - get_total_of_single_month(data, month)
# 			year_total += totals[month]

# 	return totals, year_total/len(MONTHS)

# Function to breakdown a month's spending per category
def get_category_breakdown_for_single_month(data, month):

	return data[month].get('Category Totals')

# Function to breakdown a category's spending per month
def get_month_breakdown_for_single_category(data, category):

	return_dict = OrderedDict()
	
	for month, obj in data.iteritems():
		return_dict[month] = obj['Category Totals'].get(category)
	
	return return_dict

# Function to get the amount spent on a category in a single month
def get_category_total_in_single_month(data, category, month):

	return data[month]['Category Totals'].get(category)

# Intermediary function to handle arg parsing and print statements
def handle_args(args):

	if args.month is None and args.category is None:
		raise Exception('No inputs given! Please specify a month and/or category')
	
	# Read data
	data = read_data()

	# Detailed view of a month and category combo
	if args.month and args.category:

		companies, expenses = get_details_for_category_in_month(data, args.category, args.month)

		print('\nYour {} {} breakdown is as follows:'.format(args.month, args.category))
		
		print('\nCompanies:')
		for company, total in companies.iteritems():
			print('${0:-7.2f} spent at {1:5}'.format(total, company))

		print('\nExpenses')
		for expense, total in expenses.iteritems():
			print('${0:-7.2f} was spent on {1:5} purchases'.format(total, expense))

		overall_total = get_category_total_in_single_month(data, args.category, args.month)

		print('\nOverall you spent ${} in {} on {}\n'.format(overall_total, args.month, args.category))

	# Get amount spent in each category for a single month
	elif args.month and args.category is None:
		
		breakdown = get_category_breakdown_for_single_month(data, args.month)
		print('\nYour {} breakdown is as follows:\n'.format(args.month))
		for category, total in breakdown.iteritems():
			print('${0:-7.2f} spent on {1:5}'.format(total, category))

		total = get_total_of_single_month(data, args.month)
		print('\nOverall you spent ${} in {}\n'.format(total, args.month))

	# Get amount spent in each month for a single category
	elif args.month is None and args.category:
		
		print('\nYour {} breakdown is as follows:\n'.format(args.category))

		breakdown = get_month_breakdown_for_single_category(data, args.category)
		for month, total in breakdown.iteritems():
			print('${0:-7.2f} spent in {1:5}'.format(total, month))

		total = get_total_of_single_category(data, args.category)
		print('\nOverall you spent ${} on {}\n'.format(total, args.category))
	
	# Expect average command
	# elif 'average' in args:
	# 	totals, average = get_average_spent_in_each_month(data)
	# 	for month, total in totals.iteritems():
	# 		print('You saved ${0:-7.2f} in {1:5}'.format(total, month))
	# 	print('\nOn average you saved ${0:.2f} per month this year'.format(average))

# Main
def main():

	parser = argparse.ArgumentParser(description='Runs Ian\'s budget analyzer')
	
	parser.add_argument('-m', '--month', type=str, choices=MONTHS, help='The month you wish to analyze')
	parser.add_argument('-c', '--category', type=str, choices=CATEGORIES, help='The category you wish to analyze')

	# average_parser = subparsers.add_parser('average', help='')
	# average_parser.set_defaults(average=True)

	args = parser.parse_args()

	try:
		handle_args(args)
	except Exception as e:
		print('{}'.format(e))
		sys.exit(1)

# Starter
if __name__ == '__main__':
	
	main()
