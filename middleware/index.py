import middleware.latex2text
import middleware.sensitive_replace
import middleware.text2image
import middleware.ocr

middlewares_in = {
    "ocr": middleware.ocr.OcrMiddleware,
}
middlewares_out = {
    "latex2text": middleware.latex2text.Latex2TextMiddleware,
    "text2image": middleware.text2image.Text2ImageMiddleware,
    "sensitive_replace": middleware.sensitive_replace.SensitiveReplaceMiddleware,
}

default_middlewares_in = [
    "ocr",
]
default_middlewares_out = [
    "latex2text",
    "text2image",
    "sensitive_replace",
]
