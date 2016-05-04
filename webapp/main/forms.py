from flask.ext.wtf import Form
from wtforms import IntegerField,StringField, SubmitField,RadioField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError



class EditRateForm(Form):
	rate_score = IntegerField("Rate_score",validators=[Required()])
	submit = SubmitField('Submit')
	def validate_rate_score(self,field):
		if field.data<1 or field.data>5:
			raise ValidationError('Rate score must between 1 to 5.')


class EditUserForm(Form):
	"""docstring for EditUserForm"""
	name = StringField('name', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
	age = IntegerField("age",validators=[Required()])
	gender = RadioField("gender_info",choices=[('F','Female'),('M','Male')])
	occupation = StringField('occupation', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Occupation must have only letters, '
                                          'numbers, dots or underscores')])
	submit = SubmitField('Submit')

class EditMovieForm(Form):
	"""docstring for EditMovieForm"""
	title = StringField('title', validators=[Required()])
	imdb_url = StringField('imdb_url', validators=[Required()])
	genre = StringField('genre', validators=[Required(),Regexp('^(?:[01]?\d-)*[01]?\d$',0,
                                          'genre must be xx-xx-xx,xx<19 ')])
	# release_time = StringField('release_time',validators=[Regexp('^\d{4}-\d{2}-\d{2}\s*(?:\d{2}:\d{2}:\d{2})?$',0,
 #                                          'release_time must be xxxx-xx-xx 00:00:00 ')])
	release_time = StringField('release_time',validators=[Regexp('^\d{4}-\d{2}-\d{2}$',0,
                                          'release_time must be xxxx-xx-xx')])
	submit = SubmitField('Submit')



		
