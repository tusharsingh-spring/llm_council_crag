# Test the API directly
$conversationId = "42168080-957e-42c4-83b6-ef0eb4c5707b"
$body = @{
    content = "What is 2+2?"
} | ConvertTo-Json

Write-Host "Sending message to backend..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/conversations/$conversationId/message" -Method POST -ContentType "application/json" -Body $body -TimeoutSec 120
    
    Write-Host "Success!"
    Write-Host "Stage 1 responses: $($response.stage1.Count)"
    Write-Host "Stage 2 rankings: $($response.stage2.Count)"
    Write-Host "Stage 3 model: $($response.stage3.model)"
    Write-Host "Stage 3 response: $($response.stage3.response.Substring(0, [Math]::Min(100, $response.stage3.response.Length)))..."
} catch {
    Write-Host "Error: $_"
}
