from aws_cdk import (
    aws_s3 as s3,
    core as cdk
)

class VotingFrontendStack(cdk.Stack):
  def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    bucket = s3.Bucket(self,
      "FrontendBuckets",
      public_read_access=True,
      versioned=True,)
