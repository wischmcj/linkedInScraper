import { DuckDBInstance } from '@duckdb/node-api';

// import puppeteer from "puppeteer";
import puppeteer from "puppeteer-extra";
import { setupButtonClickTracker, getClickStatistics, stopButtonClickTracker} from './buttonTracker.js';
import { email, password,} from './information.js';
import { selectorExists, initializePage, closePage } from './utils.js';
import { get_pk_and_surl, solve_captcha, getTokenFrame } from './resolve_captcha.js';

// default vals for testing
const login_url = 'https://www.linkedin.com/login'

// let page_and_browser = await initializePage();
// let page = page_and_browser[0];
// let browser = page_and_browser[1];
// console.log('signing in');
// await signIn(page);


// const urls = await getUrls(5, true);
// const urls = await getUrls(5,0, false);
// for (let url of urls) {
//     // await apply(url);
//     console.log(url);
// }


// await processJobs();


async function getUrls(num_jobs=5, start_index=0, debug=False) {
    // Getting jobs to run from duckdb
    const instance = await DuckDBInstance.create('linkedin.duckdb');
    const conn = await instance.connect();
    const jobs = await conn.runAndReadAll(`select * 
                                            from linkedin_data.job_urls 
                                            where company_name not in ('Jobot','TRM Labs', 'Braintrust')`);
    console.log(typeof jobs);
    const rows = jobs.getRows();

    console.log(rows.length,' Jobs Found');
    var jobUrls = rows.slice(start_index, start_index + num_jobs)
    if (debug) {
        //easy apply url
        const job_url= "https://www.linkedin.com/jobs/view/4257497407"
        // non-standard domain apply url
        // const job_url = 'https://www.linkedin.com/jobs/view/4253333502' // for testing
        jobUrls = [job_url]
    }
    return jobUrls
}

async function signIn(page) {
    await page.goto(
        login_url
    );
    // await page.locator('button[data-automation-id="signInLink"]').click();

    await page.waitForSelector('input[id="username"]', { timeout: 5000 });

    await page.locator('input[id="username"]').fill(email);

    await page.locator('input[id="password"]').fill(password);

    await page.locator('button[data-litms-control-urn="login-submit"]').click({ delay: 400 });

    //give the page time to load
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    if (await page.url().includes('checkpoint')) {
        console.log('detected captcha challenge. Resolving...')
        solve_captcha(page);
        //await solve_captcha(page);
    }
    else {
        console.log('no captcha challenge detected')
    }
}

async function processJobs() {
    let page_and_browser = await initializePage();
    let page = page_and_browser[0];
    let browser = page_and_browser[1];
    console.log(typeof page)

    console.log('signing in');
    await signIn(page);

    console.log('waiting for start puzzle');
    await new Promise(resolve => setTimeout(resolve, 5000));

    const urls = await getUrls(5,0, true);
    for (let url of urls) {
        await apply(page, url);
    }
    // page.on('request', request => {
    //     console.log(request.url());
    //     console.log(request.headers());
    //   });

    await new Promise(resolve => setTimeout(resolve, 15000));    
    closePage(page, browser);
    
    // await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    // await click_apply_button(page);
}

async function apply(page, job_url) {
    // go to job url
    await page.goto(
        job_url
    );
    await new Promise(resolve => setTimeout(resolve, 5000));


    //*********The below are not tested yet  **********//
    //Check if span with text "Application submitted" exists
    // if so, already applied
    const application_submitted = 'div[data-view-name="job-post-apply-timeline"]';
    if (await selectorExists(page, application_submitted)) {
        console.log('Application already submitted');
        return;
    }
    //if span with class class="artdeco-inline-feedback__message" and text No longer accepting applications, skip
    const no_longer_accepting_applications = 'span[class="artdeco-inline-feedback__message"]';
    if (await selectorExists(page, no_longer_accepting_applications)) {
        console.log('No longer accepting applications');
        return;
    }
    //************************//

    try {
        await click_apply_button(page);
    }
    catch (error) {
        console.log('No apply button found');
    }
    const apply_button = 'button[class="jobs-apply-button"]';
    var applyBtn = await page.$(apply_button)
    console.log(applyBtn);
    await applyBtn.click();
    
    // await new Promise(resolve => setTimeout(resolve, 20000)); 

    let isInternal, jobPage = await identifyNewTabDomain(newPage.url(), browser);
    if (isInternal) {
        await apply_to_linkedin(jobPage);
    }
    else {
        await identifyExternalApply(jobPage);
    }
    // await new Promise(resolve => setTimeout(resolve, 15000));

}

async function click_apply_button(page) {
    const apply_button = 'button[class="jobs-apply-button"]';
    if (await selectorExists(page, apply_button)) {
        // check if easy apply button (aria-label contains "Easy Apply")
        if (await page.locator(apply_button)) {
            console.log("Easy Apply button found. Clicking");
            await page.locator(apply_button).click();
        }
        else {
            console.log("Apply button found. Clicking");
            await page.locator(apply_button).click();
        }
    }
}

async function identifyNewTabDomain(url, browser) {
    // Determine if apply link is internal or external (to linkedIn)
    // This is done instead of checking link as obsfucated urls are often used (e.g. tinyurls)

    const jobUrlObject = new URL(url);  

    let pages = await browser.pages();

    let jobPage = null;
    let externalJobPage = null;
    if (pages.length ==1) {
        // If no new tab is opened, apply target is likely internal
        console.log('No new tab opened');
        isInternal = true 
    }
    else {
        let i = 0
        // Iterate over tabs to find the apply target
        for (let iter_page of pages) {
            i += 1
            const urlObject = new URL(iter_page.url());
            const domainName = urlObject.hostname; 

            console.log('tab ',i,' url path name', urlObject.pathname);
            console.log('tab ',i,' url domain/host name', domainName);
            console.log('tab ',i,' url as json', urlObject.toJSON );   
            if (urlObject.pathname.includes(jobUrlObject.pathname)) {
                console.log(urlObject.pathname);
                jobPage = iter_page;
                isInternal = false                
            }
            if (domainName == 'www.linkedin.com') {
                jobPage = iter_page;
                isInternal = true
                console.log('Job page found, passing...');
            }
                console.log('apply directs to');
                console.log(domainName);
        }
    }
    return isInternal, jobPage
    // check if the page is a job page
    // check if an automation is available for the site 
        // linked in
        // workday
        // greenhous
   // if so, run the automation  
}


async function easy_apply(page, selector) {    
    // all elements under div w class "jobs-easy-apply-modal"
    // named jobs-easy-apply-modal

    // inputs are nested in divs w class XXgWYIwGXSpKlhJjFKnNbLOKYXvNcyJALl (which is in div with class jobs-easy-apply-modal__content)
    // look for elements following a label with text e.g. first name, last name, email, phone, etc.

    // selects w options nested after labels w text 
    //selects ids from first page 
    //  text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255214328-21448336428-multipleChoice //for email address
    // text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338204-phoneNumber-country
    // single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338204-phoneNumber-nationalNumber
    // text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4255579489-21451338180-multipleChoice

    // next: button w  name data-easy-apply-next-button

    // if h3 with text Resume, should have already auto selected. hit next again 
    // same w Mark this job as a top choice 

    // if div w class "job-details-easy-apply-top-choice__content" then hit next
    // same with div w class "jobs-document-upload-redesign-card__container" //resume

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

export { signIn };