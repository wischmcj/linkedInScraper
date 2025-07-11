import puppeteer from "puppeteer";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker } from './buttonTracker.js';

import { email, password, requestHeaders, captcha_token} from './information.js';

async function selectorExists(page, selector) {
    try {
        await page.waitForSelector(selector, { timeout: 5000 });
    } catch (error) {
        console.log('selector not found. error: ', error);
        return false;
    }
    return true;
}


async function initializePage(trackClicks=true) {
    console.log("Getting page");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
        devtools: true,
        slowMo: 250
    });
    const page = await browser.newPage();
    await page.setExtraHTTPHeaders({...requestHeaders});
    if (trackClicks) {
        await setupButtonClickTracker(page, {
            enableConsoleLog: true,
            enableFileLog: true,
            logFilePath: './test-button-clicks.log',
            trackAllElements: true, // Track all clickable elements
            captureScreenshot: false,
            screenshotDir: './test-screenshots'
        });
    }
    return [page, browser];
}
        
async function closePage(page, browser) {

    const stats = await getClickStatistics(page);
    console.log('\n📈 Final click statistics:', stats);

    // Stop tracking
    await stopButtonClickTracker(page);
    
    console.log('✅ Test completed! Check the console output and log file for details.');
    
    // await browser.close();
}

async function detailedLogging(page) {
    page.on('request', request => {
        console.log(request.url());
        console.log(request.headers());
    });
}


async function manualDebug(page) {
    // Allows running of local module code in browser 
    // example for running multil line code and deserializing the result:
    // nodeEval(`
    //      (async () => { 
    //          const x = await page.$$eval('button[class="jobs-easy-apply-modal__content"]', els => els.map(el => el.textContent));
    //          return JSON.stringify(x);
    //        }
    //      )();`
    // )
    //     .then(res => console.log(JSON.parse(res)))
    //     .catch(err => console.error(err));
    let browser;
    try {
        // WARNING: unsafe to expose to clients!
        // eval() for individual development purposes only!
        await page.exposeFunction("nodeEval", script => {
            return new Promise((resolve, reject) => {
            try {
                resolve(eval(script));
            }
            catch (err) {
                reject(err);
            }
            });
        });
        for (;;) await setTimeout(2**30); // sleep forever
    }
    catch (err) {
        console.error(err);
    }
    finally {
            await browser?.close();
        }
}

export { selectorExists, initializePage, closePage, manualDebug };