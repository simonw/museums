# niche-museums.com

https://www.niche-museums.com/about

Read [niche-museums.com, powered by Datasette](https://simonwillison.net/2019/Nov/25/niche-museums/) for a detailed explanation of how this all works.

The content on this site (primary contained in `museums.yaml`) is licensed [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Setup

This project uses *[Poetry](https://python-poetry.org/)* to make it easier to setup the appropriate dependencies to run.

Installation steps for *Poetry* can be checked on their [website](https://python-poetry.org/docs/#installation) but for most of the cases this command line would work:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Build the museum database:
```
# On bash
poetry run `pwd`/build.sh
# On fish shell
poetry run (pwd)/build.sh
```

## Run

Start the server:
```
# On bash
poetry run `pwd`/serve.sh
# On fish shell
poetry run (pwd)/serve.sh
```

The address will be printed on the terminal window. The 'Niche Museums' website will be accesible through it.