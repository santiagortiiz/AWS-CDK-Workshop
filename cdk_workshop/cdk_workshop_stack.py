from constructs import Construct
from aws_cdk import (
    # Duration,
    Stack,
    # aws_iam as iam,
    # aws_sqs as sqs,
    # aws_sns as sns,
    # aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)

from cdk_dynamo_table_view import TableViewer
from .hitcounter import HitCounter


class CdkWorkshopStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        lambda_backend = _lambda.Function(
            self, 'BackendLogic',
            runtime=_lambda.Runtime.PYTHON_3_7,
            code=_lambda.Code.from_asset('lambda'),
            handler='hello.handler',
        )

        lambda_counter = HitCounter(
            self, 'EndpointHitCounter',
            downstream=lambda_backend,
        )

        apigw.LambdaRestApi(
            self, 'CDKWorkshopAPI',
            # handler=backend,
            handler=lambda_counter._handler,
        )

        TableViewer(
            self, 'ViewHitCounter',
            title='Hello Hits',
            table=lambda_counter.table,
        )

        # queue = sqs.Queue(
        #     self, "CdkWorkshopQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        # topic = sns.Topic(
        #     self, "CdkWorkshopTopic"
        # )

        # topic.add_subscription(subs.SqsSubscription(queue))
