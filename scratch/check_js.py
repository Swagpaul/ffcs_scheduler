import subprocess

with open("app/templates/results.html", "r", encoding="utf-8") as f:
    html = f.read()

# Extract script block
start = html.find("<script>") + len("<script>")
end = html.find("</script>")
script_content = html[start:end]

with open("scratch/temp.js", "w", encoding="utf-8") as f:
    f.write(script_content)

# Use node to check syntax
try:
    subprocess.run(["node", "-c", "scratch/temp.js"], check=True, capture_output=True, text=True)
    print("Syntax OK")
except subprocess.CalledProcessError as e:
    print("Syntax Error!")
    print(e.stderr)
