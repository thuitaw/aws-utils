import logging
import json
import boto.sqs
from .exceptions import MissingQueueError


class SQSConsumer(object):
    """
    A simple consumer for an sqs queue
    This is meant to be run as a daemon
    """

    def __init__(self, aws_access_key_id, aws_secret_access_key, region, queue_name, logger=None):  # noqa
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region = region
        self.queue_name = queue_name
        self.init_logger(logger)

    def init_logger(self, logger):
        if not logger:
            logger = logging.getLogger("sqs_consumer_logger")
        self.logger = logger

    def connect_to_sqs(self):
        self.logger.info('Connecting to sqs ...')
        conn = boto.sqs.connect_to_region(
            self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key)
        return conn

    def get_queue_arns(self):
        arns = []
        queue = self.get_queue()
        if queue:
            attrs = self.connect_to_sqs().get_queue_attributes(queue)
            policy_json = json.loads(attrs.get('Policy'))
            arns = [s.get('Condition').get('ArnEquals').get('aws:SourceArn')
                    for s in policy_json.get('Statement')]
            self.logger.info('arns: {}'.format(arns))
        return arns

    def get_queue(self):
        queue = self.connect_to_sqs().get_queue(self.queue_name)
        if not queue:
            self.logger.warning(
                'Can not fetch queue: {}'.format(self.queue_name))
            raise MissingQueueError(
                "Cannot get Queue: {}".format(
                    self.queue_name))

        return queue

    def pop_message(self, visibility_timeout=10, wait_time_seconds=15):
        return self.get_queue().read(
            visibility_timeout=visibility_timeout,
            wait_time_seconds=wait_time_seconds)

    def post_process_message(self, message):
        '''
        override this method for custom handling of the message
        after consumption
        for now it just deletes the message
        '''
        message.delete()

    def process_message(self):
        '''
        override this method for custom handling of the message
        on consumption
        '''
        pass

    def process_queue_messages(self):
        while True:
            message = self.pop_message()
            if message:
                self.process_message(message)
                self.post_process_message(message)
