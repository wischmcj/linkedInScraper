import { DuckDBInstance } from '@duckdb/node-api';

import puppeteer from "puppeteer";

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
// "https://leidos.wd5.myworkdayjobs.com/en-US/External/job/Geospatial-Data-Scientist_R-00160099?bid=56&tid=x_de4204c6-7a43-47bd-a8e0-fd5e04bf08bb&source=APPLICANT_SOURCE-3-10317"


// function doSetTimeout(var_in) {
//     setTimeout(() => {
//         debugger;
//         console.log(var_in);
//     }, 1000);
//   }

// const test= [job_url]
// for (var i = 1; i <= num_jobs; ++i)
//     console.log(test[i], i);
//     await apply(test[i]);
//     doSetTimeout(i);
apply(test[0][0]);


async function selectorExists(page, selector) {
    try {
        await page.waitForSelector(selector, { timeout: 1000 });
    } catch (error) {
        return false;
    }
    return true;
}
 
async function apply(job_url) {
    console.log(job_url);
    console.log('hello');
    var page = await getPage();
    console.log(typeof page)
    page.on('request', request => {
        console.log(request.url());
        console.log(request.headers());
      });
    await page.goto(
        job_url
    );

    const all_buttons = await page.locator('::-p-xpath(//button)');
    
    
    console.log(all_buttons);
    await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    // const allButtons = await page.locator('button');
    // console.log(allButtons);
    // debugger; 

    // let willClick = false;
    // await page
    // .locator('button')
    // .on(LocatorEvent.Action, () => {
    //     willClick = true;
    // })
    // .click();
    
    // const allButtons = document.querySelectorAll('button'); 
    // allButtons.forEach(button => {
    //     button.addEventListener('click', function() {
    //         console.log(`Button with text "${button.textContent}" clicked!`);
    //     });
    // });
    await selectorExists(page, 'div[data-automation-id="errorMessage"]')
    // await click_apply_button(page);
}

async function getPage() {
    console.log("Getting page");

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: false,
    });
    const page = await browser.newPage();
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
