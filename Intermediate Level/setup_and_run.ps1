Write-Host "==================================================="
Write-Host "Setting up AI Engineer RAG Project"
Write-Host "==================================================="

if (-not (Test-Path -Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

Write-Host "Activating virtual environment..."
& .\venv\Scripts\Activate.ps1

Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Starting Streamlit app..."
streamlit run app.py
