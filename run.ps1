# run.ps1
# PowerShell script to run both the FastAPI server and Streamlit client concurrently

Write-Host "Starting FastAPI server..."
$serverJob = Start-Job -ScriptBlock {
    Set-Location -Path "$using:PWD\server"
    uvicorn main:app --port 3001 --reload
}

Write-Host "Starting Streamlit client..."
$clientJob = Start-Job -ScriptBlock {
    Set-Location -Path "$using:PWD\client"
    streamlit run app.py
}

Write-Host "Both services started. Press Ctrl+C to stop."

try {
    # Keep the script running
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "Stopping Services..."
    Stop-Job $serverJob
    Stop-Job $clientJob
    Remove-Job $serverJob
    Remove-Job $clientJob
}
