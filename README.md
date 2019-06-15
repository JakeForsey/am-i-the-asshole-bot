# am-i-the-asshole-bot
Bot that judges submissions to reddit.com/r/AmItheAsshole/

<img src="assets/anubis-icon.png" alt="anubis-icon" width="200"/><img src="assets/aita-icon.png" alt="aita-icon" width="200"/>

# Installation
## Windows (not tested)
```
pip install virtualenv
virtualenv env -p python36
env\Scripts\activate
pip install -r requirements.txt

# Add src/bot to PYTHONPATH
```

## Ubuntu (not tested)
```
pip install virtualenv
virtualenv env -p python36
source env/bin/activate
pip install -r requirements.txt

# Add src/bot to PYTHONPATH

crontab -e

# Add something like to scrape data every two hours: 
0 */2 * * * /path/to/env/bin/python /path/to/am-i-the-asshole-bot/src/bot/main.py --mode scrape
```