# The base API gateway resource
resource "aws_api_gateway_rest_api" "api_gateway" {
  name = "api-gateway-${local.env}"
}
