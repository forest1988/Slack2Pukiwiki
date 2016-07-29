# Slack2Pukiwiki
Save Slack logs into Pukiwiki.

## Settings
Install requirements by pip.
```shell
$ pip install -r requirements.txt
```
Copy (or just only rename) the setting file, and write your own API token and other settings.
```shell
$ cp settings.py.original settings.py
```

## How to use
### Simply Get Channel History
```shell
$ python slackAPI.py
```

In the default, you can get messages of yesterday.
If you want to change the range, you can use `--latest` and `--oldest` options as below.

```shell
$ python slackAPI.py --oldest 2016-07-23 --latest 2016-07-29
```

Then, you can get messages from 2016-07-23 to 2016-07-29.


### Slack Backup in Pukiwiki
Get channel history by slackAPI.py, then send it to pukiwiki server by txt2pukiwiki.py.

```shell
$ python slackAPI.py --format pukiwiki
$ python txt2pukiwiki.py -l slackbackup/filelist.txt
```

__You cannot see any update in pukiwiki notification (the left column by default), 
but you can see the new page in 'page list' page.__

You can use both arguments and settings.py for some options.
For example, if you want to use 'pukiwiki' format in slackAPI.py, 
You may write `'FORMAT': 'pukiwiki'` in settings.py, instead of use `--format` option.

'filelist.txt' is overwritten for each time you use 'slackAPI.py'. 
If you want to keep it, please rename or move it properly.

What's more, 
you can use txt2pukiwiki.py not only with slackAPI.py, but also for any text file you want. 
Please enjoy updating your pukiwiki!


## Notice
The scripts are written for __Python 3__. 
We coded them to be compatible with __Python 2__, but there perhaps remain some bugs. 
Please feel free to ask us if you have trouble using them. 


## TIPS
### 'pip install requirements' fails
- Maybe your account don't have correct permission. Please try using sudo.
```shell
$ sudo pip install -r requirements
```

- Maybe your pip version is too old. Please try updating pip.
```shell
$ pip install pip --upgrade
```


### 'import paramiko' error
Maybe 'cryptography' module doesn't work well. Please try reinstalling it.
```shell
$ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
$ sudo pip install cryptography --force-reinstall
```


### ssh key not found
Try not using ~/ as $HOME. 

