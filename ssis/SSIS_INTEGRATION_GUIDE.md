# SSIS integration guide

## Recommended control flow
1. Add package parameters `InputFile` (string), `BatchSize` (Int32; e.g. 5000), `DbConnection` (sensitive string; supply through SSIS environment/reference, never commit credentials), and `PythonExe` (string path to the virtual-environment interpreter).
2. Add package variables `User::ExitCode` (Int32, initial 0), `User::StdOut` and `User::StdErr` (String), and optionally `User::ElapsedSeconds` (Int32).
3. Add an **Execute Process Task**. Set Executable to `@[ $Package::PythonExe ]` using the expression editor (remove spaces: `@[$Package::PythonExe]`). Set WorkingDirectory to the repository directory. Set FailTaskIfReturnCodeIsNotSuccessValue=True and SuccessValue=0.
4. Arguments: use an expression so paths/credentials are quoted safely. Prefer a protected environment variable/secret store for credentials. Example expression:
   `""" + @[User::PythonScript] + "" --input "" + @[$Package::InputFile] + "" --batch-size " + (DT_WSTR,10)@[$Package::BatchSize] + " --db-conn "" + @[$Package::DbConnection] + "" --log-file "" + @[User::LogFile] + """`
   `PythonScript` and `LogFile` are package variables. Validate paths with spaces using the target SSIS/Windows version's expression editor. If secrets contain quotes, use a secret mechanism/DSN rather than embedding them in command text.
5. In **Process** tab, set `StandardOutputVariable`=`User::StdOut` and `StandardErrorVariable`=`User::StdErr`. Map the process exit code to `User::ExitCode` with the task's **ResultSet** property when supported, or use `ExecValueVariable` and inspect the Execute Process Task result. SSIS Task result is Success/Failure; process return code is 0 on success, 1 on ETL failure. Configure `OnError` precedence constraints to notify/stop downstream loads; don't continue on failure.

## Parameters and quoting
Use full paths, a dedicated Python virtual environment, and a least-privilege SQL identity. SSIS expressions must quote each argument independently. Avoid logging connection strings or passwords. An alternative is `--db-conn` sourced at runtime from a protected environment variable; the current CLI accepts the connection string directly, so protect SSIS parameters at the project/environment level.

## Exit codes, output, diagnosis
The script emits timestamped logs to stderr and optionally a log file; uncaught operational/validation errors become a concise ERROR log and exit code 1. Success returns 0. Captured stdout contains a final JSON summary (rows read/loaded, elapsed time), suitable for SSIS logging; stderr contains progress and diagnostics. Test a deliberately missing input and confirm the task fails. Keep the fail-on-nonzero setting enabled.

## Deploy/test checklist
Install `requirements.txt` in the interpreter SSIS will invoke; apply `sql/schema.sql`; verify network access and permissions; run a small sample from command prompt; then configure SSIS parameters and test success/failure paths. SSIS 32/64-bit runtime must match installed Python/ODBC driver architecture. Enable package logging for task start/end, error events, and variable values only when they contain no secrets. Rotate logs and avoid capturing sensitive values.
