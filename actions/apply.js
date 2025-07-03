import { DuckDBInstance } from '@duckdb/node-api';

import puppeteer from "puppeteer";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker } from './buttonTracker.js';
import { email, password } from '../information.js';


const instance = await DuckDBInstance.create('linkedin.duckdb');
const conn = await instance.connect();

const jobs = await conn.runAndReadAll('select * from linkedin_data.job_urls');
console.log(typeof jobs);
const rows = jobs.getRows();
 
console.log(rows.slice(0, 10))

// jobs-apply-button-id
const num_jobs = 5
const test = rows.slice(0, num_jobs)
const apply_button = 'button[id="jobs-apply-button-id"]';
const job_url = 'https://www.linkedin.com/jobs/view/4253333502'

apply(test[0][0]);

// async function loginPythonClient() {
//     const spawn = require("child_process").spawn;
//     const pythonProcess = spawn('python',["pipe", arg1, arg2, ...]);
//     const response = await fetch('http://localhost:5000/login');
//     const data = await response.json();
//     console.log(data);
// }


async function selectorExists(page, selector) {
    try {
        await page.waitForSelector(selector, { timeout: 1000 });
    } catch (error) {
        return false;
    }
    return true;
}

async function signIn(page) {
    console.log("Account already exists. Signing in");

    // await page.locator('button[data-automation-id="signInLink"]').click();

    await page.locator('input[id="username"]').fill(email);

    await page.locator('input[id="password"]').fill(password);

    await page.locator('button[data-automation-id="signInSubmitButton"]').click({ delay: 400 });
}
async function login(job_url) {
    console.log(job_url);
    autocomplete="username webauthn"
    const page = await getPage();
    await page.goto(job_url);
    await new Promise(resolve => setTimeout(resolve, 15000));
}

async function apply(job_url) {
    console.log(job_url);
    console.log('hello');
    var page = await getPage();
    console.log(typeof page)

    // page.on('request', request => {
    //     console.log(request.url());
    //     console.log(request.headers());
    //   });
    await page.goto(
        job_url
    );
    
    await new Promise(resolve => setTimeout(resolve, 15000));

    
    const stats = await getClickStatistics(page);
    console.log('\n📈 Final click statistics:', stats);

    // Stop tracking
    await stopButtonClickTracker(page);
    
    console.log('✅ Test completed! Check the console output and log file for details.');
    
    // await browser.close();
    
    // await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    // await click_apply_button(page);
}

async function getPage() {
    console.log("Getting page");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
    });
    const page = await browser.newPage();
    await setupButtonClickTracker(page, {
        enableConsoleLog: true,
        enableFileLog: true,
        logFilePath: './test-button-clicks.log',
        trackAllElements: true, // Track all clickable elements
        captureScreenshot: false,
        screenshotDir: './test-screenshots'
    });
    return page;
}
        
async function click_apply_button(page) {
    if (await selectorExists(page, apply_button)) {
        // check if easy apply button (aria-label contains "Easy Apply")
        if (await page.locator(apply_button).getAttribute('aria-label').includes("Easy Apply")) {
            console.log("Easy Apply button found. Clicking");
            await page.locator(apply_button).click();
        }
        else {
            console.log("Apply button found. Clicking");
            await page.locator(apply_button).click();
        }
    }
}

async function easy_apply(page, selector) {
    // all elements under div w class "jobs-easy-apply-modal"
    // named jobs-easy-apply-modal

    // inputs are nested in divs w class XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl 
    // look for elements following a label with text e.g. first name, last name, email, phone, etc.

    // selects w options nested after labels w text 
    //selects ids  
    // text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338204-phoneNumber-country
    // single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338204-phoneNumber-nationalNumber
    // text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338180-multipleChoice

    // next: button w  name data-easy-apply-next-button

    // if h3 with text Resume, should have already auto selected. hit next again 
    // same w Mark this job as a top choice 

    // common questions 
    // legal auth
    // radio-button-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338244-multipleChoice
    // sponsorship
    // radio-button-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338236-multipleChoice
    // prevously worked for 
    // radio-button-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338228-multipleChoice

}

async function apply_to_workday(page, job_url) {
    await page.goto(job_url);
    await click_apply_button(page);
    await easy_apply(page);
}
