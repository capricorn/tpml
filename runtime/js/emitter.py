import subprocess
from jinja2 import Template 

def emit(prefix=True):
    with open('runtime/js/bookmarklet.jinja', 'r') as f:
        emit_template = Template(f.read()) 
    
    with open('runtime/js/matcher.js', 'r') as f:
        matcher_js = f.read()

    bookmarklet_js = emit_template.render(matcher_js=matcher_js)

    # TODO: Handle missing esbuild install
    result = subprocess.run(
        f'./runtime/js/node_modules/.bin/esbuild --bundle --minify <<END_JS\n{bookmarklet_js}\nEND_JS', 
        shell=True,
        capture_output=True)

    scheme_prefix = 'javascript:' if prefix else ''
    return f'{scheme_prefix}{result.stdout.decode('utf8').strip()}'
