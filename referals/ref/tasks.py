from core.celery import app
from .models import Refcode

@app.task
def expire_code(code_id):

    code = Refcode.objects.filter(id=code_id).first()
    if code:
        code.is_active = False
        code.save()