from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, FileField
from wtforms.validators import DataRequired, Email, Optional
from flask_wtf.file import FileAllowed

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[Optional()])
    subject = StringField('Subject', validators=[Optional()])
    message = TextAreaField('Message', validators=[DataRequired()])

class StandForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[Optional()])
    location = StringField('Location')
    size = StringField('Size')
    status = SelectField('Status', choices=[('Available', 'Available'), ('Sold', 'Sold'), ('Reserved', 'Reserved')])
    map_embed = TextAreaField('Map Embed Code')
    featured = BooleanField('Featured')
    images = FileField('Images', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    excerpt = TextAreaField('Excerpt')
    status = SelectField('Status', choices=[('Draft', 'Draft'), ('Published', 'Published'), ('Featured', 'Featured')])
    featured_image = FileField('Featured Image', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
