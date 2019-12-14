# DiggiCamp

Scrape your digicampus (that use a very specific single sign-on)


## Usage

```python3
from diggicamp import Diggicamp

# create new instance (session)
d = Diggicamp()

# login with you credentials
d.login("username", "password")

# get a list of all your courses over the semesters
d.get_courses()
```
