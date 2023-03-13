from constructs import Construct
from aws_cdk import (
    aws_lambda as _lambda,
    aws_dynamodb as ddb,
    RemovalPolicy
)

class HitCounter(Construct):

    @property
    def handler(self):
        return self._handler

    @property
    def table(self):
        return self._table

    def __init__(self, scope: Construct, construct_id: str,
                downstream: _lambda.IFunction, read_capacity: int = 4, **kwargs):

        # Validation which will throw an error if the read_capacity is not in the allowed range
        if read_capacity < 3 or read_capacity > 20:
                raise ValueError("readCapacity must be greater than 5 or less than 20")

        super().__init__(scope, construct_id, **kwargs)

        # Define dynamodb table
        self._table = ddb.Table(
            self, 'Hits',
            partition_key={'name': 'path', 'type': ddb.AttributeType.STRING},
            encryption=ddb.TableEncryption.AWS_MANAGED,
            read_capacity=read_capacity,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create a lambda function and set it as a property to pass it to the API GW
        self._handler = _lambda.Function(
            self, 'HitCountHandler',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='hitcount.handler',
            environment={
                'DOWNSTREAM_FUNCTION_NAME': downstream.function_name,
                'HITS_TABLE_NAME': self._table.table_name,
            }
        )

        # Give the Lambda’s execution role permissions to read/write from the table
        # and execute dowstream lambda
        self._table.grant_read_write_data(self._handler)
        downstream.grant_invoke(self._handler)