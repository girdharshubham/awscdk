import boto3


def template(**kwargs):
    return {"values": {"controller": {"replicaCount": kwargs["replica"]}}}


def handler(event, context):
    ssm = boto3.client("ssm")

    parameter_name = event["parameter_name"]
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=False)
    environment = response["Parameter"]["Value"]
    if environment == "development":
        return template(replica=1)
    elif environment == "staging":
        return template(replica=3)
    elif environment == "production":
        return template(replica=3)
    else:
        return template(replica=0)
