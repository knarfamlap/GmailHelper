from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors




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







###################################################
def GetMessage(service, user_id, msg_id):
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id, format= 'metadata', metadataHeaders='From').execute()


    # return from and snippet
    msg = []
    msg.append(message['payload']['headers'][0]['value'])
    msg.append(message['snippet'])

    #index 0 is from
    #index 1 is snippet
    return msg
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


unread_messages = ListMessagesWithLabels(service, 'me', label_ids=[label_id_inbox, label_id_unread])


print('Unread messages in inbox: ', str(len(unread_messages)))



for msg in unread_messages:
    dict = {}
    msg_id = msg['id']
    full_message = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = full_message['payload'] #fetching payload from the message
    header = payload['headers'] #fetching the headers from payload

    for hdr in header:
        if hdr['name'] == 'Subject':
            dict['Subject'] = hdr['value']
        else:
            pass

    for dte in header:
        if dte['name'] == 'Date':
            dict['Date'] = dte['value']
        else:
            pass

    for frm in header:
        if frm['name'] == 'From':
            dict['From'] = frm['value']
        else:
            pass

    dict['Snippet'] = full_message['snippet']





#Calling List of Messages with the query. Returns msg Id
# messagesMatchingQuery = ListMessagesMatchingQuery(service, 'me','Knight News')


#appends each snippet from each message into messaSnippets
# msg = []
# for messages in messagesMatchingQuery:
#     #messagSnippets then is imported into script.py and passed into message.html
#     #which is then rendered
#     snipp = GetMessage(service, 'me', messages['id'])[1]
#     email_sender = GetMessage(service, 'me', messages['id'])[0]
#     info = {'From': email_sender,
#             'Snippet': snipp
#             }
#     msg.append(dict(info))
#
# for item in msg:
#     for k,v in item.items():
#         print(k ,v)
#
