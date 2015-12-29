from python_dashing.core_modules.base import Module

class Reviews(Module):
    @classmethod
    def dependencies(kls):
        yield "python_dashing.core_modules.components.main:Components"

