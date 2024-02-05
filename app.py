#!/usr/bin/env python3
import os
from typing import Dict

import aws_cdk as cdk
from awscdk.stack import App

app = cdk.App()

App(
    app, "Dev",
    env=cdk.Environment(
        account=os.getenv("CDK_DEFAULT_ACCOUNT"),
        region='ap-south-1'
    ),
    environment="development",
    helm_charts={
        "IngressNginx": {
            "chart": "ingress-nginx",
            "repository": "https://kubernetes.github.io/ingress-nginx",
            "namespace": "ingress-nginx",
            "createNamespace": True,
            "values": {
                "controller": {
                    "replicaCount": 1
                }
            }
        }
    })
app.synth()
