from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:admin@localhost/quiz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "random string"


db = SQLAlchemy(app)

# This is user model which contains basic information for a user.
class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120))
    user_type = db.Column(db.String(120))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)

    @classmethod
    def find_login_user_by_email(cls, email):
        user = cls.query.filter_by(email=email).first()
        return user

    @staticmethod
    def to_json(x):
        return {
            'id': x.id,
            'full_name': x.full_name,
            'email': x.email,
            'user_type': x.user_type
        }

# This is the survey model containing the list of quizes or surveys
class SurveyModel(db.Model):
    __tablename__ = 'survey'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

    @classmethod
    def get_surveys(cls, user_id):
        result = db.engine.execute("SELECT * FROM quiz.survey where is_active=1 and id not in (select survey_id from questions where id in (select question_id from submissions where user_id="+user_id+"))")
        result_as_list = result.fetchall()
        return result_as_list
    
    @staticmethod
    def to_json(x):
        return {
            'id': x.id,
            'name': x.name,
            'description': x.description,
            'is_active': x.is_active
        }

# Question model containg the question for various quizes/surveys
class QuestionModel(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(120))
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    survey = db.relationship('SurveyModel', remote_side='SurveyModel.id',backref='question_survey')

    options = db.relationship('OptionsModel', backref="question_options")

    @staticmethod
    def to_json(x):
        return {
            'id': x.id,
            'question': x.question,
            'survey': x.survey.name,
            'options' : [OptionsModel.to_json(option) for option in x.options],
            'is_active': x.is_active
        }

    @staticmethod
    def to_json_admin(x):
        return {
            'id': x.id,
            'question': x.question,
            'survey': x.survey.name,
            'options' : [OptionsModel.to_json_admin(option) for option in x.options],
            'is_active': x.is_active
        }

# OptionsModel containing the options for a particular question.
class OptionsModel(db.Model):
    __tablename__ = 'options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    option = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship('QuestionModel', remote_side='QuestionModel.id',backref='option_question')

    @staticmethod
    def to_json(x):
        return {
            'id': x.id,
            'option': x.option
        }

    @staticmethod
    def to_json_admin(x):
        return {
            'id': x.id,
            'option': x.option,
            'is_correct':x.is_correct
        }

# Submission model containing information for answers submitted by a particular user.
class SubmissionModel(db.Model):
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship('QuestionModel', remote_side='QuestionModel.id',backref='submission_question')
    user = db.relationship('UserModel', remote_side='UserModel.id',backref='submission_user')
    answer = db.relationship('OptionsModel', remote_side='OptionsModel.id',backref='answer_question')

    

    @staticmethod
    def to_json(x):
        return {
            'id': x.id,
            'question_id': x.question_id,
            'user_id': x.user_id,
            'answer_id':x.answer_id,
            'is_correct': x.is_correct,
            'question': QuestionModel.to_json(x.question),
            'user': UserModel.to_json(x.user),
            'answer': OptionsModel.to_json(x.answer)
        }

db.create_all()
try:
    admin = UserModel(full_name="Adminstrator", email="admin@admin.com", password="password", user_type="admin")
    db.session.add(admin)
    db.session.commit()
except:
    print("Admin Already there")
    pass

# Page that loads intially when the application is launched.
@app.route('/', methods=['GET'])
def index(): 
    return render_template('index.html')
    
@app.route('/acl', methods=['GET'])
def acl():
    return render_template('acl.html')

# Below code contains CRUD operation to display data on various HTML pages.
@app.route('/admin-dashboard', methods=['GET'])
def admin_dashboard():
    try:
        content_type = request.args.get('content_type')
    except:
        content_type = 'survey'

    submissions = SubmissionModel.query.all()

    if content_type == 'questions':
        listData = QuestionModel.query.all()
        for i in range(len(listData)):
            listData[i] = QuestionModel.to_json_admin(listData[i])
    else:
        listData = SurveyModel.query.all()
        for i in range(len(listData)):
            listData[i] = SurveyModel.to_json(listData[i])

    return render_template('admin_dashboard.html', listData = json.dumps(listData), submission_data = [ SubmissionModel.to_json(submission) for submission in submissions])

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user = UserModel(full_name=data['fullname'], email=data['email'], password=data['password'], user_type='user')
    
    db.session.add(user)
    db.session.commit()
    return {
        'message': 'User {} was created.'.format(data['fullname'])
    }

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json

    current_user = UserModel.find_login_user_by_email(data['username'])
    if not current_user:
        return {'message': 'User {} doesn\'t exist'.format(data['id'])}, 400
    if data['password']==current_user.password:
        return {'user':UserModel.to_json(current_user)}, 200
    return {},500

@app.route('/quiz-categories', methods=['GET'])
def quiz():

    user_id = request.args.get('id')

    listSurvey = SurveyModel.get_surveys(user_id)#SurveyModel.query.filter(SurveyModel.is_active==True).all()
    '''for i in range(len(listSurvey)):
        listSurvey[i] = SurveyModel.to_json(listSurvey[i])'''
    return render_template('quiz-cat.html', listSurvey = listSurvey)

@app.route('/<type>/mcq', methods=['GET'])
def question(type):
    questions = QuestionModel.query.filter(QuestionModel.survey_id==type, QuestionModel.is_active==True).all()
    for i in range(len(questions)):
        questions[i] = QuestionModel.to_json(questions[i])
    return render_template('questions.html', questions = questions)

@app.route('/submit-quiz/<user_id>', methods=['POST'])
def submit_quiz(user_id):
    data = request.json

    response = {}

    for i in data:
        print(i, data[i])
        is_correct_answer = OptionsModel.query.filter(OptionsModel.question_id == i, OptionsModel.id == data[i]).first().is_correct
        
        response[i] = is_correct_answer

        submission = SubmissionModel(question_id=i,user_id=user_id,answer_id=data[i],is_correct=is_correct_answer)
        db.session.add(submission)
        db.session.commit()

    return {'result' : response}

@app.route('/survey/<survey_id>', methods=['POST','DELETE'])
def survey_manage(survey_id):
    if request.method == 'POST':
        data = request.json
        survey = SurveyModel(name=data['name'], description=data['description'])
        db.session.add(survey)
        db.session.commit()
    elif request.method == 'DELETE':
        survey = SurveyModel.query.get(survey_id)
        survey.is_active = not survey.is_active
        db.session.commit()
    return {}

@app.route('/questions/<question_id>', methods=['POST','DELETE'])
def question_manage(question_id):
    if request.method == 'POST':
        data = request.json
        survey = SurveyModel.query.filter(SurveyModel.name==data['survey']).first()
        if(survey):
            question = QuestionModel(question=data['question'], survey_id=survey.id)
            db.session.add(question)
            db.session.commit()

            for i in range(4):
                if data['correct']==str(i+1):
                    option_data = OptionsModel(question_id=question.id, option=data['options'][i], is_correct=True)
                else:
                    option_data = OptionsModel(question_id=question.id, option=data['options'][i])
                db.session.add(option_data)
                db.session.commit()
        else:
            return {'message':'No Survey found'},500
    elif request.method == 'DELETE':
        question = QuestionModel.query.get(question_id)
        question.is_active = not question.is_active
        db.session.commit()
    return {}

@app.route('/thank-you', methods=['GET'])
def thank_you():
    return render_template('thank-you.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=True)
