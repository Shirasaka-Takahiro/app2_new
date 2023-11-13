provider "aws" {
  profile = "terraform_python_test"
  region  = var.regions["tokyo"]
}

provider "aws" {
  profile = "terraform_python_test"
  alias   = "us-east-1"
  region  = var.regions["virginia"]
}

terraform {
  required_version = "~> 1.3.6"
  #backend "s3" {
  #  bucket  = "example-dev-tfstate-bucket"
  #  region  = "ap-northeast-1"
  #  key     = "dev.tfstate"
  #  profile = "terraform-user"
  #}
  backend "local" {
     path   = "terraform.tfstate"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "4.49.0"
    }
  }
}

module "dev" {
  source = "../../module"

  general_config     = var.general_config
  regions            = var.regions
  availability_zones = var.availability_zones
  vpc_cidr           = var.vpc_cidr
  public_subnets     = var.public_subnets
  private_subnets    = var.private_subnets
  public_subnet_ids  = module.dev.public_subnet_ids
  private_subnet_ids = module.dev.private_subnet_ids
  ami                = var.ami
  key_name           = var.key_name
  #public_key_path    = var.public_key_path
  instance_type      = var.instance_type
  volume_type        = var.volume_type
  volume_size        = var.volume_size
  instance_id        = module.dev.instance_id
}