import pytest
from unittest.mock import patch
import requests
from dotenv import load_dotenv
from functions import check_portfolio_name_exists  # change `your_module` to the actual filename (no .py)
load_dotenv()
class TestCheckPortfolioNameExists:
 
    @patch("requests.get")
    def test_portfolio_exists(self, mock_get):
        mock_get.return_value.status_code = 200
        result = check_portfolio_name_exists("existing-repo")
        assert result is False
 
    @patch("requests.get")
    def test_portfolio_available(self, mock_get):
        mock_get.return_value.status_code = 404
        result = check_portfolio_name_exists("new-repo")
        assert result is True
 
    @patch("requests.get")
    def test_unexpected_error(self, mock_get):
        mock_get.return_value.status_code = 500
        result = check_portfolio_name_exists("error-repo")
        assert result is False