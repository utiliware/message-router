#!/bin/bash
e=${1:-sandbox}

case $e in
sandbox)
	SelfUpdate=sandbox
	;;

dev)
	SelfUpdate=dev
	;;

*)
  SelfUpdate=sandbox
	;;
esac

echo "$environment...."
company="abc"
stackname="$company-iac-$environment"
region="us-east-1"
path="cloudformation"
template="$path/pipeline.yaml"
RepositoryName="infrastructure"
Image="aws/codebuild/amazonlinux2-x86_64-standard:5.0"
Scope="CLOUDFRONT"
EngineVersion="6.x"
ValkeyEngineVersion="8.1"
DBMasterUsername="db_admin"

aws s3 sync . s3://$CloudformationBucket/$stackname --delete --exclude '*' --include '*.yaml' --include '*.yml' --profile $profile --region $region

echo "Linting..."
# cfn-lint -t $path/* -r $region --non-zero-exit-code informational
find $path/ -name '*.yaml' | tail +1 | while read -r i; do echo "$i" && sam validate --region "${region}" -t "$i" --lint; done
export AWS_PROFILE=$profile
aws cloudformation deploy \
	--stack-name $stackname \
	--region $region \
	--s3-bucket $CloudformationBucket \
	--capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND \
	--template-file $template --parameter-overrides \
	ConnectionArn=$ConnectionArn \
	StackName=$stackname \
	Environment=$environment \
	CloudformationBucket=$CloudformationBucket \
	RepositoryName=$RepositoryName \
	BranchName=$BranchName \
	ClassB=$ClassB \
	Path=$path \
	KeyName=$KeyName \
	Image=$Image \
	RetentionInDays=$RetentionInDays \
	BillingAndScalingMode=$BillingAndScalingMode \
	BackupRetentionPeriod=$BackupRetentionPeriod \
	CacheNodeType=$CacheNodeType \
	NumReplicas=$NumReplicas \
	SnapshotRetentionLimit=$SnapshotRetentionLimit \
	NumShards=$NumShards \
	EngineVersion=$EngineVersion \
	ValkeyEngineVersion=$ValkeyEngineVersion \
	Domain=$Domain \
	CdnDomain=$CdnDomain \
	CdnComplianceDomain=$CdnComplianceDomain \
	CertificateArn=$CertificateArn \
	DLVerifyCertificateArn=$DLVerifyCertificateArn \
	HostedZoneID=$HostedZoneID \
	NotificationArn=$NotificationArn \
	ClusterInstanceCount=$ClusterInstanceCount \
	ClusterInstanceType=$ClusterInstanceType
