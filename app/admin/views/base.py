from starlette_admin import ExportType
from starlette_admin.contrib.sqla.ext.pydantic import ModelView


class BaseModelView(ModelView):
    export_types = [ExportType.EXCEL, ExportType.PDF]
    page_size_options = [5, 10, 25, 50, -1]
