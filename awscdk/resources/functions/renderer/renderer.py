import boto3


def template(**kwargs):
    return {
        "values": {
            "controller": {
                "replicaCount": kwargs["replica"]
            }
        }
    }


def handler(event, context):
    ssm = boto3.client("ssm")

    parameter_name = event["parameter_name"]
    response = ssm.get_parameter(Name=parameter_name, WithDecryption=False)
    environment = response["Parameter"]["Value"]
    match environment:
        case "development":
            return template(replica=1)
        case "staging":
            return template(replica=2)
        case "production":
            return template(replica=2)
