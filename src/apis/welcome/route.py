#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Functionalities for the apis_list route.

    The scope of the application is academic research.
    It is part of the Osmotic Computing activities carried 
    out at both University of Messina and TU Wien.
"""

__author__ = "Lorenzo Carnevale"
__copyright__ = None
__credits__ = ["Lorenzo Carnevale"]
__license__ = None
__version__ = "1"
__maintainer__ = "Lorenzo Carnevale"
__email__ = "lcarnevale@unime.it"
__status__ = "Prototype"


import urllib
from flask import url_for


def route_rules(app):
	"""
		This method returns the Agento's APIs list

		Returns:
			content: a JSON data with the APIs list
			status_code: the status code
	"""

	with app.test_request_context():

		output = []
		for rule in app.url_map.iter_rules():
			# list the url parameters
			options = {}
			for arg in rule.arguments:
				options[arg] = "[%s]" % (arg)
			# create the complete url
			url = url_for(rule.endpoint, **options)
			# list the HTTP methods
			methods = ','.join(rule.methods)
			
			output.append([rule.endpoint, methods, url])
	output = sorted(output)

	return output

def route_table(data):
	"""
		This method generates the HTML table with the
		routes list

		TODO
	"""
	pass