##Web Instance
resource "aws_instance" "ec2-web" {
  ami       = var.ami
  subnet_id = var.public_subnet_ids[0]
  vpc_security_group_ids = [
    aws_security_group.common.id,
    aws_security_group.ec2.id
  ]
  key_name      = aws_key_pair.key.id
  instance_type = var.instance_type
  root_block_device {
    volume_type = var.volume_type
    volume_size = var.volume_size
  }

  tags = {
    Name = "${var.general_config["project"]}-${var.general_config["env"]}-web01"
  }
}

##DB Instance
resource "aws_instance" "ec2-db" {
  ami       = var.ami
  subnet_id = var.private_subnet_ids[0]
  vpc_security_group_ids = [
    aws_security_group.common.id,
  ]
  key_name      = aws_key_pair.key.id
  instance_type = var.instance_type
  root_block_device {
    volume_type = var.volume_type
    volume_size = var.volume_size
  }

  tags = {
    Name = "${var.general_config["project"]}-${var.general_config["env"]}-db01"
  }
}

##Elastic IP
resource "aws_eip" "eip_ec2" {
  vpc      = true
  instance = aws_instance.ec2-web.id

  tags = {
    Name = "${var.general_config["project"]}-${var.general_config["env"]}-eip01"
  }
}

##Key Pair
resource "aws_key_pair" "key" {
  key_name   = var.key_name
  public_key = file("~/.ssh/example.pub")
}