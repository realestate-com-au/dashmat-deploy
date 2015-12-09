from python_dashing.core_modules.base import Module

class Charts(Module):
    relative_to = "custom.charts"

    @property
    def javascript(self):
        yield "chart.js"
