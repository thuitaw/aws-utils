import logging
import os
import boto
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from .exceptions import (
    InvalidBucketNameError, BucketCreationError, NonExistentBucketError,
    MissingFileError, NonExistentKeyError)


class S3Connector(object):
    """
    Inorder to upload a file to S3, one needs
        1) To create a bucket (or at least have access to one)
        2) Create a new key, that is attached to the bucket
        3) Use the created key to upload a file

        The bucket_name, and the key name should all be unique
    """
    def __init__(self, aws_access_key_id, aws_secret_access_key, host, logger=None):  # noqa
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.host = host
        self.init_logger(logger)

    def init_logger(self, logger):
        if not logger:
            logger = logging.getLogger("s3_connector_logger")

        self.logger = logger

    def connect_to_s3(self):
        self.logger.info('Connecting to s3 ...')
        conn = S3Connection(
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            host=self.config.s3.host)
        return conn

    def create_new_bucket(self, name):
        if not name:
            raise InvalidBucketNameError
        conn = self.connect_to_s3()
        try:
            bucket = conn.create_bucket(name)
            return bucket
        except boto.exception.S3CreateError as e:
            self.logger.exception(
                "Failed to create bucket {exception}".format(
                    exception=e))
            raise BucketCreationError(e.message)

    def get_bucket(self, name):
        conn = self.connect_to_s3()
        try:
            bucket = conn.get_bucket(name)
            return bucket
        except boto.exception.S3ResponseError as e:
            self.logger.exception(
                "Failed to fetch bucket {exception}".format(
                    exception=e))
            raise NonExistentBucketError(e.message)

    def create_key(self, bucket, key_name):
        '''
        key name can also be thought of as the file name
        on s3
        '''
        key = Key(bucket)
        key.key = key_name
        self.logger.info("Created bucket key: {key}".format(
            key=key_name))
        return key

    def upload_from_file(self, bucket_name, key_name, file_path, **kwargs):
        if not os.path.isfile(file_path):
            self.logger.exception(
                "Missing file, or wrong file path provided")
            raise MissingFileError
        bucket = self.get_bucket(bucket_name)
        key = self.create_key(bucket, key_name)
        file_size = key.set_contents_from_filename(file_path, **kwargs)
        self.logger.info("uploaded file of size {size} from path {path}".format(
            size=file_size, path=file_path))
        return key

    def upload_from_string(self, bucket_name, key_name, contents, **kwargs):
        bucket = self.get_bucket(bucket_name)
        key = self.create_key(bucket, key_name)
        key.set_contents_from_string(contents, **kwargs)
        return key

    def update_item_from_string(self, bucket_name, old_key_name, new_key_name, contents, mime_type, **kwargs): # noqa
        bucket = self.get_bucket(bucket_name)
        key = bucket.get_key(old_key_name)
        if key:
            self.delete_file(bucket_name, old_key_name)
            self.upload_image_as_string(
                bucket_name=bucket_name,
                key_name=new_key_name,
                contents=contents, mime_type=mime_type, **kwargs)
        raise NonExistentKeyError

    def upload_image_as_string(self, bucket_name, key_name, contents, mime_type, **kwargs): # noqa
        bucket = self.get_bucket(bucket_name)
        key = self.create_key(bucket, key_name)
        key.set_metadata('Content-Type', mime_type)
        key.set_contents_from_string(contents, **kwargs)
        return key

    def delete_file(self, bucket_name, key_name, **kwargs):
        bucket = self.get_bucket(bucket_name)
        return bucket.delete_key(key_name)

    def delete_files(self, bucket_name, key_list, **kwargs):
        bucket = self.get_bucket(bucket_name)
        return bucket.delete_keys(key_list)
