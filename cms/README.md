1. Install Python : ```pip install python3.9.1```

2. Setup Virtualenv : ```sudo pip3 install virtualenv```
                      ```virtualenv venv -p python3```
                      ```source venv/bin/activate```

3. Inside the virtualenv clone the repo. And navigate into cms folder where ```manage.py``` file is located


4. Install the required packages with ```pip3 install -r requirement.txt```

5. make migrations with the command: ``` python manage.py makemigrations```
   
6. make migrations with the command ```bash migrate_and_seed.sh ```      
   
7. Run django server: ``` python manage.py runserver```

8. Admin details username: ```mahesh``` , password: ```mahesh61437```, email: ```accessmaheshforu@gmail.com```

9. Change email to ```accessmaheshforu@gmail.com``` in login API and you can get the token for admin.
Use the same token for all the tings. if you forget the token, hit ```get_token``` API with valid email and password to get the new or existing token
