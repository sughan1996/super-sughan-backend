from dbmodels.poemsHandler import get_poem_values, get_random_poem
from haikuFoundationApp.jobs.usersHandler import get_user_id_values


def post_profile_controller(event):
  userId = event.get('body', {}).get('userId', None)
  resp = get_user_id_values(userId=userId)
  return resp


def post_home_controller(event):
  output = get_random_poem()
  return output
