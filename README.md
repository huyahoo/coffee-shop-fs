# Coffee Shop Full Stack

## Backend Environment

### Create a virtual environment
```bash
cd backend
python3 -m venv env
source env/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create .env configuration file
```
AUTH0_DOMAIN=<SPA_DOMAIN>
ALGORITHMS=RS256
API_AUDIENCE=<API_CLIENT>
```

### Run
```bash
export FLASK_APP=src/api.py;
export FLASK_ENV=development;
flask run --reload
```

## Frontend Environment

### Installing Ionic Cli
```bash
sudo npm install -g @ionic/cli
```

### Installing project dependencies
```bash
npm install
```

### Run
```bash
export NODE_OPTIONS=--openssl-legacy-provider
ionic serve
```