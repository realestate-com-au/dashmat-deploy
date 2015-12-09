from python_dashing.core_modules.base import Module

class Scaling(Module):
    relative_to = "custom.scaling"

    @classmethod
    def dependencies(kls):
        yield "python_dashing.core_modules.amazon_base.main:AmazonBase"

    @property
    def css(self):
        yield "scaling.css"
