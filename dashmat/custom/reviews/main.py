from dashmat.core_modules.base import Module

class Reviews(Module):
    @classmethod
    def dependencies(kls):
        yield "dashmat.core_modules.components.main:Components"

