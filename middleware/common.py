from dataclasses import dataclass


@dataclass
class MessageMiddlewareArguments:
    force_image: bool = False
    image_converted: bool = False
    sensitive_replaced: bool = False
