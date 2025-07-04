import { DuckDBInstance } from '@duckdb/node-api';

// import puppeteer from "puppeteer";
import puppeteer from "puppeteer-extra";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker} from './buttonTracker.js';
import { email, password, requestHeaders, captcha_token} from './information.js';
import { solve_captcha } from './resolve_captcha.js';
import { selectorExists, initializePage, closePage } from './utils.js';


// default vals for testing
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


async function getUrls(num_jobs=5) {
    // Getting jobs to run from duckdb
    const instance = await DuckDBInstance.create('linkedin.duckdb');
    const conn = await instance.connect();
    const jobs = await conn.runAndReadAll('select * from linkedin_data.job_urls');
    console.log(typeof jobs);
    const rows = jobs.getRows();

    const test = rows.slice(0, num_jobs)
    const job_url = 'https://www.linkedin.com/jobs/view/4253333502' // for testing
    test = [job_url]
    return test
}

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
}

async function apply(job_url) {
    console.log(job_url);
    console.log('hello');
    let page_and_browser = await initializePage();
    let page = page_and_browser[0];
    let browser = page_and_browser[1];
    console.log(typeof page)

    console.log('signing in');
    await signIn(page);

    console.log('waiting for start puzzle');
    await new Promise(resolve => setTimeout(resolve, 5000));
    console.log('clicking start puzzle');

    const urls = await getUrls();
    for (let url of urls) {
        await apply(url);
    }
    // page.on('request', request => {
    //     console.log(request.url());
    //     console.log(request.headers());
    //   });

    await new Promise(resolve => setTimeout(resolve, 15000));


    // go to job url
    await page.goto(
        job_url
    );


    let jobPage, externalJobPage = await identifyExternalApply(browser);
    
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // if (jobPage) {
    //     await apply_to_linkedin(jobPage);
    // }
    // if (externalJobPage) {
    //     await identifyExternalApply(externalJobPage);
    // }
    // await new Promise(resolve => setTimeout(resolve, 15000));

    closePage(page, browser);
    
    // await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    // await click_apply_button(page);
}

async function apply_to_linkedin(page) {
    await new Promise(resolve => setTimeout(resolve, 15000));
    // await click_apply_button(page);
    // await easy_apply(page);
}

async function identifyExternalApply(browser) {
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
    return jobPage, externalJobPage
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
