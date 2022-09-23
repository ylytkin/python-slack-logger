import logging
import json

try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


class SlackLogFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super(SlackLogFormatter, self).__init__(*args, **kwargs)

    def formatException(self, *args, **kwargs):
        string = super(SlackLogFormatter, self).formatException(*args, **kwargs)

        return f"```{string}```"


class SlackLogHandler(logging.Handler):
    EMOJIS = {
        logging.NOTSET: ':loudspeaker:',
        logging.DEBUG: ':speaker:',
        logging.INFO: ':information_source:',
        logging.WARNING: ':warning:',
        logging.ERROR: ':exclamation:',
        logging.CRITICAL: ':boom:'
    }

    def __init__(
        self,
        webhook_url,
        channel=None,
        username=None,
        emojis=None,
        format='```%(asctime)s\n%(name)s\n%(levelname)s\n\n%(message)s```',
        date_format='%Y-%m-%d %H:%M:%S',
    ):
        logging.Handler.__init__(self)
        self.webhook_url = webhook_url
        self.channel = channel
        self.username = username
        self.emojis = emojis if emojis is not None else SlackLogHandler.EMOJIS
        self.formatter = SlackLogFormatter(fmt=format, datefmt=date_format)

    def _make_content(self, record):
        icon_emoji = getattr(record, 'slack_icon', self.emojis[record.levelno])
        content = {
            'text': self.format(record),
            'icon_emoji': icon_emoji
        }
        if hasattr(record, 'slack_username'):
            content['username'] = getattr(record, 'slack_username')
        elif self.username:
            content['username'] = self.username
        else:
            content['username'] = "{0} - {1}".format(record.module, record.name)
        if self.channel:
            content['channel'] = self.channel
        return content

    def emit(self, record):
        try:
            req = Request(self.webhook_url)
            req.add_header('Content-Type', 'application/json')

            content = self._make_content(record)
            urlopen(req, json.dumps(content).encode("utf-8"))
        except:
            self.handleError(record)
