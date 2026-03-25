A power plant failure occurred yesterday. You have access to the full system log file via the `search_logs` tool.

Your task:
1. Search for all CRIT, ERRO, and WARN events
2. Compress them into a condensed log within 1500 tokens
3. Submit using `submit_logs` and read the technician feedback
4. Iterate based on feedback until you receive the flag

Known components to cover: ECCS8, WTANK07, WTRPMP, PWR01, STMTURB12, WSTPOOL2, FIRMWARE.
Start by searching for all CRIT events to understand the failure timeline.
