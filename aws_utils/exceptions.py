class S3Exception(Exception):
    pass


class InvalidBucketNameError(S3Exception):
    pass


class BucketCreationError(S3Exception):
    pass


class NonExistentBucketError(S3Exception):
    pass


class MissingFileError(S3Exception):
    pass


class NonExistentKeyError(S3Exception):
    pass


class MissingQueueException(Exception):
    pass
