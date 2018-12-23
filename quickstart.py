from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors
import base64
from bs4 import BeautifulSoup
import re
import time
import dateutil.parser as parser
from datetime import datetime
import datetime
import csv
import json
from tqdm import tqdm



def ListMessagesWithLabels(service, user_id, label_ids=[]):

  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print('An error occurred: %s' % error)



##################################################
def ListMessagesMatchingQuery(service, user_id, query):
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError, error:
    print('An error occurred: %s' % error)


# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

# Call the Gmail API
label_id_inbox = 'INBOX'
label_id_unread = 'UNREAD'


if raw_input("Would you like to seach by query? y/n ").startswith('y'):
    query = raw_input("Enter query: ")
    messages = ListMessagesMatchingQuery(service, 'me', query)
else:
    messages = ListMessagesWithLabels(service, 'me', label_ids=[label_id_inbox, label_id_unread])
    print("LOADING UNREAD MESSAGES...")


print('Unread messages in inbox: ', str(len(messages)))

formated_messages = [ ]


for msg in messages:
    dict = {}
    msg_id = msg['id']
    full_message = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = full_message['payload'] #fetching payload from the message
    header = payload['headers'] #fetching the headers from payload

    for hdr in header:
        if hdr['name'] == 'Subject':
            subject  = hdr['value']
            dict['Subject'] = subject
        else:
            pass

    for dte in header:
        if dte['name'] == 'Date':
            date_parser = parser.parse(dte['value'])
            m_date = date_parser.date()
            dict['Date'] = str(m_date)
        else:
            pass

    for frm in header:
        if frm['name'] == 'From':
            sender = frm['value']
            dict['From'] = sender
        else:
            pass

    dict['Snippet'] = full_message['snippet']



    try:
        # Fetching message body
		mssg_parts = payload['parts'] # fetching the message parts
		part_one  = mssg_parts[0] # fetching first element of the part
		part_body = part_one['body'] # fetching body of the message
		part_data = part_body['data'] # fetching data from the body
		clean_one = part_data.replace("-","+") # decoding from Base64 to UTF-8
		clean_one = clean_one.replace("_","/") # decoding from Base64 to UTF-8
		clean_two = base64.b64decode (bytes(clean_one, 'UTF-8')) # decoding from Base64 to UTF-8
		soup = BeautifulSoup(clean_two , "lxml" )
		mssg_body = soup.body()
		# mssg_body is a readible form of message body
		# depending on the end user's requirements, it can be further cleaned
		# using regex, beautiful soup, or any other method
		dict['Message_body'] = mssg_body
    except:
        pass
    formated_messages.append(dict)



with open('data.json', 'w') as outfile:
    json.dump(formated_messages, outfile)

print('DONE!')



#
