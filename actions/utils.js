import puppeteer from "puppeteer";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker } from './buttonTracker.js';

import { email, password, requestHeaders, captcha_token} from './information.js';

async function selectorExists(page, selector, timeout=5000) {
    try {
        await page.waitForSelector(selector, { timeout: timeout });
    } catch (error) {
        console.log('selector not found. error: ', error);
        return false;
    }
    return true;
}


async function initializePage(trackClicks=true, slowMo=100) {
    console.log("Getting page");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
        devtools: true,
        slowMo: slowMo
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
    //          const x = await page.locator('div[data-automation-id*="previousWorker"] input[id*="2"]').click();
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
        for (;;){
            setTimeout(2**30); // sleep forever
        }
    }
    catch (err) {
        console.error(err);
    }
    finally {
            await browser?.close();
        }
}

async function wait(page, selector_str, func='wait', timeout=1000) {
    // Used to try a few different ways of running a selector, to see if it is valid
    console.log('Waiting for selector: ', selector_str, ' function: ', func, ' timeout: ', timeout);
    try {
        if (func == '$$eval') {
            await page.$$eval(selector_str, (elements) => {
                console.log(elements);
                console.log('elements.length: ', elements.length);
            });
        }
        else if (func == 'wait') {
            await page.waitForSelector(selector_str, { timeout: timeout });
        }
        else if (func == '$eval') {
            await page.$eval(selector_str, (element) => {
                console.log(element);
            });
        }
        console.log('Selector found: ', selector_str, ' element: ', await page.$(selector_str));
    }
    catch (error) {
        console.log('Error waiting for selector: ', selector_str);
        console.log(error);
    }
}

export { selectorExists, initializePage, closePage, manualDebug, wait };