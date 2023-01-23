from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigateway
)
from constructs import Construct

from .generic_lambda import LambdaWithDBPermissions


class DbApiStack(Stack):
    experiment_table = "video_validation_experiment"
    example_table = "example_videos"

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a new Lambda function for the base path response
        base_path_handler = _lambda.Function(self, "BasePathFunction",
                                             runtime=_lambda.Runtime.PYTHON_3_7,
                                             handler="base_path.handler",
                                             code=_lambda.Code.from_asset("lambda"),
                                             )

        update_fn = LambdaWithDBPermissions(self,
                                            "UpdateFunction",
                                            "update_experiment.handler",
                                            self.experiment_table)

        query_processed = LambdaWithDBPermissions(self,
                                                  "QueryProcessedIndexFunction",
                                                  "query_processed.handler",
                                                  self.experiment_table)

        query_example = LambdaWithDBPermissions(self,
                                                "QueryExampleFunction",
                                                "query_example.handler",
                                                self.example_table)

        # Define an API Gateway REST API
        api = apigateway.RestApi(self,
                                 "video-validation-api",
                                 deploy=True, )

        # Add a GET method to the base path resource
        api.root.add_method("GET", apigateway.LambdaIntegration(base_path_handler))

        # Define a resource for the API
        experiment_resource = api.root.add_resource("items")
        # Define a GET method for the resource, connected to the read Lambda function
        read_integration = apigateway.LambdaIntegration(query_processed.lambda_fn)
        experiment_resource.add_method("GET", read_integration)
        # Define a PUT method for the resource, connected to the update Lambda function
        update_integration = apigateway.LambdaIntegration(update_fn.lambda_fn)
        experiment_resource.add_method("PUT", update_integration)

        # Define a resource for the API
        example_resource = api.root.add_resource("examples")
        # Define a GET method for the resource, connected to the read Lambda function
        read_integration = apigateway.LambdaIntegration(query_example.lambda_fn)
        example_resource.add_method("GET", read_integration)