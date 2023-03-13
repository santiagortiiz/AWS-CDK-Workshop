from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
)

class HitCounter(Construct):

    @property
    def handler(self):
        return self._handler

    def __init__(self, scope: Construct, construct_id: str, downstream: _lambda.IFunction, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # Define dynamodb table
        table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING}
        )

        # Create a lambda function and set it as a property to pass it to the API GW
        self._handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='hitcount.handler',
            environment={
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': table.table_name,
            }
        )

        # Give the Lambda’s execution role permissions to read/write from the table
        # and execute dowstream lambda
        table.grant_read_write_data(self._handler)
        downstream.grant_invoke(self._handler)