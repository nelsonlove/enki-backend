from openai.error import AuthenticationError
from gpt_utils import GPT
from gpt_utils.prompt import BasePrompt


def authenticate_api_key(api_key):
    gpt = GPT()
    try:
        gpt.response('Test', api_key=api_key)
    except AuthenticationError:
        return False
    return True


class ListPrompt(BasePrompt):
    def __init__(self,
                 intro_text=None,  # Text inserted at beginning of prompt
                 *items,  # Sequence of items used to build prompt
                 separator='\n- ',  # Separator for items, defaults to putting one item on each line
                 auto_truncate=False,  # If true, prompt will be truncated if its length > max_tokens
                 max_tokens=2048,
                 final_text='',
                 ):
        self.items = list(items)
        self.separator = separator
        self.intro_text = intro_text
        self.auto_truncate = auto_truncate
        self.max_tokens = max_tokens
        self.final_text = final_text

    def truncate(self):
        self.items = self.items[1:]

    @property
    def text(self):
        prompt = self.intro_text + '\n\n' if self.intro_text else ''
        prompt += self.separator.join(self.items)
        if self.final_text:
            prompt += self.separator + self.final_text
        return prompt.strip()

    def format(self, *args, **kwargs):
        while self.auto_truncate and len(self.text) > self.max_tokens:
            self.truncate()
        return self.text


def get_reply(
        prompt,
        messages
):
    temperature = prompt.temperature / 100
    frequency_penalty = prompt.variety / 100

    min_tokens = 10
    max_tokens = 512
    verbosity_multiplier = prompt.verbosity / 100
    max_tokens = int(min_tokens + (max_tokens - min_tokens) * verbosity_multiplier)

    prompt = ListPrompt(
        prompt.intro,
        *[message.sender + ': ' + message.text for message in messages],
        auto_truncate=True,
        max_tokens=2048-max_tokens,
        separator='\n',
        final_text=prompt.bot + ': '
    )

    reply = GPT(
        engine="davinci",
        stop='\n',
        max_tokens=max_tokens,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
    ).response(prompt.text)

    return reply
