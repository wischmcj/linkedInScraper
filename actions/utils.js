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


async function initializePage() {
    console.log("Getting page");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
        devtools: true
    });
    const page = await browser.newPage();
    await page.setExtraHTTPHeaders({...requestHeaders});
    await setupButtonClickTracker(page, {
        enableConsoleLog: true,
        enableFileLog: true,
        logFilePath: './test-button-clicks.log',
        trackAllElements: true, // Track all clickable elements
        captureScreenshot: false,
        screenshotDir: './test-screenshots'
    });
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


export { selectorExists, initializePage, closePage };