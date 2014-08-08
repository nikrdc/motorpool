![alt tag](https://raw.githubusercontent.com/nikrdc/motorpool/master/static/img/logo.png)

Twice a year, Viget employees carpool to and from large company events. Currently, the office manager handles the organization of these carpools herself, using a time consuming and fragile combination of Google Docs and email correspondence. Motorpool is a web app with the intended goal of minimizing the pain of coordinating carpools, both for office managers and employees.

#### How Motorpool works:
**1. Create an event and share its URL with other attendees.** Each event has a securely unique URL that can’t be reproduced by anyone it hasn’t been shared with. For further protection, add a password to the event.

**2. Wait for attendees to join the event as drivers and riders, organizing carpools organically.** Each event has a list of rides there and back. Anyone is free to join as a driver and create new rides. Once rides have been added by drivers, other attendees can join them as riders.

**3. Check the event page to view and edit ride information.** Drivers and riders can return to the event page to check who they’re riding with and edit their rides. Motorpool displays a range of information that makes organizing carpools much easier.


#### Usage notes:
* Font files have not been included.
* Use a virtual environment to run and develop the app locally by installing the _virtualenv_ utility.
* Install requirements in your virtual environment or production environment with `pip install -r requirements.txt`
* The secret key must be set in the environment for the app to function securely. Follow [this](http://stackoverflow.com/questions/14786072/keep-secret-keys-out-with-environment-variables) link to learn how to set a secret key with an environment variable. 
* If you want email notifications, remember to set the mail username and password in the environment (using the same method you used for the secret key).
