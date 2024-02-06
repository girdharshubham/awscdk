export SYSTEM_MASTER := $(shell aws sts get-caller-identity | jq -r '.Arn')

.PHONY: deploy
deploy: cleanup
	@echo "Deploying environment: $(env) | $(region) | $(aws_profile)"
	@cdk deploy $(env) -O cdk-output.json --profile $(aws_profile) && \
	helm_values=$$(cat cdk-output.json | jq -r ".$(env)|keys[]") && \
	cat cdk-output.json | jq -r --arg key "$$helm_values" ".$(env)[$$key]" | jq -r .values | yq -P >values.yml && \
	eks_cluster=$$(aws eks list-clusters --region $(region) --profile $(aws_profile) | jq -r '.clusters[0]') && \
	aws eks update-kubeconfig --region $(region) --profile $(aws_profile) --name $$eks_cluster && \
	helm upgrade --install ingress-nginx ingress-nginx \
      --repo https://kubernetes.github.io/ingress-nginx \
      --namespace ingress-nginx --create-namespace -f values.yml

.PHONY: cleanup
cleanup:
	@rm -f values.yml cdk-output.json


.PHONY: destroy
destroy: cleanup
	@echo "Deploying environment: $(env) | $(region) | $(aws_profile)"
	eks_cluster=$$(aws eks list-clusters --region $(region) --profile $(aws_profile) | jq -r '.clusters[0]') && \
	aws eks update-kubeconfig --region $(region) --profile $(aws_profile) --name $$eks_cluster && \
	helm uninstall ingress-nginx -n ingress-nginx && \
	cdk destroy $(env) --profile $(aws_profile)
