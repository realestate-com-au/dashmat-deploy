from dashmat.core_modules.base import Module

class Scaling(Module):
    @classmethod
    def npm_deps(kls):
        return {
              "react-bootstrap": "^0.28.1"
            }

    @classmethod
    def dependencies(kls):
        yield "dashmat.core_modules.amazon_base.main:AmazonBase"
        yield "dashmat.core_modules.components.main:Components"
        yield "dashmat.core_modules.bootstrap.main:BootStrap"
