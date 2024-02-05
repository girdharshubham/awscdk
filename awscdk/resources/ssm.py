from aws_cdk import aws_ssm as ssm

from constructs import Construct


class DeploymentEnvironmentParameter(Construct):

    def __init__(
        self,
        scope: Construct,
        id: str,
        environment: str,
        name: str,
        description: str = "The environment to deploy to",
        allowed_pattern: str = "^(development|staging|production)$",
    ) -> None:
        super().__init__(scope, id)

        ssm.StringParameter(
            self,
            id,
            parameter_name=f"{name}/{environment}",
            description=description,
            allowed_pattern=allowed_pattern,
            string_value=environment,
        )
