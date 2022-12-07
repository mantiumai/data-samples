## Description

This script fetches data with methods for retrieving information about users and stories from the Hacker News API. The script exports the data to a `JSON` file(list of dictionaries) and a `CSV` file (Filtered data in Pandas DataFrame)

### Steps

- Clone this repository
- Create a Python virtual environment
  ```py
  python3 -m venv env
  ```
- Activate it
  ```
  source env/bin/activate
  ```
- Install the requirements
  ```
   pip3 install -r requirements.txt
  ```
- Run the file `hackernews.py`. By default it fetches the top 20 stories. You can change this by calling appropriate the method or change the parameter of the `stories` method.
