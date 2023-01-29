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
        random_id = random.randint(10000, 1000000)
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
    questions = relationship('Question', backref='quiz')

    __table_args__ = (
        UniqueConstraint('link'),
    )


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    quiz_id = Column(Integer, ForeignKey('quiz.id'))


Base.metadata.create_all(engine)


# -------------- functions --------------


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


