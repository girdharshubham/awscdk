#!/usr/bin/env python3
import os

import aws_cdk as cdk
from awscdk.stack import App

app = cdk.App()

App(
    app,
    "Dev",
    env=cdk.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")),
    environment="development",
    # use cfnoutput internally instead of using the makefile
    system_master=os.getenv("SYSTEM_MASTER"),
    # TODO | ingress nginx is integrated through the makefile at them moment, but the ideal way would be to do it through aws cdk. aws_eks supports helm charts.
    # The missing bit is to integrate the cfnoutput to work with aws_eks helm chart bit
    helm_charts={
        "IngressNginx": {
            "chart": "ingress-nginx",
            "repository": "https://kubernetes.github.io/ingress-nginx",
            "namespace": "ingress-nginx",
            "createNamespace": True,
            "values": {"controller": {"replicaCount": 1}},
        }
    },
)
app.synth()
