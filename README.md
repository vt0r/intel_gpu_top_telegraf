# intel_gpu_top_telegraf

A simple utility that bridges Intel GPU telemetry to Telegraf by executing
`intel_gpu_top` with JSON output and formatting the results for Telegraf
ingestion via the `exec` input plugin in `json` format.

## Requirements

- The `intel_gpu_top` binary must be present and in your PATH. On Ubuntu, this
  means the `intel-gpu-tools` package must be installed.
- This script must be executed with root privileges (a requirement of
  `intel_gpu_top`). Example `sudoers` rule for the `telegraf` user:

    ``` yaml
    # Allow telegraf user to run the intel_gpu_top_telegraf script
    telegraf ALL=(root:root) NOPASSWD: /usr/local/bin/intel_gpu_top_telegraf
    ```

- Python 3.6+ to execute the script itself

## Installation

```bash
sudo cp intel_gpu_top_telegraf.py /usr/local/bin/intel_gpu_top_telegraf
sudo chmod +x /usr/local/bin/intel_gpu_top_telegraf
```

## Usage

Run directly:

``` bash
sudo ./intel_gpu_top_telegraf.py
```

Or if installed to `/usr/local/bin/`:

``` bash
sudo intel_gpu_top_telegraf
```

## How It Works

1. Executes `intel_gpu_top -J` to get JSON-formatted GPU metrics
2. Collects a single sample by sleeping for 0.5 seconds (`intel_gpu_top`'s
  sampling interval is 1s, and we only want one sample)
3. Sends a SIGINT to the `intel_gpu_top` process, so it will gracefully exit
  and close the JSON body
4. Injects a UTC timestamp and measurement name for Telegraf
5. Outputs valid JSON to stdout, pretty-printed

## Integration with Telegraf

Configure Telegraf to use this script as an input plugin of the `exec` type
with the `data_format` type of `json`.

``` toml
[[inputs.exec]]
  commands = ["sudo /usr/local/bin/intel_gpu_top_telegraf"]
  timeout = "5s"
  interval = "5s"
  data_format = "json"

  json_strict = true
  json_name_key = "measurement_name"
  json_time_key = "timestamp"
  json_time_format = "unix_ns"
```

## Output Example

```json
{
    "period": {
        "duration": 47.798026,
        "unit": "ms"
    },
    "frequency": {
        "requested": 0.0,
        "actual": 0.0,
        "unit": "MHz"
    },
    "interrupts": {
        "count": 0.0,
        "unit": "irq/s"
    },
    "rc6": {
        "value": 0.0,
        "unit": "%"
    },
    "power": {
        "GPU": 0.0,
        "Package": 4.900891,
        "unit": "W"
    },
    "imc-bandwidth": {
        "reads": 1111.078538,
        "writes": 103.508663,
        "unit": "MiB/s"
    },
    "engines": {
        "Render/3D": {
            "busy": 0.0,
            "sema": 0.0,
            "wait": 0.0,
            "unit": "%"
        },
        "Blitter": {
            "busy": 0.0,
            "sema": 0.0,
            "wait": 0.0,
            "unit": "%"
        },
        "Video": {
            "busy": 0.0,
            "sema": 0.0,
            "wait": 0.0,
            "unit": "%"
        },
        "VideoEnhance": {
            "busy": 0.0,
            "sema": 0.0,
            "wait": 0.0,
            "unit": "%"
        }
    },
    "clients": {},
    "timestamp": 1769843071611457318,
    "measurement_name": "intel_gpu_top"
}
```
