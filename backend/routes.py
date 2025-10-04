from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from domain.interactors.label_interactor import LabelInteractor
from data.repositories.label_repository import LabelRepository
from domain.entities.label import Label
from domain.entities.signal_data import Signal, SignalData
from domain.entities.access_request import AccessRequest
from core.errors import NotFoundLabelException, DismatchPasswordException

app = FastAPI()

repository = LabelRepository()
interactor = LabelInteractor(repository=repository)


@app.post("/labels/")
async def create_label(model: Label):
    await interactor.create(model)
    return JSONResponse(status_code=status.HTTP_201_CREATED)

@app.post("/labels/access")
async def access_request(model: AccessRequest):
    try:
        await interactor.access_request(access_request=model)
        return JSONResponse(status_code=status.HTTP_200_OK)
    except NotFoundLabelException:
        raise HTTPException(status_code=404)
    except DismatchPasswordException:
        raise HTTPException(status_code=401)
    
@app.post("/labels/signals")
async def send_signals(model: SignalData):
    try:
        await interactor.post_signals(model)
        return JSONResponse(status_code=status.HTTP_200_OK)
    except NotFoundLabelException:
        raise HTTPException(status_code=404)

@app.delete("/labels/{label_id}")
async def delete(label_id: str):
    await interactor.delete(label_id=label_id)
