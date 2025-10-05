from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from domain.interactors.label_interactor import LabelInteractor
from data.repositories.label_repository import LabelRepository
from domain.entities.label import Label
from domain.entities.signal_data import Signal, SignalData
from domain.entities.access_request import AccessRequest
from domain.entities.create_request import CreateRequest
from domain.entities.access_esp_request import AccessESPRequest
from domain.entities.update_request import UpdateRequest
from core.errors import NotFoundLabelException, DismatchPasswordException
import uvicorn
import os

app = FastAPI()

from data.repositories.position_repository import PositionRepository

repository = LabelRepository()
position_repository = PositionRepository()
interactor = LabelInteractor(repository=repository, position_repository=position_repository)


# ESP endpoints
@app.post("/create")
async def create_label(model: CreateRequest):
    # Create a label with hardcoded password (corporate password from ESP)
    label = Label(
        id=model.id,
        own_password="corporate_secret",
        com_password="corporate_secret"
    )
    interactor.create(label)
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.post("/access")
async def access_request(model: AccessESPRequest):
    try:
        # Create access request with hardcoded passwords
        access_req = AccessRequest(
            own_id=model.my_id,
            neighbour_id=model.seen_id,
            com_password="corporate_secret",
            own_password="corporate_secret"
        )
        interactor.access_request(access_request=access_req)
        return JSONResponse(content="true", status_code=200)
    except NotFoundLabelException:
        return JSONResponse(content="false", status_code=200)
    except DismatchPasswordException:
        return JSONResponse(content="false", status_code=200)
    
@app.post("/update")
async def send_signals(model: UpdateRequest):
    try:
        interactor.post_update(model)
        return JSONResponse(content={"status": "ok"}, status_code=200)
    except NotFoundLabelException:
        raise HTTPException(status_code=404)

@app.delete("/delete/{label_id}")
async def delete(label_id: str):
    interactor.delete(label_id=label_id)
    return JSONResponse(content={"status": "ok"}, status_code=200)

# Web interface endpoints
@app.get("/api/positions")
async def get_positions():
    """Get all calculated positions"""
    positions = interactor.get_all_positions()
    return JSONResponse(content=positions, status_code=200)

@app.post("/api/base-stations")
async def configure_base_stations(config: dict):
    """Configure base station positions"""
    interactor.configure_base_stations(config)
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the web interface"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>GeoMAX Tracking System</h1><p>Frontend not found</p>")

if __name__ == "__main__":
    uvicorn.run(app, host="10.37.152.60", port=8000, log_level="info")