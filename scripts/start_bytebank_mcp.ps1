param()

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Ambiente virtual ausente. Crie-o com: python -m venv .venv"
}

& $python (Join-Path $PSScriptRoot "bytebank_mcp_server.py")