import argparse
import csv
import sys
from collections import OrderedDict
from json import dump

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

# Transaction class to neatly contain sale details
class Transaction:

	def __init__(self, company, amount, occurrence):
		self.company = company
		self.amount = amount
		self.occurrence = occurrence

# Month class to contain sales objects and a total spent
class Month:

	def __init__(self):
		
		self.total = 0.0
		self.categories = OrderedDict()
		self.category_totals = OrderedDict()
		
		for category in CATEGORIES:
			self.categories[category] = Category()
			self.category_totals[category] = 0.0

# Category class to contain month objects in that category
class Category:

	def __init__(self):
		
		self.company_totals = OrderedDict()
		self.expense_totals = OrderedDict()
		self.transactions = []

# Helper function to print data in json format for debugging purposes
def print_data_as_json(data):
	
	final_result = OrderedDict()

	for month, data in data.iteritems():
		final_result[month] = OrderedDict()
		final_result[month]['Total'] = data.total
		final_result[month]['Categories'] = OrderedDict()
		final_result[month]['Category Totals'] = data.category_totals
		for category in data.categories.keys():
			final_result[month]['Categories'][category] = OrderedDict()
			final_result[month]['Categories'][category]['Company Totals'] = data.categories[category].company_totals
			final_result[month]['Categories'][category]['Expense Totals'] = data.categories[category].expense_totals
			final_result[month]['Categories'][category]['Transactions'] = [(transaction.company, str(transaction.amount), transaction.occurrence) 
																								 											for transaction in data.categories[category].transactions]

	with open('data.json', 'w') as f:
		dump(final_result, f, indent=2)

# Helper function to convert money strings to floats
def convert_to_float(s):
	return float(s.strip().replace('$', '').replace(',', ''))

# Function to read CSV file for data
def read_data():
	
	first_line_read = False
	data = OrderedDict()

	for month in MONTHS:
		data[month] = Month()

	with open('budget.csv', 'r') as csv_file:
		reader = csv.reader(csv_file)

		headers = [item.decode("utf-8-sig").encode("utf-8") for item in next(reader) if item != '']

		# for i in range(len(headers)):
		# 	if headers[i] != CATEGORIES[i]:
		# 		print(headers[i])

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
					# CATEGORIES[count] == category -- this assumes the CSV is accurate with our headers

					# Set the fields in the month class
					amount_as_float = convert_to_float(row[index+2])
					data[row[index]].total += amount_as_float
					data[row[index]].category_totals[CATEGORIES[count]] += amount_as_float

					# Set the fields in the month's category class
					month_category = data[row[index]].categories.get(CATEGORIES[count])
					month_category.company_totals[row[index+1]] = month_category.company_totals.get(row[index+1],0.0)+amount_as_float
					month_category.expense_totals[row[index+3]] = month_category.expense_totals.get(row[index+3],0.0)+amount_as_float
					month_category.transactions.append(Transaction(row[index+1],amount_as_float,row[index+3]))
					

				index += 4
				count += 1

	return data

# Function to get total amount spent in a specified month
def get_total_of_single_month(data, month):

	return data[month].total

# Function to get the cumulative total of a specified category
def get_total_of_single_category(data, category):

	return sum([obj.category_totals.get(category) for obj in data.values()])

# Function to get the company specifics of a specified month and category combo
def get_details_for_category_in_month(data, category, month):

	return (data[month].categories.get(category).company_totals, data[month].categories.get(category).expense_totals)

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

	return data[month].category_totals

# Function to breakdown a category's spending per month
def get_month_breakdown_for_single_category(data, category):

	return_dict = OrderedDict()
	
	for month, obj in data.iteritems():
		return_dict[month] = obj.category_totals.get(category)
	
	return return_dict

# Intermediary function to handle arg parsing and print statements
def handle_args(args):

	if args.month is None and args.category is None:
		raise Exception('No inputs given! Please specify a month and/or category')
	
	# Read data
	data = read_data()

	if args.month and args.category:

		companies, expenses = get_details_for_category_in_month(data, args.category, args.month)

		print('\nYour {} {} breakdown is as follows:'.format(args.month, args.category))
		
		print('\nCompanies:')
		for company, total in companies.iteritems():
			print('${0:-7.2f} spent at {1:5}'.format(total, company))

		print('\nExpenses')
		for expense, total in expenses.iteritems():
			print('${0:-7.2f} was spent on {1:5} purchases'.format(total, expense))

	elif args.month and args.category is None:
		
		breakdown = get_category_breakdown_for_single_month(data, args.month)
		print('Your {} breakdown is as follows:'.format(args.month))
		for category, total in breakdown.iteritems():
			print('${0:-7.2f} spent on {1:5}'.format(total, category))

	elif args.month is None and args.category:
		
		breakdown = get_month_breakdown_for_single_category(data, args.category)
		for month, total in breakdown.iteritems():
			print('${0:-7.2f} spent in {1:5}'.format(total, month))

	# 	total = get_total_of_single_month(data, args.month)
	# 	if total == 0.0:
	# 		print('You either didn\'t spend any money or {} hasn\'t passed yet'.format(args.month))
	# 	else:
	# 		print('You spent ${0:.2f} total in {1:5}'.format(total, args.month))
	
	# # Expect category command
	# elif 'category' in args:
	# 	if args.category not in data:
	# 		raise Exception('Invalid category: {}'.format(args.category))

	# 	if args.split:
	# 		handle_split_arg(data, args, 'category', args.split)

	# 	total = get_total_of_single_category(data, args.category)
	# 	print('You spent ${} on {} related expenses this year'.format(total, args.category))
	
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
