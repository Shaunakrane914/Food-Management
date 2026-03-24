import re

with open("main.py", "r", encoding="utf-8") as f:
    content = f.read()

# The regex looks for `templates.TemplateResponse("template.html",` 
# and replaces it with `templates.TemplateResponse(request, "template.html",`
# The quotes capture ensures it only targets legacy calls where the first arg is a string.
new_content = re.sub(
    r'templates\.TemplateResponse\(\s*(["\'][^"\']+["\'])\s*,',
    r'templates.TemplateResponse(request, \1,',
    content
)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Replaced {content.count('templates.TemplateResponse') - new_content.count('templates.TemplateResponse')} occurrences? No, just verifying it ran successfully.")
print("Syntax updated!")
