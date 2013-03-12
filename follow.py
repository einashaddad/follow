
# This Python file uses the following encoding: utf-8

import requests
import pyquery as pq
import os
import pdb
import sys

def scrape_hs(hs_email, hs_password, host):
	"""
	Returns a response object after creating an authenticated session with 
	hackerschool 
	"""
	session = requests.session()

	#retrieving the csrf-token from the html
	page = pq.PyQuery(url = host+'/login')
	meta_content = page('meta')

	for m in pq.PyQuery(meta_content):
		if pq.PyQuery(m).attr('name') == 'csrf-token':
			csrf_token = pq.PyQuery(m).attr('content')

	payload = {
		'authenticity_token': csrf_token,
		'email': hs_email,
		'password': hs_password,
		'commit': 'Log In',
		'utf8' : u'✓'
	}

	request = session.post(host+'/sessions', data=payload, verify=False)

	resp = session.get(host+'/private') 

	return resp

def extract_githubs(resp):
	"""
	Returns a dictionary of people to follow with their github usernames as values
	"""
	content = resp.text
	content = pq.PyQuery(content)
	people = content('#batch7 .person')
	
	people_to_follow = {}

	for person in people:
		person = pq.PyQuery(person)
		person_class = person('div.name')
		person_endpoint = person_class('a').attr('href')

		icon_links = person('div.icon-links')
		first_link = icon_links('a').attr('href')
		

		if 'github' in first_link:
			just_user = first_link[17:] 
			people_to_follow[person_endpoint] = just_user
	return people_to_follow

def follow_users(gh_username, gh_password, people_to_follow):
	"""
	Follows the users given in the dictionary by sending a put request to the github API 
	"""
	url = "https://api.github.com/user/following" 

	s = requests.Session()
	s.auth = gh_username, gh_password

	for user_to_follow in people_to_follow.values():

		if s.get(url+user_to_follow).status_code != 204:	#if not following user

			r = s.put(url+user_to_follow)

			if r.status_code == 204:
				print "Followed %s" % (user_to_follow)
			else:
				print "Response for %s" % (user_to_follow)
				print r.content
		else: print "Already following: %s" % (user_to_follow)

if __name__ == '__main__':
	host = 'https://www.hackerschool.com'
	# set the usernames and passwords as environment variables
	try:
		hs_email = os.environ['hs_email']
		hs_password = os.environ['hs_password']
		gh_username = os.environ["gh_username"]
		gh_password = os.environ["gh_password"]
	except KeyError:
		print "Create hs_email, hs_password, gh_username, gh_password as environment variables"
		sys.exit()

	response = scrape_hs(hs_email, hs_password, host)
	people_to_follow = extract_githubs(response)
	follow_users(gh_username, gh_password, people_to_follow)

