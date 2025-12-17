package aws.security

# 1. Règle IAM : Interdire les permissions "FullAccess" (Trop dangereux)
# Cette règle va vérifier qu'on n'utilise pas AdministratorAccess ou AmazonS3FullAccess
deny[msg] {
  resource := input.Resources[_]
  resource.Type == "AWS::IAM::Role"
  # On vérifie la liste des ManagedPolicyArns
  policy := resource.Properties.ManagedPolicyArns[_]
  contains(policy, "FullAccess")
  msg := sprintf("ALERTE SÉCURITÉ: Le rôle IAM contient une permission 'FullAccess' interdite : %v", [policy])
}

# 2. Règle S3 : Le chiffrement doit être activé obligatoirement
deny[msg] {
  resource := input.Resources[_]
  resource.Type == "AWS::S3::Bucket"
  # On vérifie si la propriété BucketEncryption est absente
  not resource.Properties.BucketEncryption
  msg := "ALERTE SÉCURITÉ: Un Bucket S3 n'a pas de chiffrement activé."
}

# 3. Règle DynamoDB : Le chiffrement doit être activé (NOUVEAU)
# Ajouté pour garantir que votre base de données est aussi conforme
deny[msg] {
  resource := input.Resources[_]
  resource.Type == "AWS::DynamoDB::Table"
  # On vérifie si SSESpecification n'est pas activé
  not resource.Properties.SSESpecification.SSEEnabled
  msg := "ALERTE SÉCURITÉ: La table DynamoDB n'est pas chiffrée (SSE)."
}

# 4. Règle Lambda : Doit être dans un VPC ou avoir du Tracing (Active X-Ray)
deny[msg] {
  resource := input.Resources[_]
  resource.Type == "AWS::Lambda::Function"
  # On vérifie si le TracingConfig est absent ou pas sur 'Active'
  not resource.Properties.TracingConfig.Mode == "Active"
  msg := "ALERTE SÉCURITÉ: Le monitoring (X-Ray Tracing) n'est pas activé sur la Lambda."
}