import time

from sqlalchemy import (create_engine, Integer, Text,
                        String, Column, DateTime, ForeignKey, Boolean,
                        UniqueConstraint, column)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone, timedelta
import random
from sqlalchemy.orm import relationship, Session

engine = create_engine('sqlite:///quiz.db')
engine.connect()
session = Session(engine)
Base = declarative_base()


def random_id_for_quiz_link():
    random_id = random.randint(10000, 1000000)
    all_id = tuple(*session.query(column("Quiz.id")).all())
    if random_id in all_id:
        new_random_id = random.randint(10000, 1000000)
        return new_random_id
    return random_id


class Quiz(Base):
    __tablename__ = "quiz"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    title = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    create_link = random.randint(100000, 1000000)
    link = Column(Integer, default=random_id_for_quiz_link())
    offset = timedelta(hours=6)
    created_on = Column(DateTime(), default=datetime.now(tz=timezone(offset)))
    questions = relationship('Question', backref='quiz', cascade='delete')
    answers = relationship('Answer', cascade='delete')

    __table_args__ = (
        UniqueConstraint('link'),
    )


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    quiz_id = Column(Integer, ForeignKey('quiz.id'))


class Answer(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=True)
    answer = Column(Text, nullable=False)
    offset = timedelta(hours=6)
    time = Column(DateTime(), default=datetime.now(tz=timezone(offset)))
    question_id = Column(Integer, ForeignKey('questions.id'))
    quiz_id = Column(Integer, ForeignKey('quiz.id'))


Base.metadata.create_all(engine)


# -------------- functions --------------

def answers_by_question_id(q_id):
    answers = session.query(Answer).filter(Answer.question_id == q_id)
    return answers


def answers_by_quiz_id(id):
    answers = session.query(Answer).filter(Answer.quiz_id == id)
    return answers


def all_answers():
    answers = session.query(Answer).order_by('-id')
    return answers


def create_answer(data: dict):
    answer_obj = Answer(
        username=data['username'],
        user_id=data['user_id'],
        quiz_id=data['quiz_id'],
        answer=data['answer'],
        question_id=data['question_id'],
    )
    session.add(answer_obj)
    session.commit()


def delete_answer(id):
    answer = session.query(Answer).get(id)
    session.delete(answer)
    session.commit()


def create_quiz(data: dict):
    """
    Передай user_id, is_anon, title, description.
    Возвращает id опроса.
    """
    quiz_obj = Quiz(
        user_id=data['user_id'],
        is_anonymous=data['is_anon'],
        title=data['title'],
        description=data['description'],
    )
    session.add(quiz_obj)
    session.commit()
    return quiz_obj.id


def delete_quiz(id):
    quiz = session.query(Quiz).get(id)
    session.delete(quiz)
    session.commit()


def get_quiz(id):
    quiz = session.query(Quiz).get(id)
    return quiz


def get_my_quiz(user_id):
    my_quiz = session.query(Quiz).filter(Quiz.user_id == user_id)
    return my_quiz


def create_question(data: dict):
    question_obj = Question(
        question=data['question'],
        quiz_id=data['quiz_id'],
    )
    session.add(question_obj)
    session.commit()


def delete_question(id):
    question = session.query(Question).get(id)
    session.delete(question)
    session.commit()


def delete_all_questions(quiz_id):
    questions = session.query(Question).filter(Question.quiz_id == quiz_id)
    questions.delete()
    session.commit()


def get_quiz_questions(quiz_id):
    quiz = session.query(Quiz).get(quiz_id)
    questions_text = [i.question for i in quiz.questions]
    return questions_text


def get_questions_by_id(id: int):
    q_text = []
    questions = session.query(Question).filter(Question.quiz_id == id).all()
    for q in questions:
        q_text.append(q.question)

    return q_text


def get_questions_objects_by_id(id):
    questions = session.query(Question).filter(Question.quiz_id == id).all()
    q_obj = [q for q in questions]
    return q_obj


def get_one_question(q_id):
    question = session.query(Question).get(int(q_id)).question
    return question


def get_questions_objects(quiz_id):
    quiz = session.query(Quiz).get(quiz_id)
    questions_objects = [i for i in quiz.questions]
    return questions_objects


def change_quiz_anonymity(quiz_id):
    '''
    :param quiz_id:
    :return: str value for string
    '''

    quiz = get_quiz(quiz_id)
    status = quiz.is_anonymous
    if status:
        quiz.is_anonymous = False
        session.commit()
        return 'не анонимный'
    else:
        quiz.is_anonymous = True
        session.commit()
        return 'анонимный'


def change_quiz_title(quiz_id, new_title):
    quiz = get_quiz(quiz_id)
    quiz.title = new_title
    session.commit()


def change_quiz_content(quiz_id, new_description):
    quiz = get_quiz(quiz_id)
    quiz.description = new_description
    session.commit()


def get_all_links_id():
    all_quiz = session.query(Quiz.link).all()
    id_without_tuple = [i[0] for i in all_quiz]
    return id_without_tuple


def find_by_link(link):
    quiz = session.query(Quiz).filter(Quiz.link == link).all()
    return quiz
