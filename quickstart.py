from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient import errors

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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
    results = service.users().labels().list(userId='me').execute()
    # Gmails Labels
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])

    #Calling List of Messages with the query. Returns msg Id
    messagesMatchingQuery = ListMessagesMatchingQuery(service, 'me','Knight News')


    #appends each snippet from each message into messaSnippets
    msg = []
    for messages in messagesMatchingQuery:
        #messagSnippets then is imported into script.py and passed into message.html
        #which is then rendered
        snipp = GetMessage(service, 'me', messages['id'])[1]
        email_sender = GetMessage(service, 'me', messages['id'])[0]
        info = {'From': email_sender,
                'Snippet': snipp
                }
        msg.append(dict(info))

    return msg



def ListMessagesMatchingQuery(service, user_id, query):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
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

def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
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


if __name__ == '__main__':
    main()
