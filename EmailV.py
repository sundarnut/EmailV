# If you're on a Macbook, follow these steps to make the program work.
# It will only work if you have VPNed in to our office network.
# 
# 1. Install Python3
#    Head to https://python.org/
#    Navigate to Downloads and install Python 3.9 for your Macbook
#    This will install python3 and pip3 for you to use on your Macbook
#
# 2. Verify it works
#    Head to your Terminal Window and type "python3" and press enter
#    You will see something like:
#        Python 3.9.0 (v3.9.0:9cf6752276, Oct  5 2020, 11:29:23) 
#        [Clang 6.0 (clang-600.0.57)] on darwin
#        Type "help", "copyright", "credits" or "license" for more information.
#        >>> 
#
# 3. Check if pip3 works as well, by typing pip3 on your Terminal Console:
#    You will see a long list of options for pip3 to be employed
#
# 4. Install requests by typing this command:
#        pip3 install requests
#
# 5. Download this Python file locally to your Documents folder.
#
# 6. Create a text file with all @company.com email addresses that have
#    accounts on an external website.
#
# 7. Run this file by executing the following command:
#        python3 -W ignore EmailV.py list_of_accounts.txt
#
# 8. With this sample file a1.txt, do:
#        python3 -W ignore EmailV.py a1.txt
#
# 9. It will find out how many of these accounts are not valid in our 
#    network, at the point of execution if you use a text file.
#

import json
import os.path
import requests
import sys

def main():

    if len(sys.argv) != 2:

        print("Usage: python3 -W ignore EmailV.py [filename] or ")
        print("       python3 -W ignore EmailV.py [email_address]")
        print()
        print("    This program will read all email addresses in the file,")
        print("        and check if any of those are not valid in the Active Directory.")
        print("    You can also provide a specific email address for current eligibility check in AD.")
        print("    It will only check for email addresses valid in the [Company] domain, like @company.com or @fellowcompany.com.")
        print()
        print("Example: python3 -W ignore EmailV.py list_of_emails.txt")
        print("         python3 -W ignore EmailV.py johndoe@company.com")

        return

    # Obtain list of all valid email domains
    domainResponse = requests.get('https://yourserver.company.com/GetEmailDomains.aspx')
    domainJson = json.loads(domainResponse.text)

    if os.path.isfile(sys.argv[1]):

        total = 0
        validCounter = 0

        print("Processing file:", sys.argv[1]);
        print()

        file = open(sys.argv[1], "r")
        line = file.readline()

        while line:

            elements = line.split()

            for element in elements:

                atPosition = element.find("@")

                if atPosition > 0 and atPosition < len(element):
                    domain = element[atPosition + 1:]

                    if domain.lower() in domainJson["domains"]:

                        found = False

                        total += 1

                        response = requests.get('https://yourserver.company.com/Services/GetPrimaryEmail.aspx?email=' + element);
                        responseJson = json.loads(response.text)

                        errorCode = responseJson["errorCode"]

                        if errorCode == 0:
                            primaryEmail = responseJson["primaryEmail"]

                            response = requests.get('https://yourserver.company.com/Services/CheckUser.aspx?email=' + primaryEmail);
                            responseJson = json.loads(response.text)

                            if responseJson["valid"]:
                                validCounter += 1
                                found = True

                        if found == False:
                            print(element, "is no longer valid.")

            line = file.readline()

        file.close()
        print()
        print("Found", validCounter, "valid emails out of", total, "in file:", sys.argv[1]);

        return

    atPosition = sys.argv[1].find("@")

    if atPosition > 0 and atPosition < len(sys.argv[1]):
        domain = sys.argv[1][atPosition + 1:]

        if domain.lower() in domainJson["domains"]:

            found = False

            response = requests.get('https://yourserver.company.com/Services/GetPrimaryEmail.aspx?email=' + sys.argv[1])
            responseJson = json.loads(response.text)

            errorCode = responseJson["errorCode"]

            if errorCode == 0:
                primaryEmail = responseJson["primaryEmail"]

                response = requests.get('https://yourserver.company.com/Services/CheckUser.aspx?email=' + primaryEmail)
                responseJson = json.loads(response.text)

                if responseJson["valid"]:
                    print(sys.argv[1] + " is valid.")
                    found = True

            if found == False:
                print(sys.argv[1], "is no longer valid.")

        else:
            print("Please use email addresses that are valid in the Company domain.")

    else:
        print("Unable to find file: ", sys.argv[1])

main()
