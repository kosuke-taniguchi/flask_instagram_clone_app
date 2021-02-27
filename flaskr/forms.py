from wtforms import StringField, TextAreaField, PasswordField, SubmitField, FileField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Email
from wtforms.form import Form


class SignupForm(Form):
    picture_path = FileField('トップ画像の選択')
    username = StringField('ユーザー名', validators=[DataRequired()])
    email = StringField('メールアドレス', validators=[DataRequired(), Email('メールアドレスが誤っています')])
    password = PasswordField('パスワード', validators=[DataRequired(), EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('確認用パスワード', validators=[DataRequired()])
    submit = SubmitField('登録')


class LoginForm(Form):
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired(),])
    submit = SubmitField('ログイン')


class PostForm(Form):
    picture_path = FileField('画像を選択')
    content = TextAreaField('コンテンツ')
    author = HiddenField('', validators=[DataRequired()])
    submit = SubmitField('投稿')


class EditProfileForm(Form):
    picture_path = FileField('トップ画像の選択')
    username = StringField('ユーザー名', validators=[DataRequired()])
    profile_comment = TextAreaField('コメント')
    submit = SubmitField('編集する')


class CommentForm(Form):
    author = HiddenField('', validators=[DataRequired()])
    content = TextAreaField('コメント', validators=[DataRequired()])
    submit = SubmitField('コメントする')


class EditPostForm(Form):
    content = TextAreaField('コンテンツ')
    submit = SubmitField('投稿')


class SearchForm(Form):
    search_content = StringField('', validators=[DataRequired()])
    submit = SubmitField('探す')


class SearchFriendsForm(Form):
    username = StringField('', validators=[DataRequired()])
    submit = SubmitField('探す')