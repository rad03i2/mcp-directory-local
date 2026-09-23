import json
import tempfile
import unittest
from pathlib import Path
from mcp_directory import Directory, DirectoryError, validate_server

class DirectoryTests(unittest.TestCase):
    def stdio(self, name="files"):
        return validate_server({"name":name,"description":"Local files","transport":"stdio","command":"python","args":["server.py"],"tags":["Files","local"]})

    def test_round_trip_and_search(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"registry.json"; reg=Directory(); reg.add(self.stdio()); reg.save(path)
            loaded=Directory.load(path)
            self.assertEqual(loaded.get("files").command,"python")
            self.assertEqual([x.name for x in loaded.search("LOCAL", tag="files")],["files"])

    def test_duplicate_rejected(self):
        reg=Directory([self.stdio()])
        with self.assertRaises(DirectoryError): reg.add(self.stdio())

    def test_invalid_transport_shape(self):
        with self.assertRaises(DirectoryError): validate_server({"name":"bad","transport":"stdio","url":"https://x"})
        with self.assertRaises(DirectoryError): validate_server({"name":"bad","transport":"https","url":"http://x"})

    def test_export(self):
        http=validate_server({"name":"remote","description":"r","transport":"https","url":"https://example.test/mcp","tags":[]})
        reg=Directory([self.stdio(),http]); out=reg.export_client_config()
        self.assertEqual(out["mcpServers"]["files"]["args"],["server.py"])
        self.assertEqual(out["mcpServers"]["remote"]["url"],"https://example.test/mcp")

    def test_remove_missing(self):
        with self.assertRaises(DirectoryError): Directory().remove("missing")

    def test_malformed_registry(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"r.json"; p.write_text('{"version":2,"servers":[]}',encoding="utf-8")
            with self.assertRaises(DirectoryError): Directory.load(p)

if __name__ == "__main__": unittest.main()
