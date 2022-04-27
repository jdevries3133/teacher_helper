from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from teacherhelper.email_ import Email


def test_setup_template():
    """Mainly, test that the importlib resources API is working in email's
    init method"""

    with patch("teacherhelper.email_.get_data_dir") as ddir:
        temp = TemporaryDirectory()
        ddir.return_value = Path(temp.name)

        Email().setup()

        created_template = Path(temp.name) / "email_templates" / "default.html"
        assert created_template.exists()
        with open(created_template, "r") as fp:
            assert "{{ email_content }}" in fp.read()
