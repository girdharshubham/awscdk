import json
import os

from aws_cdk import (
    aws_lambda as l,
    aws_iam as iam,
    custom_resources as cr,
    CfnOutput
)
from constructs import Construct


class HelmValue(Construct):
    def __init__(self,
                 scope: Construct,
                 id: str,
                 environment: str
                 ) -> None:
        super().__init__(scope, id)

        with open(f"{os.getcwd()}/awscdk/resources/functions/renderer/renderer.py", encoding="utf8") as code:
            handler = code.read()

        policy = iam.PolicyStatement(actions=["ssm:GetParameter"], resources=["*"])
        func = l.Function(self,
                          f"{id}Function",
                          code=l.Code.from_inline(handler),
                          runtime=l.Runtime.PYTHON_3_10,
                          handler="index.handler",
                          initial_policy=[policy],
                          )

        custom_resource = cr.AwsCustomResource(
            self,
            f"{id}CustomResource",
            on_update=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                physical_resource_id=cr.PhysicalResourceId.of("Trigger"),
                parameters={
                    "FunctionName": func.function_name,
                    "InvocationType": "RequestResponse",
                    "Payload": json.dumps({
                        "parameter_name": environment
                    })
                },
            ),
            policy=cr.AwsCustomResourcePolicy.from_statements([
                iam.PolicyStatement(
                    actions=["lambda:InvokeFunction"],
                    resources=[func.function_arn]
                )
            ])
        )

        CfnOutput(self, f"{id}HelmValueOutput",
                  value=custom_resource.get_response_field("values"),
                  export_name="IngressReplicaCount"
                  )
