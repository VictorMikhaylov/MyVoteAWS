from aws_cdk.core import Stack, Construct
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode

class VotingStorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        votes_table = Table(self, 
            id = "Votes",
            partition_key=Attribute(
                name="voter",
                type=AttributeType.STRING
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )
