import logging
import boto.sns


class SNSPubSubConnector(object):


    def __init__(self, aws_access_key_id, aws_secret_access_key, region, logger=None):  # noqa
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region = region
        self.init_logger(logger)

    def init_logger(self, logger):
        if not logger:
            logger = logging.getLogger("sns_pub_sub_logger")
        self.logger = logger

    def get_sns_conn(self):
        return boto.sns.connect_to_region(
            self.region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key)

    def get_topics_from_aws(self):
        topics = self.get_sns_conn().get_all_topics()
        self.logger.debug("AWS Topic fetched: %s" % topics)
        return topics

    def get_topics(self):
        if not hasattr(self, 'sns_topics'):
            topics = self.get_topics_from_aws()
            self.sns_topics = topics['ListTopicsResponse']['ListTopicsResult']['Topics']  # noqa
        return self.sns_topics

    def get_arn_for_topic(self, topic_name):
        self.logger.debug("Fetching ARN for %s" % topic_name)
        for topic in self.get_topics():
            if topic['TopicArn'].split(":")[-1] == topic_name:
                return topic['TopicArn']

    def sns_notify(self, topic_name, subject, json_message):
        self.logger.debug(
            "SNS Notify %s:%s %s" % (topic_name, subject, json_message))
        topic_arn = self.get_arn_for_topic(topic_name)
        self.get_sns_conn().publish(
            topic_arn,
            message=json_message,
            subject=subject)
