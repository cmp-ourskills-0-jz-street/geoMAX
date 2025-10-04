from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from domain.interactors.label_interactor import LabelInteractor
from data.repositories.label_repository import LabelRepository
from domain.entities.label import Label
from domain.entities.signal_data import Signal, SignalData
from domain.entities.access_request import AccessRequest
from core.errors import NotFoundLabelException, DismatchPasswordException
import uvicorn

app = FastAPI()

repository = LabelRepository()
interactor = LabelInteractor(repository=repository)


@app.post("/labels/")
async def create_label(model: Label):
    interactor.create(model)

@app.post("/labels/access")
async def access_request(model: AccessRequest):
    try:
        interactor.access_request(access_request=model)
    except NotFoundLabelException:
        raise HTTPException(status_code=404)
    except DismatchPasswordException:
        raise HTTPException(status_code=401)
    
@app.post("/labels/signals")
async def send_signals(model: SignalData):
    try:
        interactor.post_signals(model)
    except NotFoundLabelException:
        raise HTTPException(status_code=404)

@app.delete("/labels/{label_id}")
async def delete(label_id: str):
    interactor.delete(label_id=label_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")