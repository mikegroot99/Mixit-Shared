import os

CLIENT_ID = "1d512be4-f921-4613-9035-15ea23bd0c07" 

CLIENT_SECRET = "bhz8Q~ySRzBi.R0ZD0YvI5bTi.SMGeFeg2w1JaTb" 

AUTHORITY = "https://login.microsoftonline.com/common"

REDIRECT_PATH = "/getAToken"

CENDPOINT = 'https://graph.microsoft.com/v1.0/me/calendarview?startdatetime=2022-04-28T10:10:18.978Z&enddatetime=2022-05-09T10:10:18.979Z'   # This resource requires no admin consent
EENDPOINT = 'https://graph.microsoft.com/v1.0/me/messages'

SCOPE = ["Calendars.ReadWrite", "Mail.Read"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
