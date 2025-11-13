param(
    [string]$BaseUrl = "http://localhost:8848/nacos",
    [string]$DataId = "demo.yaml",
    [string]$Group = "DEFAULT_GROUP",
    [string]$Token,
    [string]$Username,
    [string]$Password,
    [string]$OutFile
)

# Normalize base URL
if ($BaseUrl.EndsWith("/")) { $BaseUrl = $BaseUrl.TrimEnd('/') }

# Pick up token from env if not provided explicitly
if (-not $Token -and $env:NACOS_ACCESS_TOKEN) { $Token = $env:NACOS_ACCESS_TOKEN }

function Write-Err($msg) {
    Write-Error -Message $msg
}

function Try-GetConfig([string]$base, [string]$dataId, [string]$group, [string]$token) {
    $url = "$base/v1/cs/configs?dataId=$([uri]::EscapeDataString($dataId))&group=$([uri]::EscapeDataString($group))"
    if ($token) { $url = "$url&accessToken=$token" }
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
        return @{ ok = $true; status = $resp.StatusCode; content = $resp.Content }
    } catch {
        $code = $null
        try { $code = $_.Exception.Response.StatusCode.Value__ } catch { $code = -1 }
        return @{ ok = $false; status = $code; content = $null }
    }
}

# 1) If token absent, try unauthenticated (works only if auth disabled)
$result = Try-GetConfig -base $BaseUrl -dataId $DataId -group $Group -token $Token

if ($result.ok) {
    if ($OutFile) {
        $result.content | Out-File -FilePath $OutFile -Encoding utf8
        Write-Output "Saved content to $OutFile"
    } else {
        $result.content | Write-Output
    }
    exit 0
}

# 2) If unauthorized and no token provided, optionally try login if username/password are supplied
if (($result.status -eq 401 -or $result.status -eq 403)) {
    if (-not $Token -and $Username -and $Password) {
        try {
            $loginResp = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/auth/users/login" -Body @{ username = $Username; password = $Password } -ContentType 'application/x-www-form-urlencoded' -TimeoutSec 10
            $Token = $loginResp.accessToken
        } catch {
            Write-Err "Authentication required (HTTP $($result.status)). Login failed. Provide valid credentials or an access token."
            exit 2
        }

        # Retry with token
        $result2 = Try-GetConfig -base $BaseUrl -dataId $DataId -group $Group -token $Token
        if ($result2.ok) {
            if ($OutFile) {
                $result2.content | Out-File -FilePath $OutFile -Encoding utf8
                Write-Output "Saved content to $OutFile"
            } else {
                $result2.content | Write-Output
            }
            exit 0
        } else {
            Write-Err "Authorized request failed with HTTP $($result2.status)."
            exit 3
        }
    } else {
        Write-Err "Authentication required (HTTP $($result.status)). Provide -Token, set NACOS_ACCESS_TOKEN, or pass -Username/-Password to login."
        exit 1
    }
}

# 3) Other errors
Write-Err "Request failed with HTTP $($result.status)."
exit 4

