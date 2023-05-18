from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm, CreateForm

from werkzeug.utils import secure_filename
import os

from app.BBDB import BBDB
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import pickle
import uuid
#h2938366.stratoserver.net
#
#
#
#MOVED TO __init__.py FOR BETTER IMPORTS
#
#


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Thanks for logging in')
        user = {'username': form.username.data}

        db = BBDB("h2938366.stratoserver.net")
        pic = np.asarray(form.picture.data)
        #pic = np.asarray(mpl.image.imread('uploads/' + filename))
        db.insertPicture(pic, uuid.uuid4(), 'backend.pictures')
        #face_recognition(form.picture.data, username)
        return render_template('validationauthenticated.html', ra='a',  user=user)
    return render_template('login.html',  title='Sign In', form=form)


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateForm()
    if form.validate_on_submit():
        flash('Thanks for logging in')
        user = {'username': form.username.data}
        return render_template('validationauthenticated.html', ra='r', user=user)
    return render_template('create.html',  title='Sign In', form=form)
