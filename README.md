# Capstone Project: talentTree

## Description:

- **Introduction:** 
    - **talentTree** is a human capital management platform that focuses on clean data, replacing human error often found in headlines with pre-built function and level options. Each organization gets their own set of data so you can utilize your expanded organizational network while ensuring that your organization's data is secure.

-  **Features:**
    - Companies: to ensure clean data, companies are unique to your organization based on domain. Companies are the base feature that connect the profiles to their roles and contact maps.
    - Roles: Currently only primary roles are supported. This is the most important attribute of a profile, that ties together a level, function(s), a company, and a start date.
    - Profiles: the bread and butter of talentTree. A profile is a contact belonging to your organization. They are typically represented by their headline or primary role. Profile creation features usage of RESTful API to fetch a valid company domain to eliminate any user error.
    - Map: this feature allows users to cross-reference companies with a level and functions to fully map a given space and look for gaps or opportunities in your network. Map creation features use of select2 to allow users to select as many of their companies as possible.

- **Technologies Used:**
    - Front-End: HTML, Bootstrap, JavaScript, jQuery, CSS
    - Back-End: Python, Flask, SQL-Alchemy, PostgreSQL, WTForms

- **Usage:**
    - You can visit talentTree deployed through Render here: https://talenttree.onrender.com/
    - This project was completed using python 3.7.9 (dev)
    - to run this project locally at http://127.0.0.1:5000/ do the following after setting up your virtual environment and initializing Postgres: 
    ```
    (venv)$ git clone https://github.com/rkchitwood/talentTree.git
    (venv)$ pip install -r requirements.txt
    (venv)$ createdb talenttree
    (venv)$ flask run
    ```

- **Contributors:**
    - This project was completed in its entirety by [Ryan Chitwood](https://github.com/rkchitwood)