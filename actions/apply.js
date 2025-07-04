import { DuckDBInstance } from '@duckdb/node-api';

// import puppeteer from "puppeteer";
import puppeteer from "puppeteer-extra";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker} from './buttonTracker.js';
import { email, password, requestHeaders, captcha_token} from './information.js';
import { solve_captcha } from './resolve_captcha.js';

// Getting jobs to run from duckdb
// const instance = await DuckDBInstance.create('linkedin.duckdb');
// const conn = await instance.connect();
// const jobs = await conn.runAndReadAll('select * from linkedin_data.job_urls');
// console.log(typeof jobs);
// const rows = jobs.getRows();

// default vals for testing
// const num_jobs = 5
// const test = rows.slice(0, num_jobs)
const job_url = 'https://www.linkedin.com/jobs/view/4253333502' // for testing
const login_url = 'https://www.linkedin.com/login'


// apply(test[0][0]);
let page_and_browser = await initializePage();
let page = page_and_browser[0];
let browser = page_and_browser[1];
// page.on('request', request => {
//     console.log(request.url());
//     console.log(request.headers());
//   });
console.log('signing in');
await signIn(page);

async function signIn(page) {

    await page.goto(
        login_url
    );
    // await page.locator('button[data-automation-id="signInLink"]').click();

    await page.locator('input[id="username"]').fill(email);

    await page.locator('input[id="password"]').fill(password);

    await page.locator('button[data-litms-control-urn="login-submit"]').click({ delay: 400 });

    //give the page time to load
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    if (await page.url().includes('checkpoint')) {
        console.log('detected captcha challenge. Resolving...')
        //await solve_captcha(page);
    }
    return page;

}

async function apply(job_url) {
    console.log(job_url);
    console.log('hello');
    let page_and_browser = await initializePage();
    let page = page_and_browser[0];
    let browser = page_and_browser[1];
    console.log(typeof page)

    // page.on('request', request => {
    //     console.log(request.url());
    //     console.log(request.headers());
    //   });

    console.log('signing in');
    await signIn(page);

    console.log('waiting for start puzzle');
    await new Promise(resolve => setTimeout(resolve, 5000));
    console.log('clicking start puzzle');
    let pat = '::-p-xpath(//button[contains(text(), "Start")])'
    
    
    pat = 'div[id="root"]'
    try {        
        await page.locator('div ::-p-text(Start Puzzle)').click();
        console.log(pat, 'clicked start puzzle');
    }
    catch (error) {
        console.log(pat, 'no start puzzle button found: ', error);
    }

    await new Promise(resolve => setTimeout(resolve, 15000));


    // go to job url
    await page.goto(
        job_url
    );



    await new Promise(resolve => setTimeout(resolve, 1000));
    // <button aria-label="Visual challenge. Audio challenge is available below, compatible with screen reader software." class="sc-nkuzb1-0 sc-d5trka-0 eZxMRy button" data-theme="home.verifyButton">Start Puzzle</button>

    //get all pages
    let pages = await browser.pages();

    let jobPage = null;
    let externalJobPage = null;
    if (pages.length ==1) {
        console.log('No new tab opened');
    }
    else {
        for (let iter_page of pages) {
            const urlObject = new URL(iter_page.url());
            const domainName = urlObject.hostname; 
            console.log(domainName);

            console.log(jobUrlObject.pathname);
            console.log(urlObject.pathname);
            if (urlObject.pathname.includes(jobUrlObject.pathname)) {
                jobPage = iter_page;
                console.log('Job page found, passing...');
            }
            if (domainName != 'www.linkedin.com') {
                console.log('apply directs to');
                console.log(domainName);
                console.log(urlObject.pathname);
                let externalJobPage = iter_page;
            }
        }
    }
    // if (jobPage) {
    //     await apply_to_linkedin(jobPage);
    // }
    // if (externalJobPage) {
    //     await identifyExternalApply(externalJobPage);
    // }
    // await new Promise(resolve => setTimeout(resolve, 15000));

    
    const stats = await getClickStatistics(page);
    console.log('\n📈 Final click statistics:', stats);

    // Stop tracking
    await stopButtonClickTracker(page);
    
    console.log('✅ Test completed! Check the console output and log file for details.');
    
    // await browser.close();
    
    // await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    // await click_apply_button(page);
}

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
        

async function apply_to_linkedin(page) {
    await new Promise(resolve => setTimeout(resolve, 15000));
    // await click_apply_button(page);
    // await easy_apply(page);
}

async function identifyExternalApply(page) {
    await new Promise(resolve => setTimeout(resolve, 15000));
    // check if the page is a job page
    // check if an automation is available for the site 
        // linked in
        // workday
        // greenhous
   // if so, run the automation  
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
