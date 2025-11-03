Type in the username and password to be used for the
database.

a.
User – ImportUser

b.
Password – Import123!@#

Note:
if you change this password from the one above you will need to run the below
command to set the correct encrypted password in the SDS_PPID.ini.

Adding the SQL account password to the SDS_PPID.ini

a.
In order to set the password in the SDS_PPID.ini you will need to
run this command. This command will encrypt the password and update the INI
file with the password.

b.
C:\>SDS_PPID.exe /SET_PASSWORD:”Import123!@#” (or the password for sql account if
different)
