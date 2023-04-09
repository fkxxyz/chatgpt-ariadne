import middleware.latex2text
import middleware.sensitive_replace
import middleware.text2image

middlewares = {
    "latex2text": middleware.latex2text.Latex2TextMiddleware,
    "text2image": middleware.text2image.Text2ImageMiddleware,
    "sensitive_replace": middleware.sensitive_replace.SensitiveReplaceMiddleware,
}

default_middlewares = [
    "latex2text",
    "text2image",
    "sensitive_replace",
]
