import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
from mcp_directory.cli import main

class CliTests(unittest.TestCase):
    def test_add_find_export_remove(self):
        with tempfile.TemporaryDirectory() as d:
            reg=Path(d)/"r.json"
            item=json.dumps({"name":"clock","description":"Clock tools","transport":"stdio","command":"clock-server","args":[],"tags":["time"]})
            with redirect_stdout(StringIO()): self.assertEqual(main(["--registry",str(reg),"add",item]),0)
            out=StringIO()
            with redirect_stdout(out): self.assertEqual(main(["--registry",str(reg),"find","clock","--json"]),0)
            self.assertEqual(json.loads(out.getvalue())[0]["name"],"clock")
            out=StringIO()
            with redirect_stdout(out): self.assertEqual(main(["--registry",str(reg),"export","clock"]),0)
            self.assertEqual(json.loads(out.getvalue())["mcpServers"]["clock"]["command"],"clock-server")
            with redirect_stdout(StringIO()): self.assertEqual(main(["--registry",str(reg),"remove","clock"]),0)

    def test_invalid_returns_two(self):
        with tempfile.TemporaryDirectory() as d, redirect_stderr(StringIO()):
            self.assertEqual(main(["--registry",str(Path(d)/"r.json"),"show","missing"]),2)

if __name__ == "__main__": unittest.main()
