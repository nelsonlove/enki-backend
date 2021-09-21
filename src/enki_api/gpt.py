from openai.error import AuthenticationError
import gpt_utils


def authenticate_api_key(api_key):
    gpt = gpt_utils.GPT()
    try:
        gpt.response('Test', api_key=api_key)
    except AuthenticationError:
        return False
    return True
