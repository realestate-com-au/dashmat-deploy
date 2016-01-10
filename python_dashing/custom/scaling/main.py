from python_dashing.core_modules.base import Module

class Scaling(Module):
    @classmethod
    def npm_deps(kls):
        return {
              "react-bootstrap": "^0.28.1"
            }

    @classmethod
    def dependencies(kls):
        yield "python_dashing.core_modules.amazon_base.main:AmazonBase"
        yield "python_dashing.core_modules.components.main:Components"
        yield "python_dashing.core_modules.bootstrap.main:BootStrap"
