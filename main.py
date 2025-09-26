from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import fractions

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def parse_ingredient_line(line):
    parts = line.split()
    amount = 0
    unit_index = 0
    try:
        amount = float(parts[0])
        unit_index = 1
    except:
        try:
            amount = float(sum(fractions.Fraction(s) for s in parts[0:2]))
            unit_index = 2
        except:
            amount = 0
    unit = parts[unit_index] if len(parts) > unit_index else ""
    ingredient_name = " ".join(parts[unit_index + 1:]) if len(parts) > unit_index + 1 else ""
    return amount, unit, ingredient_name

def scale_ingredient(amount, original_servings, desired_servings):
    return amount * desired_servings / original_servings

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/scale", response_class=HTMLResponse)
def scale(request: Request, ingredients: str = Form(...), original_servings: int = Form(...), desired_servings: int = Form(...)):
    scaled_lines = []
    for line in ingredients.strip().split("\n"):
        if not line.strip():
            continue
        amount, unit, name = parse_ingredient_line(line)
        new_amount = scale_ingredient(amount, original_servings, desired_servings)
        if new_amount.is_integer():
            new_amount = int(new_amount)
        scaled_lines.append(f"{new_amount} {unit} {name}".strip())
    return templates.TemplateResponse("result.html", {"request": request, "scaled_lines": scaled_lines})