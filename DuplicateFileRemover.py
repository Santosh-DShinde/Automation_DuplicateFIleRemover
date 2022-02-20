import hashlib
import os
import schedule
import smtplib
import time
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sys import *
from urllib.request import urlopen

#####################################################################################################
# This is user defined function used to check the internet connection is established or not.
# By using urlopen method it gets check is there internet connection is available or not.
# After that this function return the True/False value to the user defined main function.
# And after checking the connection main method proceed for the next procedure.
#####################################################################################################


def is_connected():
    try:
        urlopen("https://www.google.co.in/", timeout=1)
        return True
    except Exception as obj:
        return False

#####################################################################################################
# This Function Creates Directory if it is not exist in current path.
# In this function after creating the directory we create a Log File in that newly created Directory.
# The log file is such a file which contains the header of Duplicate file Records.
# If we don't give explicitly name of directory then this function creates Directory Implicitly
# named LogFile.
# This log file name will be the "LogFile" and after that the current time also concat.
#####################################################################################################


def Create_Files(Name, DirName='LogFiles'):
    global abs, fd
    File_Name = DirName + datetime.now().strftime("%H-%M-%S") + ".txt"
    if not os.path.exists(DirName):
        os.mkdir(DirName)
    for root, dir, file in os.walk("."):
        for dirnames in dir:
            abs = os.path.join(os.getcwd(), DirName, File_Name)
            if not os.path.exists(abs):
                fd = open(abs, "a")
                Heading = "=" * 80
                fd.write(Heading)
                fd.write(f"\nRecords of Removed Duplicate Files From Directory : {Name} \n")
                fd.write(Heading)
                fd.write("\n")

    RemoveDuplicateFiles(Name, fd, abs, File_Name)

#####################################################################################################
# This function removes all  the duplicate files by considering the checksum of each file.
# If file contains same data, then that function removes that file from that specified directory.
# After deleting that files this function writes the all data ("Information about the deleted files")
# into that Log File Which is in newly Created Directory.
# That function also checks how many duplicate files found inside that specified directory
# This function checks tha how many files scanned how many remaining
#####################################################################################################


def RemoveDuplicateFiles(Dups, fd, fileName, LogFileName):
    StartTime = time.time(); Unique = {}; icnt = 0; ncounter = 0
    try:
        if os.path.exists(Dups):
            for root, directory, file in os.walk(Dups):
                for files in file:
                    icnt += 1
                    file = os.path.join(os.getcwd(), Dups, files)
                    if not os.path.isdir(file) and os.path.isfile(file):
                        HashCode = hashlib.md5(open(file, "rb").read()).hexdigest()
                        if HashCode not in Unique:
                            Unique[HashCode] = file
                        else:
                            ncounter += 1
                            os.remove(file)
                            print(f"Successfully deleted {file}")
                            fd.write(f"\n{file} File gets successfully deleted\n")
            if ncounter == 0:
                fd.write(f"No Duplicate Files Found in {Dups} Directory \n")
            else:
                fd.write(f"\n{ncounter} Duplicate files found ")

        fd.close()

    except Exception as obj:
        print("Exception Occurred : ", obj)

    ExeTime = (time.time() - StartTime)
    ExeTime = round(ExeTime, 4)
    mail_Sending(File_Name=fileName, Counter=icnt, NumberOfFileFound=ncounter, Executiontime=ExeTime,
                 LogFileName=LogFileName)

#####################################################################################################
# The mail_Sending function sends the file which is inside the newly created folder.
# This function accepts the file name, how many file scanned, how many files deleted, all execution
# time required for running script, and log file name.
# We have to specify the mail id and password of the sender for sending the mail implicitly.
# Body of the function contains the all statistics.
# After going through this journey this function sends mail to the specific mail id which is provided
# by commandline arguments.
#####################################################################################################


def mail_Sending(File_Name, Counter, NumberOfFileFound, Executiontime, LogFileName):
    try:
        Sender = "shindesan3047@gmail.com"
        Receiver = argv[3]
        password = "Darshan@1214"

        msg = MIMEMultipart()
        msg['From'] = Sender
        msg['To'] = Receiver
        Subject = """
        Process log generated at : %s """ % (datetime.now().strftime("%H_%M_%S"))
        msg['Subject'] = Subject
        body = """
        Hello %s,  
        Total %d files scanned
        Total %d duplicate file found
        Time required for this script is %s
        Please find attached document which contains records of removed duplicates files at : %s 

        This is auto generated mail.
                           \n\n\n\n\n\n\n 
                                      Thanks & Regards,
                                      Santosh  Shinde
            """ % (Receiver, Counter, NumberOfFileFound, Executiontime, datetime.now().strftime("%H_%M_%S"))

        msg.attach(MIMEText(body, 'plain'))

        attachment = open(File_Name, "rb")

        p = MIMEBase('application', 'octet-stream')

        p.set_payload(attachment.read())
        encoders.encode_base64(p)

        p.add_header('content-Disposition', 'attachment;  filename= "%s" ' % LogFileName)

        msg.attach(p)

        s = smtplib.SMTP('smtp.gmail.com', 587)

        s.starttls()

        s.login(Sender, password)

        text = msg.as_string()

        s.sendmail(Sender, Receiver, text)

        s.quit()

        print("Log File sent through mail")

    except Exception as obj:
        print("Exception Occurred mail send: ", obj)

#####################################################################################################
# "main" is our user defined entry point function, from where our execution gets starts.
# This function checks all the conditions and suggest to the user how to execute that script.
# This function helps the user how to execute the script and what is the usage of that script.
# By using the scheduler this script automatically executes after specified time.
#####################################################################################################


def main():
    print(f"""\n-----------: This Is Automation Script By : Santosh Shinde :--------------\n
application name is :\t{argv[0].split(".")[0]} """)

    if len(argv) < 2 or len(argv) > 4 or len(argv) == 3:
        print('''Error : Argumental error, please refer below flags for help or usage 
For help  : -h or -H
For Usage : -u or -U''')

    if len(argv) == 2:
        if argv[1] == "-h" or argv[1] == "-H":
            print("""Help : We are happy to help you, please follow below instructions for proper execution of the Application
This Application accepts three commandline arguments as -
<1>first argument is absolute path of directory which may contains duplicate files
<2>second argument is time interval of script in minutes
<3>third argument is <mail id> of receive
expected syntax is -> <"Application_Name.py  Dir_Name_WhichMayContainsDuplicateFiles  TimeForScheduleScriptInMinutes  Receiver_MailID"> """)

        elif argv[1] == "-u" or argv[1] == "-U":
            print("""Usage : The use of this application is to <"Remove the duplicate files from specific Directory or specified path">
and create LogFile into new directory which create while running script this directory contains the all records about deleted duplicate files.
after writing record into file send that LogFile to anybody who do you want to send through mail which is accepted from user """)

    if len(argv) == 4:
        if is_connected():
            print("Processing.....🔍")
            try:
                schedule.every(int(argv[2])).minutes.do(Create_Files, argv[1])
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except Exception as obj:
                print("Exception Occurred : ", obj)
        else:
            print("Oops : You're offline. Check your internet connection")


if __name__ == "__main__":
    main()
