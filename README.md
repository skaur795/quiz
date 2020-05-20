# Quiz application
Quiz with backend in Flask
# Flask Quiz Application

## Usage

### Create an empty database in mysql

`create database <dbname>`

### Install the requirements

`pip install -r requirements.txt`

### Change DB credentials for sqlAlchemy (Line No. 7)

`app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://<username>:<password>@localhost/<dbname>'`

### Run Flask Application

`python app.py`

### Login use "admin@admin.com/password" to create surveys and questions

### For Testing

#### After running server run test.py in other terminal
