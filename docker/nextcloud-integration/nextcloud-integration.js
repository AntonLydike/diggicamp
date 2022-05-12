import express from 'express';

const {exec} = require('child_process')

const app = express();
const port = process.env.PORT ?? 4269;

/**
 * Executes a shell command and return it as a Promise.
 * @param cmd {string}
 * @return {Promise<[string, string, boolean]>}
 */
const execShellCommand = (cmd) => {
    return new Promise((resolve, reject) => {
        exec(cmd, (error, stdout, stderr) => {
            if (error) {
                console.warn(error);
            }
            resolve([stdout, stderr, !!error]);
        });
    });
}

app.get('/', (req, res) => {
    return res.send('Simple API to trigger nextcloud-update.');
});

app.post('/trigger-filescan', async (req, res) => {
    const userFolder = (req.body.toString() ?? '').replace(/[^a-z0-9/\s-_]/gm, '')
    const [stdout, stderr, hasError] = await execShellCommand(`runuser -u www-data -g www-data php occ files:scan --path "${userFolder}"`)
    return res.send(`Execution finished ${(hasError ? 'with error' : 'successfully')}.\n${stdout}\n${stderr}`);
});

app.listen(port, () =>
    console.log(`Example app listening on port ${port}!`),
);