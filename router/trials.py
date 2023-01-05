from celery import group
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from tasks.clicks import celery_trials
from celery_config.celery_utils import get_task_info

from core.constants import is_celery_working

router = APIRouter(prefix='/trials', tags=['Celery Trials'], responses={404: {"description": "Not found"}})


@router.post("/async")
def get_task():
	if is_celery_working():
		task = celery_trials.delay()
		return JSONResponse(content={"task_id": task.id})
	else:
		celery_trials()
		return JSONResponse(content={"message": "Function ran on FastAPI"})

