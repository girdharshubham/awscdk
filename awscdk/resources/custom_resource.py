import json
import os

from aws_cdk import aws_lambda as l, aws_iam as iam, custom_resources as cr, CfnOutput
from constructs import Construct


class HelmValue(Construct):
    __custom_resource: cr.AwsCustomResource

    def __init__(self, scope: Construct, id: str, ssm_parameter_base: str, environment: str) -> None:
        super().__init__(scope, id)

        with open(f"{os.getcwd()}/awscdk/resources/functions/renderer/renderer.py", encoding="utf8") as handler:
            code = handler.read()

        policy = self.__generate_lambda_default_ssm_policy()
        func = self.__register_function(code, policy)
        self.__custom_resource = self.__register_custom_resource(func, ssm_parameter_base, environment)

    def __generate_lambda_default_ssm_policy(self, actions=None,
                                             resources=None) -> iam.PolicyStatement:
        if resources is None:
            resources = ["*"]
        if actions is None:
            actions = ["ssm:GetParameter"]

        return iam.PolicyStatement(actions=actions, resources=resources)

    def __register_function(self, code, policy, handler="index.handler", runtime=l.Runtime.PYTHON_3_10) -> l.Function:
        return l.Function(
            self,
            f"{id}CRFunction",
            code=l.Code.from_inline(code),
            runtime=runtime,
            handler=handler,
            initial_policy=[policy],
        )

    def __register_custom_resource(self, func, ssm_parameter_base, environment) -> cr.AwsCustomResource:
        return cr.AwsCustomResource(
            self,
            f"{id}CR",
            on_update=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                physical_resource_id=cr.PhysicalResourceId.of("Trigger"),
                parameters={
                    "FunctionName": func.function_name,
                    "InvocationType": "RequestResponse",
                    "Payload": json.dumps(
                        {"parameter_name": f"{ssm_parameter_base}/{environment}"}
                    ),
                },
            ),
            on_create=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                physical_resource_id=cr.PhysicalResourceId.of("Trigger"),
                parameters={
                    "FunctionName": func.function_name,
                    "InvocationType": "RequestResponse",
                    "Payload": json.dumps(
                        {"parameter_name": f"{ssm_parameter_base}/{environment}"}
                    ),
                },
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements(
                [
                    iam.PolicyStatement(
                        actions=["lambda:InvokeFunction"], resources=[func.function_arn]
                    )
                ]
            ),
        )

    def register_output(self) -> CfnOutput:
        return CfnOutput(
            self,
            f"{id}CRResponse",
            value=self.__custom_resource.get_response_field("Payload"),
            export_name="CRResponse",
        )
