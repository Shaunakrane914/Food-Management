from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Frontend Only Server")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": None})

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard",
            "total_ingredients": 0,
            "low_stock_count": 0,
            "low_stock_items": [],
            "recent_bom": [],
            "recent_activity": []
        }
    )

@app.get("/form")
async def form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "message": None})

@app.get("/menu")
async def menu(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request, "active_page": "menu", "menu": {}})

@app.get("/studentstaff")
async def studentstaff(request: Request):
    return templates.TemplateResponse("studentstaff.html", {"request": request, "active_page": "studentstaff"})

@app.get("/supplier")
async def supplier(request: Request):
    return templates.TemplateResponse("supplier.html", {"request": request, "active_page": "supplier"})

@app.get("/analytics")
async def analytics(request: Request):
    return templates.TemplateResponse("analytics.html", {"request": request, "active_page": "analytics"})

@app.get("/index")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/pax")
async def pax(request: Request):
    return templates.TemplateResponse("pax.html", {"request": request, "active_page": "pax"})

@app.get("/pax_settings")
async def pax_settings(request: Request):
    return templates.TemplateResponse("pax_settings.html", {"request": request, "active_page": "pax_settings"})

@app.get("/settings")
async def settings(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request, "active_page": "settings", "dishes": []})

@app.get("/bom")
async def bom(request: Request):
    return templates.TemplateResponse("bom.html", {"request": request, "active_page": "bom", "bom_results": None, "error": None})

@app.get("/bom_database")
async def bom_database(request: Request):
    return templates.TemplateResponse("bom_database.html", {"request": request, "active_page": "bom", "dishes_data": []})

@app.get("/edit_menu")
async def edit_menu(request: Request):
    return templates.TemplateResponse("edit_menu.html", {"request": request, "active_page": "menu"})

if __name__ == "__main__":
    import uvicorn
    # Using port 8001 to avoid conflicting with the running main backend
    uvicorn.run("frontend:app", host="0.0.0.0", port=8001, reload=True)
