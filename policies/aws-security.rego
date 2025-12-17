package aws.security

# Interdire IAM FullAccess
deny[msg] {
  resource := input.Resources[_]
  resource.Type == "AWS::IAM::Role"
  policy := resource.Properties.ManagedPolicyArns[_]
  contains(policy, "FullAccess")
  msg := "IAM Role trop permissif (FullAccess interdit)"
}

# S3 doit être chiffré
deny[msg] {
  resource := input.Resources[_]
  resource.Type == "AWS::S3::Bucket"
  not resource.Properties.BucketEncryption
  msg := "Bucket S3 sans chiffrement"
}
