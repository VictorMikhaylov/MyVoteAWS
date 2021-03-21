from aws_cdk.core import Stack, Construct
from aws_cdk.aws_s3 import Bucket


class VotingFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = Bucket(
            self,
            id="voting-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )
