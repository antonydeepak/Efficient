# Cross-platform powershell client to send events of interest to track

Set-StrictMode -Version Latest

$MAX_RESPONSE_LENGTH = 2048

function Set-TcpServerParameters
{
    param(
        [Parameter(Mandatory = $false, ValueFromPipeline = $false)]
        [int] $server,

        [Parameter(Mandatory = $false, ValueFromPipeline = $false)]
        [int] $port
    )

    $script:Server = $server
    $script:Port = $port
}

<#
.SYNOPSIS
    Sends an event and start the clock
.DESCRIPTION
    {
        "command": "start",
        "args": {
            "duration": {
                "hours": 8,
                "minutes": 0,
                "seconds": 0
            }
        }
    }
#>
function Invoke-EfficientStartDay
{
    param(
        [Parameter(Mandatory = $false, ValueFromPipeline = $false)]
        [System.TimeSpan] $Duration = (New-TimeSpan -Hour 8 -Minute 0 -Seconds 0)
    )

    # Start Time
    $command = ConvertFrom-Json '
    {
        "command": "start",
        "args": {
            "duration": {
                "hours": 0,
                "minutes": 0,
                "seconds": 0
            }
        }
    }'
    $command.args.duration.hours = $Duration.Hours
    $command.args.duration.minutes = $Duration.Minutes
    $command.args.duration.hours = $Duration.Seconds

    SendRequest $script:Server $script:Port (ConvertTo-Json $command)

    # Record Event
    # TODO
}
Set-Alias -Name startday -Value Invoke-EfficientStartDay

<#
.SYNOPSIS
    Sends an event and start the clock
.DESCRIPTION
    {
        "command": "end"
    }
#>
function Invoke-EfficientEndDay
{
    param(
        [Parameter(Mandatory = $false, ValueFromPipeline = $false)]
        [System.TimeSpan] $Duration = (New-TimeSpan -Hour 8 -Minute 0 -Seconds 0)
    )

    # End Timer
    $command = ConvertFrom-Json '
    {
        "command": "end"
    }'
    SendRequest $script:Server $script:Port (ConvertTo-Json $command)

    # Record Event
    # TODO
}
Set-Alias -Name endday -Value Invoke-EfficientEndDay

function SendRequest
{
    param(
        [int] $server,
        [int] $port,
        [string] $message
    )
    {
        if ((-not $server) -or (-not $port))
            throw "Server '$server' or Port '$port' is empty"

        $client = New-Object -TypeName TcpClient -ArgumentList @($server, $port)
        try {
            $stream = $client.GetStream()

            try {
                $payload = [System.Text.Encoding]::UTF8.GetBytes($message)
                $stream.Write($payload, 0, $payload.Length)

                $response = New-Object -TypeName byte[] -ArgumentList $MAX_RESPONSE_LENGTH
                $stream.Read($response, 0, $MAX_RESPONSE_LENGTH)

                [System.Text.Encoding]::UTF8.GetString($response)

                $stream.Close()
                $client.Close()
            }
            finally {
                if ($stream) {
                    $stream.Dispose()
                }
            }
        }
        finally {
            if ($client) {
                $client.Dispose()
            }
        }
   }
}

Export-ModuleMember -Function Set-TcpServerParameters
Export-ModuleMember -Function Invoke-EfficientStartDay
Export-ModuleMember -Function Invoke-EfficientEndDay

Export-ModuleMember -Alias startday
Export-ModuleMember -Alias endday