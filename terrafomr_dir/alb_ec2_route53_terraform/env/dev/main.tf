provider "aws" {
  region     = var.regions["tokyo"]
  access_key = var.access_key
  secret_key = var.secret_key
}

provider "aws" {
  alias  = "us-east-1"
  region = var.regions["virginia"]
}

terraform {
  required_version = "~> 1.3.6"
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
  instance_type      = var.instance_type
  volume_type        = var.volume_type
  volume_size        = var.volume_size
  instance_id        = module.dev.instance_id
  zone_id            = var.zone_id
  zone_name          = var.zone_name
  sub_domain_1       = var.sub_domain_1
}