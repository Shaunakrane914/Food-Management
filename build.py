import os
import shutil
from jinja2 import Environment, FileSystemLoader

DIST_DIR = "dist"

def build():
    # Setup output directory
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Copy all static assets into the publish directory
    if os.path.exists("static"):
        shutil.copytree("static", os.path.join(DIST_DIR, "static"))
        
    env = FileSystemLoader("templates")
    jinja_env = Environment(loader=env)

    # A mock class for the FastAPI request object and its url_for
    class MockRequest:
        def url_for(self, endpoint, **kwargs):
            if endpoint == 'static':
                return f"/static/{kwargs.get('path')}"
            if endpoint == 'login' or endpoint == 'login_get' or endpoint == 'login_post':
                return "/login.html"
            return f"/{endpoint}.html"
            
    # Function for direct generic {{ url_for('something') }}
    def mock_url_for(endpoint, **kwargs):
        if endpoint == 'static':
            return f"/static/{kwargs.get('path')}"
        if endpoint == 'login' or endpoint == 'login_get' or endpoint == 'login_post':
            return "/login.html"
        return f"/{endpoint}.html"

    jinja_env.globals['url_for'] = mock_url_for

    # Mapping of source templates to generated route names and their contexts
    pages = {
        "landing.html": ("index.html", {}),
        "form.html": ("login.html", {"message": None}),
        "dashboard.html": ("dashboard.html", {
            "active_page": "dashboard", "total_ingredients": 0, 
            "low_stock_count": 0, "low_stock_items": [], 
            "recent_bom": [], "recent_activity": []
        }),
        "menu.html": ("menu.html", {"active_page": "menu", "menu": {}}),
        "studentstaff.html": ("studentstaff.html", {"active_page": "studentstaff"}),
        "supplier.html": ("supplier.html", {"active_page": "supplier"}),
        "analytics.html": ("analytics.html", {"active_page": "analytics"}),
        "pax.html": ("pax.html", {"active_page": "pax"}),
        "pax_settings.html": ("pax_settings.html", {"active_page": "pax_settings"}),
        "settings.html": ("settings.html", {"active_page": "settings", "dishes": []}),
        "bom.html": ("bom.html", {"active_page": "bom", "bom_results": None, "error": None}),
        "bom_database.html": ("bom_database.html", {"active_page": "bom", "dishes_data": []}),
        "edit_menu.html": ("edit_menu.html", {"active_page": "menu"})
    }

    print("Building static site for Netlify...")
    for template_name, (out_file, context) in pages.items():
        try:
            template = jinja_env.get_template(template_name)
            context["request"] = MockRequest()
            html_content = template.render(**context)
            
            with open(os.path.join(DIST_DIR, out_file), "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Generated {out_file} from {template_name}")
        except Exception as e:
            print(f"WARNING: Could not compile {template_name} - {e}")

    print("Build complete! Output is in the 'dist' directory.")

if __name__ == "__main__":
    build()
